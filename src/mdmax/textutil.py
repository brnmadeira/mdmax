"""Text helpers: whitespace clean-up, encoding detection and HTML to Markdown."""

from __future__ import annotations

import re
from html.parser import HTMLParser
from typing import List, Optional

from .tables import render_table

_TRAILING_SPACE = re.compile(r"[ \t]+\n")
_MANY_NEWLINES = re.compile(r"\n{3,}")
_INLINE_SPACE = re.compile(r"[ \t\r\n\f\v ]+")


def normalize_text(text: str) -> str:
    """Unify line endings, drop trailing spaces and runs of blank lines."""
    text = text.replace("﻿", "").replace("\r\n", "\n").replace("\r", "\n")
    text = _TRAILING_SPACE.sub("\n", text)
    text = _MANY_NEWLINES.sub("\n\n", text)
    return text.strip() + "\n" if text.strip() else ""


def decode_bytes(data: bytes) -> str:
    """UTF-8 (with or without BOM), then UTF-16 by BOM, then Windows-1252."""
    if data.startswith(b"\xef\xbb\xbf"):
        return data[3:].decode("utf-8", errors="replace")
    if data.startswith((b"\xff\xfe", b"\xfe\xff")):
        return data.decode("utf-16", errors="replace")
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("cp1252", errors="replace")


_SKIP = {"script", "style", "noscript", "template", "svg", "head", "iframe", "canvas", "object", "math"}
_BLOCK = {
    "p", "div", "section", "article", "header", "footer", "main", "aside", "nav", "blockquote",
    "figure", "figcaption", "dl", "dt", "dd", "address", "details", "summary", "form", "fieldset",
    "center", "body", "html",
}
_HEADINGS = {"h1": 1, "h2": 2, "h3": 3, "h4": 4, "h5": 5, "h6": 6}


class _HtmlToMarkdown(HTMLParser):
    def __init__(self, table_format: str = "auto"):
        super().__init__(convert_charrefs=True)
        self.table_format = table_format
        self.blocks: List[str] = []
        self.inline: List[str] = []
        self.skip_depth = 0
        self.pre_depth = 0
        self.lists: List[List] = []  # [kind, counter]
        self.li_pending = False
        self.heading: Optional[int] = None
        self.link_href: Optional[str] = None
        self.link_text_start = 0
        self.table_stack: List[dict] = []
        self.title: Optional[str] = None
        self._in_title = False

    # -- helpers -----------------------------------------------------------
    def _flush(self, heading_prefix: str = "") -> None:
        text = "".join(self.inline)
        self.inline = []
        if self.pre_depth:
            if text.strip("\n"):
                self.blocks.append(text)
            return
        text = _INLINE_SPACE.sub(" ", text).strip()
        if not text:
            return
        prefix = heading_prefix
        if not prefix and self.lists:
            prefix = self._li_prefix(continuation=not self.li_pending)
            self.li_pending = False
        self.blocks.append(prefix + text)

    def _cell_target(self):
        return self.table_stack[-1] if self.table_stack else None

    # -- parser callbacks --------------------------------------------------
    def handle_starttag(self, tag, attrs):
        if tag == "title":
            self._in_title = True
        if self.skip_depth or tag in _SKIP:
            if tag in _SKIP:
                self.skip_depth += 1
            return
        attrs = dict(attrs)
        table = self._cell_target()
        if tag == "table":
            self._flush()
            self.table_stack.append({"rows": [], "row": None, "cell": None})
            return
        if table is not None:
            if tag == "tr":
                table["row"] = []
            elif tag in ("td", "th"):
                table["cell"] = []
                self.inline = table["cell"]
            elif tag == "br":
                self.inline.append(" ")
            return
        if tag in _HEADINGS:
            self._flush()
            self.heading = _HEADINGS[tag]
        elif tag in ("ul", "ol"):
            self._flush()
            self.lists.append([tag, 0])
        elif tag == "li":
            self._flush()
            if self.lists:
                self.lists[-1][1] += 1
            self.li_pending = True
        elif tag == "pre":
            self._flush()
            self.pre_depth += 1
        elif tag == "br":
            if self.pre_depth:
                self.inline.append("\n")
            else:
                self._flush()
        elif tag == "hr":
            self._flush()
            self.blocks.append("---")
        elif tag in _BLOCK:
            self._flush()
        elif tag == "a":
            href = (attrs.get("href") or "").strip()
            if href.startswith(("http://", "https://", "mailto:")):
                self.link_href = href
                self.link_text_start = len(self.inline)
        elif tag == "img":
            alt = (attrs.get("alt") or "").strip()
            if alt:
                self.inline.append(f"[imagem: {alt}]")

    def _li_prefix(self, continuation: bool = False) -> str:
        if not self.lists:
            return ""
        indent = "  " * (len(self.lists) - 1)
        if continuation:
            return indent + "  "
        kind, counter = self.lists[-1]
        return indent + (f"{counter}. " if kind == "ol" else "- ")

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        if tag in _SKIP and self.skip_depth:
            self.skip_depth -= 1
            return
        if self.skip_depth:
            return
        table = self._cell_target()
        if table is not None:
            if tag in ("td", "th") and table["cell"] is not None:
                text = _INLINE_SPACE.sub(" ", "".join(table["cell"])).strip()
                if table["row"] is None:
                    table["row"] = []
                table["row"].append(text)
                table["cell"] = None
                self.inline = []
            elif tag == "tr" and table["row"] is not None:
                table["rows"].append(table["row"])
                table["row"] = None
            elif tag == "table":
                self.table_stack.pop()
                if table["row"]:
                    table["rows"].append(table["row"])
                rendered = render_table(table["rows"], self.table_format)
                if self.table_stack:  # nested table: keep its text inside the outer cell
                    self.inline = self.table_stack[-1]["cell"] or []
                    self.inline.append(" " + rendered.replace("\n", " ") + " ")
                elif rendered:
                    self.blocks.append(rendered)
            return
        if tag in _HEADINGS:
            self._flush("#" * (self.heading or 1) + " ")
            self.heading = None
        elif tag == "li":
            self._flush()
            self.li_pending = False
        elif tag in ("ul", "ol"):
            self._flush()
            if self.lists:
                self.lists.pop()
        elif tag == "pre":
            text = "".join(self.inline).strip("\n")
            self.inline = []
            self.pre_depth = max(0, self.pre_depth - 1)
            if text.strip():
                self.blocks.append("```\n" + text + "\n```")
        elif tag == "a" and self.link_href:
            text = "".join(self.inline[self.link_text_start:]).strip()
            href = self.link_href
            self.link_href = None
            if text and text != href and not href.endswith(text):
                del self.inline[self.link_text_start:]
                self.inline.append(f"[{text}]({href})")
        elif tag in _BLOCK:
            self._flush()

    def handle_data(self, data):
        if self._in_title:
            self.title = (self.title or "") + data
        if self.skip_depth:
            return
        self.inline.append(data)

    def result(self) -> str:
        self._flush()
        return "\n\n".join(b for b in self.blocks if b.strip())


def html_to_markdown(html: str, table_format: str = "auto") -> str:
    parser = _HtmlToMarkdown(table_format)
    parser.feed(html)
    parser.close()
    return parser.result()


def html_title(html: str) -> Optional[str]:
    parser = _HtmlToMarkdown()
    parser.feed(html)
    title = (parser.title or "").strip()
    return _INLINE_SPACE.sub(" ", title) or None
