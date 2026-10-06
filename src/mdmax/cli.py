"""Command line: ``mdmax convert``, ``mdmax stats``, ``mdmax doctor``, ``mdmax formats``."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import List, Optional

from . import __version__, storage
from .convert import (
    BASELINE_LABELS,
    BINARY_EXTENSIONS,
    SUPPORTED_EXTENSIONS,
    MissingDependency,
    NotConvertible,
    convert,
)


def _safe_streams() -> None:
    # Pipes on Windows default to cp1252: write UTF-8 (what Claude Code and other tools
    # read) and never crash on a character the console cannot show.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def _out_path(src: Path, output: Optional[str], many: bool) -> Path:
    if output:
        target = Path(output).expanduser()
        if many or target.is_dir():
            return target / (src.stem + ".md")
        return target
    target = src.with_suffix(".md")
    if target.resolve() == src.resolve():
        target = src.with_name(src.stem + ".mdmax.md")
    return target


def cmd_convert(args) -> int:
    files: List[Path] = [Path(f).expanduser() for f in args.files]
    many = len(files) > 1
    failures = 0
    results = []
    for src in files:
        try:
            result = convert(
                src,
                table_format=args.tables,
                pages=args.pages,
                include_hidden=args.include_hidden,
                exact=True if args.exact else None,
            )
        except MissingDependency as exc:
            print(f"ERROR {src.name}: {exc}", file=sys.stderr)
            failures += 1
            continue
        except (NotConvertible, FileNotFoundError, ValueError) as exc:
            print(f"SKIP  {src.name}: {exc}", file=sys.stderr)
            failures += 1
            continue
        except Exception as exc:  # a damaged file must not stop a batch
            print(f"ERROR {src.name}: {type(exc).__name__}: {exc}", file=sys.stderr)
            failures += 1
            continue
        storage.record(result, "cli")
        if args.stdout:
            sys.stdout.write(result.text)
            target = None
        else:
            target = _out_path(src, args.output, many)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(result.text, encoding="utf-8")
        results.append((result, target))
        if args.json:
            continue
        if not args.quiet:
            where = f" -> {target}" if target else ""
            print(f"OK    {src.name}{where}", file=sys.stderr)
            print(f"      {result.summary()}", file=sys.stderr)
            for warning in result.warnings:
                print(f"      note: {warning}", file=sys.stderr)
    if args.json:
        payload = [
            {
                "file": str(r.path),
                "output": str(t) if t else None,
                "tokens": r.tokens,
                "baseline_tokens": r.baseline_tokens,
                "baseline": BASELINE_LABELS.get(r.baseline_kind, r.baseline_kind),
                "saved": r.saved,
                "saved_pct": round(r.saved_pct, 1) if r.saved_pct is not None else None,
                "method": r.method,
                "pages": r.pages,
                "warnings": r.warnings,
            }
            for r, t in results
        ]
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 1 if failures and not results else 0


def cmd_stats(args) -> int:
    if args.reset:
        storage.reset()
        print("Savings log cleared.")
        return 0
    data = storage.summary()
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0
    t = data["totals"]
    if not t["files"]:
        print("No conversions recorded yet. Try: mdmax convert <file>")
        return 0
    print(f"mdmax {__version__} - savings since {data['first'][:10]}")
    print(f"Files converted: {t['files']} ({t['exact']} counted exactly, the rest estimated)")
    if t["compared"]:
        pct = 100.0 * t["saved"] / t["baseline"] if t["baseline"] else 0.0
        print(f"Tokens: {t['tokens']:,} sent instead of {t['baseline']:,} -> {t['saved']:,} saved ({pct:.0f}%)")
        print(f"  (over the {t['compared']} file(s) that have a comparison point)")
    print()
    print(f"{'format':<8}{'files':>7}{'tokens':>12}{'without mdmax':>16}{'saved':>12}")
    for fmt, f in sorted(data["by_format"].items(), key=lambda kv: -kv[1]["saved"]):
        base = f"{f['baseline']:,}" if f["baseline"] else "-"
        saved = f"{f['saved']:,}" if f["baseline"] else "-"
        print(f"{fmt:<8}{f['files']:>7}{f['tokens']:>12,}{base:>16}{saved:>12}")
    print()
    print(f"Log: {storage.home() / 'savings.jsonl'} (names and numbers only, no content)")
    return 0


def cmd_formats(args) -> int:
    print("Supported: " + " ".join(SUPPORTED_EXTENSIONS))
    print("Converted automatically by the Claude Code plugin when Claude reads them: " + " ".join(BINARY_EXTENSIONS))
    return 0


def cmd_doctor(args) -> int:
    from .formats.pdf import has_pdf_backend

    print(f"mdmax {__version__} on Python {sys.version.split()[0]} ({sys.executable})")
    print(f"PDF support: {'yes' if has_pdf_backend() else 'no - pip install pypdf'}")
    try:
        import xlrd  # noqa: F401

        print("Legacy .xls support: yes")
    except ImportError:
        print("Legacy .xls support: no - pip install xlrd")
    try:
        import anthropic  # noqa: F401

        has_sdk = True
    except ImportError:
        has_sdk = False
    has_key = bool(os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN"))
    if has_sdk and has_key:
        print("Exact token counting: available (use --exact or MDMAX_EXACT_TOKENS=1)")
    else:
        missing = [] if has_sdk else ['pip install "mdmax[exact]"']
        if not has_key:
            missing.append("an ANTHROPIC_API_KEY")
        print("Exact token counting: off - needs " + " and ".join(missing) + "; estimates are used instead")
    print(f"Data folder: {storage.home()}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mdmax",
        description="Convert documents into compact text for Claude and measure the tokens saved.",
    )
    parser.add_argument("--version", action="version", version=f"mdmax {__version__}")
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("convert", help="convert one or more files")
    p.add_argument("files", nargs="+", help="files to convert")
    p.add_argument("-o", "--output", help="output file (or folder, for several inputs)")
    p.add_argument("--stdout", action="store_true", help="print the result instead of writing a file")
    p.add_argument("--tables", choices=["auto", "csv", "markdown"], default="auto",
                   help="table format; auto picks the shorter one (default)")
    p.add_argument("--pages", help="PDF pages, e.g. 1-5,8")
    p.add_argument("--include-hidden", action="store_true", help="include hidden spreadsheet tabs")
    p.add_argument("--exact", action="store_true",
                   help="count tokens with the Anthropic API (needs mdmax[exact] and an API key)")
    p.add_argument("--json", action="store_true", help="print the numbers as JSON")
    p.add_argument("-q", "--quiet", action="store_true", help="no summary")
    p.set_defaults(func=cmd_convert)

    s = sub.add_parser("stats", help="tokens saved so far")
    s.add_argument("--json", action="store_true")
    s.add_argument("--reset", action="store_true", help="clear the savings log")
    s.set_defaults(func=cmd_stats)

    f = sub.add_parser("formats", help="list supported formats")
    f.set_defaults(func=cmd_formats)

    d = sub.add_parser("doctor", help="check what is installed")
    d.set_defaults(func=cmd_doctor)
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    _safe_streams()
    argv = list(sys.argv[1:] if argv is None else argv)
    commands = {"convert", "stats", "formats", "doctor", "-h", "--help", "--version"}
    if argv and argv[0] not in commands:
        argv.insert(0, "convert")  # `mdmax file.pdf` works as `mdmax convert file.pdf`
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "func", None):
        parser.print_help()
        return 0
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
