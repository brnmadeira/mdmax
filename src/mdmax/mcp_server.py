"""MCP server over stdio, written with the standard library only.

Tools:
* ``convert_document`` - convert a local file and return the compact text, in pages
  of ``max_chars`` so a large document never exceeds the client's tool-output limit.
* ``token_savings`` - the savings log (``mdmax stats``).

Run: ``mdmax-mcp`` (installed) or ``python -m mdmax.mcp_server``.
"""

from __future__ import annotations

import json
import sys
import traceback
from pathlib import Path
from typing import Any, Dict, Optional

from . import __version__, storage
from .convert import SUPPORTED_EXTENSIONS, MissingDependency, NotConvertible, convert

PROTOCOL_VERSIONS = ("2025-06-18", "2025-03-26", "2024-11-05")
DEFAULT_MAX_CHARS = 20000  # about 9,000 tokens: below the 10,000-token warning of Claude Code

TOOLS = [
    {
        "name": "convert_document",
        "description": (
            "Convert a local document into compact Markdown/CSV text that costs far fewer tokens "
            "than the original, and report the savings. Use it before reading PDF, Word (.docx), "
            "Excel (.xlsx/.xlsm/.xls), PowerPoint (.pptx), OpenDocument (.ods/.odt/.odp), EPUB, "
            "CSV/TSV, JSON/JSONL, HTML or TXT files. Long results come in parts: call again with "
            "the returned next_offset. Images and charts are not included."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Absolute path of the file"},
                "pages": {"type": "string", "description": "PDF only: pages to convert, e.g. '1-5,8'"},
                "table_format": {
                    "type": "string",
                    "enum": ["auto", "csv", "markdown"],
                    "description": "auto (default) picks the shorter rendering for each table",
                },
                "offset": {"type": "integer", "minimum": 0, "description": "Character offset for the next part"},
                "max_chars": {"type": "integer", "minimum": 1000, "maximum": 100000},
            },
            "required": ["path"],
            "additionalProperties": False,
        },
    },
    {
        "name": "token_savings",
        "description": "Show how many tokens mdmax has saved so far, per format.",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
]

INSTRUCTIONS = (
    "mdmax turns documents into compact text. Before reading a PDF, Office, OpenDocument, "
    "EPUB, CSV, JSON or HTML file from disk, call convert_document with its path. "
    "Supported extensions: " + " ".join(SUPPORTED_EXTENSIONS)
)


def _text(content: str, is_error: bool = False) -> Dict[str, Any]:
    return {"content": [{"type": "text", "text": content}], "isError": is_error}


def _convert_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    path = Path(str(args.get("path", ""))).expanduser()
    pages = args.get("pages") or None
    table_format = args.get("table_format") or "auto"
    offset = max(0, int(args.get("offset") or 0))
    max_chars = min(100000, max(1000, int(args.get("max_chars") or DEFAULT_MAX_CHARS)))
    try:
        key = storage.cache_key(path, pages=pages or "", tables=table_format) if path.is_file() else None
        info = storage.cached(key) if key else None
        if info is None:
            result = convert(path, table_format=table_format, pages=pages)
            folder = storage.cache_dir()
            folder.mkdir(parents=True, exist_ok=True)
            md_path = folder / f"{key}-{storage.output_name(path, pages)}"
            md_path.write_text(result.text, encoding="utf-8")
            info = storage.store(key, md_path, result)
            storage.record(result, "mcp")
        text = Path(info["md_path"]).read_text(encoding="utf-8")
    except (MissingDependency, NotConvertible, FileNotFoundError, ValueError) as exc:
        return _text(f"mdmax could not convert {path.name}: {exc}", is_error=True)

    chunk = text[offset:offset + max_chars]
    end = offset + len(chunk)
    approx = "~" if info.get("method") != "exact" else ""
    header = [f"[mdmax] {path.name}: {approx}{info['tokens']:,} tokens"]
    if info.get("baseline") is not None:
        saved = info["baseline"] - info["tokens"]
        if saved > 0:
            header.append(f"saves {approx}{saved:,} ({100 * saved / info['baseline']:.0f}%)")
    if info.get("warnings"):
        header.append("notes: " + "; ".join(info["warnings"]))
    header.append(f"full text: {info['md_path']}")
    if end < len(text):
        header.append(f"part {offset:,}-{end:,} of {len(text):,} characters; next_offset={end}")
    return _text(" | ".join(header) + "\n\n" + chunk)


def _savings_tool() -> Dict[str, Any]:
    data = storage.summary()
    t = data["totals"]
    if not t["files"]:
        return _text("No conversions recorded yet.")
    lines = [f"Files converted: {t['files']}"]
    if t["compared"]:
        pct = 100.0 * t["saved"] / t["baseline"] if t["baseline"] else 0.0
        lines.append(f"Tokens: {t['tokens']:,} instead of {t['baseline']:,}; saved {t['saved']:,} ({pct:.0f}%)")
    for fmt, f in sorted(data["by_format"].items(), key=lambda kv: -kv[1]["saved"]):
        lines.append(f"- {fmt}: {f['files']} file(s), {f['tokens']:,} tokens, saved {f['saved']:,}")
    return _text("\n".join(lines))


def handle(message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    method = message.get("method")
    msg_id = message.get("id")
    if msg_id is None:  # notification
        return None
    params = message.get("params") or {}
    try:
        if method == "initialize":
            requested = params.get("protocolVersion")
            version = requested if requested in PROTOCOL_VERSIONS else PROTOCOL_VERSIONS[0]
            result = {
                "protocolVersion": version,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "mdmax", "version": __version__},
                "instructions": INSTRUCTIONS,
            }
        elif method == "ping":
            result = {}
        elif method == "tools/list":
            result = {"tools": TOOLS}
        elif method == "tools/call":
            name = params.get("name")
            args = params.get("arguments") or {}
            if name == "convert_document":
                result = _convert_tool(args)
            elif name == "token_savings":
                result = _savings_tool()
            else:
                return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32602, "message": f"unknown tool: {name}"}}
        elif method in ("resources/list", "prompts/list"):
            result = {method.split("/")[0]: []}
        else:
            return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": f"method not found: {method}"}}
    except Exception as exc:
        traceback.print_exc(file=sys.stderr)
        return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32603, "message": str(exc)}}
    return {"jsonrpc": "2.0", "id": msg_id, "result": result}


def main() -> int:
    stdin = sys.stdin.buffer
    stdout = sys.stdout.buffer
    for raw in stdin:
        line = raw.decode("utf-8", errors="replace").strip()
        if not line:
            continue
        try:
            message = json.loads(line)
        except ValueError:
            reply = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "parse error"}}
        else:
            reply = handle(message) if isinstance(message, dict) else None
        if reply is not None:
            stdout.write((json.dumps(reply, ensure_ascii=False) + "\n").encode("utf-8"))
            stdout.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
