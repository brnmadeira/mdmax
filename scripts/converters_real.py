#!/usr/bin/env python3
"""
Real file converters for MdMax
Supports: PDF, Excel, CSV, JSON, TXT
"""

import json
import csv
import re
from pathlib import Path
from typing import Optional


class MarkdownConverter:
    """Convert various file formats to Markdown"""

    def __init__(self):
        pass

    def pdf_to_markdown(self, file_path: str) -> str:
        """Convert PDF to Markdown"""
        try:
            import PyPDF2
        except ImportError:
            raise ImportError("PyPDF2 not installed. Run: pip install PyPDF2")

        markdown_lines = []

        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)

            for page_num, page in enumerate(reader.pages, 1):
                text = page.extract_text()
                if text:
                    markdown_lines.append(f"## Page {page_num}\n")
                    markdown_lines.append(text)
                    markdown_lines.append("\n")

        return "\n".join(markdown_lines)

    def xlsx_to_markdown(self, file_path: str) -> str:
        """Convert Excel to Markdown tables"""
        try:
            from openpyxl import load_workbook
        except ImportError:
            raise ImportError("openpyxl not installed. Run: pip install openpyxl")

        markdown_lines = []
        workbook = load_workbook(file_path)

        for sheet_name in workbook.sheetnames:
            sheet = workbook[sheet_name]
            markdown_lines.append(f"## Sheet: {sheet_name}\n")

            # Extract data
            rows = []
            for row in sheet.iter_rows(values_only=True):
                rows.append(row)

            if rows:
                # Create markdown table
                headers = rows[0]
                markdown_lines.append("| " + " | ".join(str(h or "") for h in headers) + " |")
                markdown_lines.append("| " + " | ".join("---" for _ in headers) + " |")

                for row in rows[1:]:
                    if any(row):  # Skip empty rows
                        markdown_lines.append("| " + " | ".join(str(c or "") for c in row) + " |")

            markdown_lines.append("\n")

        return "\n".join(markdown_lines)

    def csv_to_markdown(self, file_path: str) -> str:
        """Convert CSV to Markdown table"""
        markdown_lines = []

        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            rows = list(reader)

            if rows:
                # Headers
                headers = rows[0]
                markdown_lines.append("| " + " | ".join(headers) + " |")
                markdown_lines.append("| " + " | ".join("---" for _ in headers) + " |")

                # Data rows
                for row in rows[1:]:
                    if len(row) != len(headers):
                        row = row + [""] * (len(headers) - len(row))
                    markdown_lines.append("| " + " | ".join(row) + " |")

        return "\n".join(markdown_lines)

    def json_to_markdown(self, file_path: str) -> str:
        """Convert JSON to Markdown (formatted JSON block)"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        markdown = f"""# JSON Data

```json
{json.dumps(data, indent=2)}
```
"""
        return markdown

    def txt_to_markdown(self, file_path: str) -> str:
        """Convert TXT to Markdown (passthrough)"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def xls_to_markdown(self, file_path: str) -> str:
        """Convert old XLS format to Markdown"""
        try:
            import xlrd
        except ImportError:
            raise ImportError("xlrd not installed. Run: pip install xlrd")

        markdown_lines = []
        workbook = xlrd.open_workbook(file_path)

        for sheet_name in workbook.sheet_names():
            sheet = workbook.sheet_by_name(sheet_name)
            markdown_lines.append(f"## Sheet: {sheet_name}\n")

            if sheet.nrows > 0:
                # Headers
                headers = sheet.row_values(0)
                markdown_lines.append("| " + " | ".join(str(h) for h in headers) + " |")
                markdown_lines.append("| " + " | ".join("---" for _ in headers) + " |")

                # Data rows
                for row_idx in range(1, sheet.nrows):
                    row = sheet.row_values(row_idx)
                    markdown_lines.append("| " + " | ".join(str(c) for c in row) + " |")

            markdown_lines.append("\n")

        return "\n".join(markdown_lines)

    def svg_to_markdown(self, file_path: str) -> str:
        """Convert SVG to Markdown (embedded)"""
        with open(file_path, 'r', encoding='utf-8') as f:
            svg_content = f.read()

        markdown = f"""# SVG Image

```svg
{svg_content}
```
"""
        return markdown

    def jpg_to_markdown(self, file_path: str) -> str:
        """Convert JPG/PNG to Markdown (with optional OCR)"""
        file_name = Path(file_path).name

        markdown = f"""# Image: {file_name}

![{file_name}]({file_path})

"""

        # Try OCR if available
        try:
            import pytesseract
            from PIL import Image

            img = Image.open(file_path)
            text = pytesseract.image_to_string(img)

            if text.strip():
                markdown += "## Extracted Text\n\n"
                markdown += text
        except ImportError:
            markdown += "*(Install pytesseract + Tesseract for OCR support)*\n"
        except Exception:
            pass

        return markdown

    png_to_markdown = jpg_to_markdown

    def epub_to_markdown(self, file_path: str) -> str:
        """Convert EPUB to Markdown"""
        try:
            from ebooklib import epub
        except ImportError:
            raise ImportError("ebooklib not installed. Run: pip install ebooklib")

        markdown_lines = []
        book = epub.read_epub(file_path)

        for item in book.get_items():
            if item.get_type() == 3:  # XHTML document
                content = item.get_content().decode('utf-8')
                # Simple strip HTML tags
                text = re.sub(r'<[^>]+>', '', content)
                if text.strip():
                    markdown_lines.append(text)

        return "\n\n".join(markdown_lines)

    def docx_to_markdown(self, file_path: str) -> str:
        """Convert DOCX to Markdown"""
        try:
            from docx import Document
        except ImportError:
            raise ImportError("python-docx not installed. Run: pip install python-docx")

        markdown_lines = []
        doc = Document(file_path)

        for para in doc.paragraphs:
            if para.text.strip():
                markdown_lines.append(para.text)

        # Add tables
        for table in doc.tables:
            rows = []
            for row in table.rows:
                row_data = [cell.text for cell in row.cells]
                rows.append(row_data)

            if rows:
                headers = rows[0]
                markdown_lines.append("| " + " | ".join(headers) + " |")
                markdown_lines.append("| " + " | ".join("---" for _ in headers) + " |")

                for row in rows[1:]:
                    markdown_lines.append("| " + " | ".join(row) + " |")

        return "\n".join(markdown_lines)

    def pptx_to_markdown(self, file_path: str) -> str:
        """Convert PPTX to Markdown"""
        try:
            from pptx import Presentation
        except ImportError:
            raise ImportError("python-pptx not installed. Run: pip install python-pptx")

        markdown_lines = []
        prs = Presentation(file_path)

        for slide_num, slide in enumerate(prs.slides, 1):
            markdown_lines.append(f"## Slide {slide_num}\n")

            for shape in slide.shapes:
                if hasattr(shape, "text") and shape.text.strip():
                    markdown_lines.append(shape.text)

            markdown_lines.append("")

        return "\n".join(markdown_lines)
