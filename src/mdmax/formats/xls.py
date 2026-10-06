"""Legacy Excel (.xls, BIFF). Needs the small pure-Python package xlrd."""

from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

from . import Converted
from .sheets import format_number, render_sheets


def convert_xls(path: Path, table_format: str = "auto", include_hidden: bool = False) -> Converted:
    try:
        import xlrd
    except ImportError as exc:
        from ..convert import MissingDependency

        raise MissingDependency("xlrd", ".xls files need xlrd: pip install xlrd") from exc

    book = xlrd.open_workbook(str(path), on_demand=True)
    sheets: List[Tuple[str, List[List[str]]]] = []
    hidden = []
    try:
        for index in range(book.nsheets):
            sheet = book.sheet_by_index(index)
            if getattr(sheet, "visibility", 0) and not include_hidden:
                hidden.append(sheet.name)
                continue
            rows = []
            for r in range(sheet.nrows):
                row = []
                for c in range(sheet.ncols):
                    cell = sheet.cell(r, c)
                    if cell.ctype == xlrd.XL_CELL_DATE:
                        try:
                            moment = xlrd.xldate.xldate_as_datetime(cell.value, book.datemode)
                            value = moment.strftime("%Y-%m-%d %H:%M" if moment.hour or moment.minute else "%Y-%m-%d")
                        except Exception:
                            value = format_number(cell.value)
                    elif cell.ctype == xlrd.XL_CELL_NUMBER:
                        value = format_number(cell.value)
                    elif cell.ctype == xlrd.XL_CELL_BOOLEAN:
                        value = "TRUE" if cell.value else "FALSE"
                    elif cell.ctype == xlrd.XL_CELL_ERROR:
                        value = xlrd.error_text_from_code.get(cell.value, "#ERROR")
                    else:
                        value = str(cell.value)
                    row.append(value)
                rows.append(row)
            sheets.append((sheet.name, rows))
    finally:
        book.release_resources()
    warnings = []
    if hidden:
        warnings.append(f"{len(hidden)} hidden sheet(s) skipped: {', '.join(hidden)} (use --include-hidden)")
    text, baseline = render_sheets(sheets, table_format)
    return Converted(text=text, baseline_text=baseline, baseline_kind="markdown-table", warnings=warnings)
