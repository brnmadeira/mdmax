"""Shared spreadsheet logic: number and date formatting, sheet rendering."""

from __future__ import annotations

import datetime as dt
import re
from typing import List, Sequence, Tuple

from ..tables import markdown_baseline, render_table

_EPOCH_1900 = dt.datetime(1899, 12, 30)
_EPOCH_1904 = dt.datetime(1904, 1, 1)

# Built-in Excel number formats that show dates or times.
BUILTIN_DATE_FORMATS = set(range(14, 23)) | set(range(27, 37)) | {45, 46, 47} | set(range(50, 59))
BUILTIN_PERCENT_FORMATS = {9, 10}

_QUOTED = re.compile(r'"[^"]*"|\\.|\[[^\]]*\]')


def is_date_format(code: str) -> bool:
    if not code or code.lower() == "general":
        return False
    stripped = _QUOTED.sub("", code)
    return bool(re.search(r"[dmyhsDMYHS]", stripped)) and not re.fullmatch(r"[#0.,\s%]*", stripped)


def is_percent_format(code: str) -> bool:
    return "%" in _QUOTED.sub("", code or "")


def format_number(value: float) -> str:
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if float(value).is_integer() and abs(value) < 1e15:
        return str(int(value))
    return f"{float(value):.15g}"


def format_percent(value: float) -> str:
    return format_number(round(float(value) * 100, 10)) + "%"


def serial_to_text(serial: float, date1904: bool = False) -> str:
    """Excel serial date -> ISO text ("2026-10-01", "2026-10-01 14:30" or "14:30")."""
    try:
        base = _EPOCH_1904 if date1904 else _EPOCH_1900
        moment = base + dt.timedelta(days=float(serial))
    except (OverflowError, ValueError):
        return format_number(serial)
    has_time = abs(float(serial) - int(float(serial))) > 1e-9
    if float(serial) < 1 and has_time:
        return moment.strftime("%H:%M:%S" if moment.second else "%H:%M")
    if has_time:
        return moment.strftime("%Y-%m-%d %H:%M:%S" if moment.second else "%Y-%m-%d %H:%M")
    return moment.strftime("%Y-%m-%d")


def render_sheets(
    sheets: Sequence[Tuple[str, List[List[str]]]], table_format: str
) -> Tuple[str, str]:
    """Render [(name, rows)] -> (text, markdown_baseline_text)."""
    parts, base_parts = [], []
    for name, rows in sheets:
        rendered = render_table(rows, table_format)
        if not rendered:
            continue
        header = f"## Sheet: {name}" if len(sheets) > 1 or name else ""
        parts.append((header + "\n" if header else "") + rendered)
        base_parts.append((header + "\n" if header else "") + markdown_baseline(rows))
    return "\n\n".join(parts), "\n\n".join(base_parts)
