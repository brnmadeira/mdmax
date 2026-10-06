"""PDF text extraction with pypdf (or pdfplumber / markitdown when that is what is installed).

When Claude reads a PDF directly, it receives the text of each page *and* an image of
each page. For text documents the image is most of the cost; sending only the text
is where mdmax saves tokens. Scanned PDFs have no text layer, so for those mdmax
steps aside and lets Claude read the pages as images.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

from ..tokens import PDF_IMAGE_TOKENS_PER_PAGE, estimate_tokens
from . import Converted

_MIN_CHARS_PER_PAGE = 25
_PAGE_NUMBER = re.compile(
    r"^[-–—\s]*(?:page|p[aá]gina|p[aá]g\.?|p\.)?\s*\d{1,4}(?:\s*(?:of|de|/)\s*\d{1,4})?[-–—\s]*$",
    re.IGNORECASE,
)
_WIDE_GAP = re.compile(r"[ \t]{3,}")


def parse_pages(spec: Optional[str], total: int) -> List[int]:
    """'1-5,8' -> [0, 1, 2, 3, 4, 7] (0-based). None or '' means every page."""
    if not spec:
        return list(range(total))
    out: List[int] = []
    for part in str(spec).replace(" ", "").split(","):
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            start = int(a) if a else 1
            end = int(b) if b else total
        else:
            start = end = int(part)
        if start < 1 or end < start:
            raise ValueError(f"invalid page range: {part}")
        out.extend(i - 1 for i in range(start, min(end, total) + 1))
    return sorted(set(out))


def _extract(path: Path, pages: Optional[str]) -> Tuple[List[Tuple[int, str]], int]:
    try:
        from pypdf import PdfReader
    except ImportError:
        PdfReader = None
    if PdfReader is not None:
        reader = PdfReader(str(path))
        if reader.is_encrypted:
            try:
                ok = reader.decrypt("")
            except Exception:
                ok = 0
            if not ok:
                from ..convert import NotConvertible

                raise NotConvertible("the PDF is password protected")
        total = len(reader.pages)
        indices = parse_pages(pages, total)
        return [(i + 1, reader.pages[i].extract_text() or "") for i in indices], total
    try:
        import pdfplumber
    except ImportError:
        pdfplumber = None
    if pdfplumber is not None:
        with pdfplumber.open(str(path)) as pdf:
            total = len(pdf.pages)
            indices = parse_pages(pages, total)
            return [(i + 1, pdf.pages[i].extract_text() or "") for i in indices], total
    from ..convert import MissingDependency

    raise MissingDependency("pypdf", "PDF needs pypdf: pip install pypdf")


def _strip_repeated_edges(pages: List[List[str]]) -> int:
    """Remove running headers/footers and page numbers. Returns lines removed.

    Only the first and last two lines of a page are candidates, and a line counts as a
    running header only when the *same* text repeats on most pages. Numbers are not
    normalized (except in the page-number pattern), so content lines such as
    "Week 3: sales" on every page are never mistaken for headers.
    """
    edge = 2
    counts: Counter = Counter()
    keyed = []
    for lines in pages:
        keys = {}
        positions = list(range(min(edge, len(lines)))) + list(range(max(0, len(lines) - edge), len(lines)))
        for pos in set(positions):
            key = " ".join(lines[pos].lower().split())
            if key:
                keys[pos] = key
        keyed.append(keys)
        counts.update(set(keys.values()))
    with_text = sum(1 for lines in pages if lines)
    threshold = max(3, math.ceil(0.6 * with_text))
    repeated = {k for k, c in counts.items() if c >= threshold}
    removed = 0
    for lines, keys in zip(pages, keyed):
        drop = {pos for pos, key in keys.items() if key in repeated or _PAGE_NUMBER.match(lines[pos].strip())}
        if drop:
            lines[:] = [line for i, line in enumerate(lines) if i not in drop]
            removed += len(drop)
    return removed


def convert_pdf(path: Path, pages: Optional[str] = None, min_chars_per_page: int = _MIN_CHARS_PER_PAGE) -> Converted:
    extracted, total = _extract(path, pages)
    raw = "\n".join(text for _, text in extracted)
    page_lines: List[List[str]] = []
    for _, text in extracted:
        lines = [_WIDE_GAP.sub("  ", line.rstrip()) for line in text.replace("\r", "\n").split("\n")]
        page_lines.append([line for line in lines if line.strip()])
    chars = sum(len(t.strip()) for _, t in extracted)
    if extracted and chars / len(extracted) < min_chars_per_page:
        from ..convert import NotConvertible

        if chars / len(extracted) < _MIN_CHARS_PER_PAGE:
            raise NotConvertible(
                "the PDF has (almost) no text layer - probably scanned images; let Claude read it directly"
            )
        raise NotConvertible(
            f"the PDF is mostly visual (about {chars // len(extracted)} characters of text per page): "
            "the page images carry the content, so it is left for Claude to read directly"
        )
    removed = _strip_repeated_edges(page_lines) if len(page_lines) >= 3 else 0
    blocks = []
    empty_pages = []
    single = len(extracted) == 1
    for (number, _), lines in zip(extracted, page_lines):
        body = "\n".join(lines).strip()
        if not body:
            empty_pages.append(number)
            body = f"[no text on this page - probably an image; read page {number} of the original PDF to see it]"
        blocks.append(body if single else f"## Page {number}\n{body}")
    warnings = []
    if empty_pages:
        warnings.append(f"page(s) without text (images?): {', '.join(map(str, empty_pages))}")
    if removed:
        warnings.append(f"{removed} repeated header/footer/page-number line(s) removed")
    if pages and len(extracted) < total:
        warnings.append(f"pages {pages} of {total}")
    baseline = estimate_tokens(raw) + PDF_IMAGE_TOKENS_PER_PAGE * len(extracted)
    return Converted(
        text="\n\n".join(blocks),
        baseline_tokens=baseline,
        baseline_kind="pdf-direct-estimate",
        pages=len(extracted),
        warnings=warnings,
    )


def page_count(path: Path) -> Optional[int]:
    try:
        from pypdf import PdfReader

        return len(PdfReader(str(path)).pages)
    except Exception:
        return None


def has_pdf_backend() -> bool:
    for name in ("pypdf", "pdfplumber"):
        try:
            __import__(name)
            return True
        except ImportError:
            continue
    return False


__all__: Sequence[str] = ("convert_pdf", "parse_pages", "page_count", "has_pdf_backend")
