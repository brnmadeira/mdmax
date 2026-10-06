"""Rendering tables with as few tokens as possible, without dropping data.

A Markdown pipe table spends a separator, padding and two pipes per cell; CSV spends
one delimiter. For the same rows CSV is almost always smaller, so ``auto`` picks
whichever rendering is shorter (and therefore cheaper) for each table.
"""

from __future__ import annotations

import csv
import io
import re
from typing import Iterable, List, Sequence, Tuple

Row = List[str]

_NEWLINES = re.compile(r"\s*[\r\n]+\s*")


def clean_cell(value) -> str:
    if value is None:
        return ""
    text = value if isinstance(value, str) else str(value)
    text = text.replace(" ", " ").strip()
    if "\n" in text or "\r" in text:
        text = _NEWLINES.sub(" / ", text)
    return text


def trim_table(rows: Iterable[Sequence]) -> List[Row]:
    """Clean cells, drop empty rows and the empty columns at the right edge."""
    table = [[clean_cell(c) for c in row] for row in rows]
    table = [row for row in table if any(row)]
    if not table:
        return []
    width = 0
    for row in table:
        for i in range(len(row) - 1, -1, -1):
            if row[i]:
                width = max(width, i + 1)
                break
    return [(row + [""] * (width - len(row)))[:width] for row in table]


def _csv_text(rows: List[Row], delimiter: str) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf, delimiter=delimiter, lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
    writer.writerows(rows)
    return buf.getvalue().rstrip("\n")


def to_csv(rows: List[Row]) -> Tuple[str, str]:
    """CSV with the delimiter that needs the fewest quotes. Returns (text, name)."""
    best = None
    for delimiter, name in ((",", "csv"), (";", "csv"), ("\t", "tsv")):
        text = _csv_text(rows, delimiter)
        if best is None or len(text) < len(best[0]):
            best = (text, name)
    return best


def to_markdown(rows: List[Row], padded_separator: bool = False) -> str:
    def line(cells: Sequence[str]) -> str:
        return "| " + " | ".join(c.replace("|", "\\|") for c in cells) + " |"

    if padded_separator:
        separator = "| " + " | ".join("---" for _ in rows[0]) + " |"
    else:
        separator = "|" + "|".join("---" for _ in rows[0]) + "|"
    out = [line(rows[0]), separator]
    out.extend(line(r) for r in rows[1:])
    return "\n".join(out)


def render_table(rows: Iterable[Sequence], fmt: str = "auto") -> str:
    """Render rows (first row = header) as a fenced CSV block or a Markdown table."""
    table = trim_table(rows)
    if not table:
        return ""
    md = to_markdown(table)
    if fmt == "markdown":
        return md
    csv_text, lang = to_csv(table)
    fenced = f"```{lang}\n{csv_text}\n```"
    if fmt == "csv":
        return fenced
    return fenced if len(fenced) < len(md) else md


def markdown_baseline(rows: Iterable[Sequence]) -> str:
    """The plain Markdown table most converters produce; used as a comparison point."""
    table = trim_table(rows)
    return to_markdown(table, padded_separator=True) if table else ""
