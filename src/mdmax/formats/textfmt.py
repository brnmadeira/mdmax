"""Text formats: CSV/TSV, JSON/JSONL, HTML, TXT/Markdown.

Claude can already read these, so the comparison point is the raw file. Savings come
from removing what carries no information: indentation in JSON, repeated keys in
lists of records, padding and empty columns in CSV, markup in HTML.
"""

from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from typing import Any, List, Optional

from ..tables import render_table
from ..textutil import decode_bytes, html_title, html_to_markdown, normalize_text
from . import Converted

_TABULAR_MIN_ROWS = 2


def _read_text(path: Path) -> str:
    return decode_bytes(Path(path).read_bytes())


def convert_csv(path: Path, table_format: str = "auto", delimiter: Optional[str] = None) -> Converted:
    raw = _read_text(path)
    sample = raw[:20000]
    if delimiter is None:
        try:
            delimiter = csv.Sniffer().sniff(sample, delimiters=",;\t|").delimiter
        except csv.Error:
            delimiter = "\t" if Path(path).suffix.lower() == ".tsv" else ","
    rows = list(csv.reader(io.StringIO(raw), delimiter=delimiter))
    text = render_table(rows, table_format)
    return Converted(text=text, baseline_text=raw, baseline_kind="raw-file")


def _scalar(value: Any) -> bool:
    return value is None or isinstance(value, (str, int, float, bool))


def _cell(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float) and value.is_integer():
        return str(int(value)) if abs(value) < 1e15 else repr(value)
    return str(value)


def _as_table(items: Any) -> Optional[List[List[str]]]:
    """A list of flat objects becomes rows (header = union of keys, in order)."""
    if not isinstance(items, list) or len(items) < _TABULAR_MIN_ROWS:
        return None
    if not all(isinstance(i, dict) and i and all(_scalar(v) for v in i.values()) for i in items):
        return None
    keys: List[str] = []
    seen = set()
    for item in items:
        for k in item:
            if k not in seen:
                seen.add(k)
                keys.append(k)
    rows = [keys]
    for item in items:
        rows.append([_cell(item.get(k)) for k in keys])
    return rows


def _compact(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _json_body(data: Any, table_format: str) -> str:
    table = _as_table(data)
    if table:
        return render_table(table, table_format)
    if isinstance(data, dict):
        parts, rest = [], {}
        for key, value in data.items():
            table = _as_table(value)
            if table:
                parts.append(f"## {key}\n" + render_table(table, table_format))
            else:
                rest[key] = value
        if parts:
            if rest:
                parts.insert(0, "```json\n" + _compact(rest) + "\n```")
            return "\n\n".join(parts)
    return "```json\n" + _compact(data) + "\n```"


def convert_json(path: Path, table_format: str = "auto") -> Converted:
    raw = _read_text(path)
    data = json.loads(raw)
    return Converted(text=_json_body(data, table_format), baseline_text=raw, baseline_kind="raw-file")


def convert_jsonl(path: Path, table_format: str = "auto") -> Converted:
    raw = _read_text(path)
    items = [json.loads(line) for line in raw.splitlines() if line.strip()]
    table = _as_table(items)
    body = render_table(table, table_format) if table else "\n".join(_compact(i) for i in items)
    return Converted(text=body, baseline_text=raw, baseline_kind="raw-file")


def convert_html(path: Path, table_format: str = "auto") -> Converted:
    raw = _read_text(path)
    body = html_to_markdown(raw, table_format)
    title = html_title(raw)
    if title and not body.lstrip().startswith("#"):
        body = f"Title: {title}\n\n{body}"
    return Converted(text=body, baseline_text=raw, baseline_kind="raw-file")


def convert_plain(path: Path, table_format: str = "auto") -> Converted:
    raw = _read_text(path)
    return Converted(text=normalize_text(raw).rstrip("\n"), baseline_text=raw, baseline_kind="raw-file")
