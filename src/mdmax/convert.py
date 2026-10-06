"""Entry point: pick the converter for a file and measure the result."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional

from .tokens import (
    count_pdf_tokens_exact,
    count_tokens_exact,
    estimate_tokens,
    exact_enabled,
)


class MissingDependency(RuntimeError):
    """A format needs an optional package that is not installed."""

    def __init__(self, package: str, message: str):
        super().__init__(message)
        self.package = package


class NotConvertible(RuntimeError):
    """The file cannot be turned into useful text (scanned PDF, encrypted, empty...)."""


def _pdf(path, opts):
    from .formats.pdf import convert_pdf

    if opts.get("min_pdf_chars"):
        return convert_pdf(path, pages=opts["pages"], min_chars_per_page=opts["min_pdf_chars"])
    return convert_pdf(path, pages=opts["pages"])


def _xlsx(path, opts):
    from .formats.ooxml import convert_xlsx

    return convert_xlsx(path, opts["table_format"], opts["include_hidden"])


def _docx(path, opts):
    from .formats.ooxml import convert_docx

    return convert_docx(path, opts["table_format"])


def _pptx(path, opts):
    from .formats.ooxml import convert_pptx

    return convert_pptx(path, opts["table_format"])


def _xls(path, opts):
    from .formats.xls import convert_xls

    return convert_xls(path, opts["table_format"], opts["include_hidden"])


def _ods(path, opts):
    from .formats.odf import convert_ods

    return convert_ods(path, opts["table_format"], opts["include_hidden"])


def _odt(path, opts):
    from .formats.odf import convert_odt

    return convert_odt(path, opts["table_format"])


def _odp(path, opts):
    from .formats.odf import convert_odp

    return convert_odp(path, opts["table_format"])


def _epub(path, opts):
    from .formats.epub import convert_epub

    return convert_epub(path, opts["table_format"])


def _csv(path, opts):
    from .formats.textfmt import convert_csv

    return convert_csv(path, opts["table_format"])


def _json(path, opts):
    from .formats.textfmt import convert_json

    return convert_json(path, opts["table_format"])


def _jsonl(path, opts):
    from .formats.textfmt import convert_jsonl

    return convert_jsonl(path, opts["table_format"])


def _html(path, opts):
    from .formats.textfmt import convert_html

    return convert_html(path, opts["table_format"])


def _plain(path, opts):
    from .formats.textfmt import convert_plain

    return convert_plain(path, opts["table_format"])


CONVERTERS: Dict[str, Callable] = {
    ".pdf": _pdf,
    ".docx": _docx,
    ".pptx": _pptx,
    ".xlsx": _xlsx,
    ".xlsm": _xlsx,
    ".xls": _xls,
    ".ods": _ods,
    ".odt": _odt,
    ".odp": _odp,
    ".epub": _epub,
    ".csv": _csv,
    ".tsv": _csv,
    ".json": _json,
    ".jsonl": _jsonl,
    ".ndjson": _jsonl,
    ".html": _html,
    ".htm": _html,
    ".txt": _plain,
    ".md": _plain,
}

SUPPORTED_EXTENSIONS = tuple(CONVERTERS)

# Binary formats Claude cannot read well on its own; the Claude Code hook converts only these.
# Text formats are left alone so that Claude can still edit them.
BINARY_EXTENSIONS = (".pdf", ".docx", ".pptx", ".xlsx", ".xlsm", ".xls", ".ods", ".odt", ".odp", ".epub")

BASELINE_LABELS = {
    "pdf-direct-estimate": "reading the PDF directly (text + page images, estimated)",
    "pdf-direct": "reading the PDF directly (text + page images)",
    "raw-file": "the original file",
    "markdown-table": "a plain Markdown table",
    "none": "",
}


@dataclass
class ConversionResult:
    path: Path
    fmt: str
    text: str
    tokens: int
    baseline_tokens: Optional[int]
    baseline_kind: str
    method: str  # "estimated" or "exact"
    pages: Optional[int] = None
    warnings: List[str] = field(default_factory=list)
    seconds: float = 0.0

    @property
    def saved(self) -> Optional[int]:
        if self.baseline_tokens is None:
            return None
        return self.baseline_tokens - self.tokens

    @property
    def saved_pct(self) -> Optional[float]:
        if not self.baseline_tokens:
            return None
        return 100.0 * self.saved / self.baseline_tokens

    def summary(self) -> str:
        approx = "~" if self.method == "estimated" else ""
        parts = [f"{approx}{self.tokens:,} tokens"]
        if self.pages:
            parts.insert(0, f"{self.pages} page(s)" if self.fmt == "pdf" else f"{self.pages} slide(s)")
        if self.baseline_tokens is not None:
            label = BASELINE_LABELS.get(self.baseline_kind, self.baseline_kind)
            if self.saved >= 0:
                parts.append(
                    f"saves {approx}{self.saved:,} ({self.saved_pct:.0f}%) vs {label} "
                    f"({approx}{self.baseline_tokens:,})"
                )
            else:
                parts.append(f"{-self.saved:,} more than {label}: the original is already compact")
        parts.append(f"[{self.method}]")
        return " | ".join(parts)


def convert(
    path,
    *,
    table_format: str = "auto",
    pages: Optional[str] = None,
    include_hidden: bool = False,
    exact: Optional[bool] = None,
    min_pdf_chars: Optional[int] = None,
) -> ConversionResult:
    """Convert a file. ``min_pdf_chars``: PDFs with less text per page than this are
    refused (NotConvertible) - the Claude Code hook uses it to leave posters, flyers and
    slide decks with little text to Claude's own PDF reading, which sees the images."""
    path = Path(path).expanduser()
    ext = path.suffix.lower()
    converter = CONVERTERS.get(ext)
    if converter is None:
        raise NotConvertible(f"unsupported format: {ext or path.name} (supported: {', '.join(SUPPORTED_EXTENSIONS)})")
    if not path.is_file():
        raise FileNotFoundError(f"file not found: {path}")
    if pages and ext != ".pdf":
        raise ValueError("pages only applies to PDF files")
    if table_format not in ("auto", "csv", "markdown"):
        raise ValueError("table_format must be auto, csv or markdown")

    started = time.perf_counter()
    opts = {"table_format": table_format, "pages": pages, "include_hidden": include_hidden,
            "min_pdf_chars": min_pdf_chars}
    converted = converter(path, opts)
    body = (converted.text or "").strip()
    if not body:
        raise NotConvertible("no text found in the file")
    text = f"# {path.name}\n\n{body}\n"

    warnings = list(converted.warnings)
    tokens = estimate_tokens(text)
    baseline = converted.baseline_tokens
    if baseline is None and converted.baseline_text is not None:
        baseline = estimate_tokens(converted.baseline_text)
    kind = converted.baseline_kind if baseline is not None else "none"
    method = "estimated"

    if exact_enabled(exact):
        try:
            tokens = count_tokens_exact(text)
            if ext == ".pdf" and not pages:
                baseline = count_pdf_tokens_exact(path)
                kind = "pdf-direct"
            elif converted.baseline_text is not None:
                baseline = count_tokens_exact(converted.baseline_text)
            method = "exact"
        except Exception as exc:  # network, credentials, missing SDK
            warnings.append(f"exact count unavailable ({exc}); using the estimate")

    return ConversionResult(
        path=path,
        fmt=ext.lstrip("."),
        text=text,
        tokens=tokens,
        baseline_tokens=baseline,
        baseline_kind=kind,
        method=method,
        pages=converted.pages,
        warnings=warnings,
        seconds=time.perf_counter() - started,
    )
