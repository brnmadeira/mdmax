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
                # Garantir UTF-8 para headers
                safe_headers = [str(h or "").encode('utf-8', errors='replace').decode('utf-8') for h in headers]
                markdown_lines.append("| " + " | ".join(safe_headers) + " |")
                markdown_lines.append("| " + " | ".join("---" for _ in headers) + " |")

                for row in rows[1:]:
                    if any(row):  # Skip empty rows
                        # Garantir UTF-8 para cada célula
                        safe_row = [str(c or "").encode('utf-8', errors='replace').decode('utf-8') for c in row]
                        markdown_lines.append("| " + " | ".join(safe_row) + " |")

            markdown_lines.append("\n")

        return "\n".join(markdown_lines)

    def csv_to_markdown(self, file_path: str) -> str:
        """Convert CSV to Markdown table"""
        markdown_lines = []

        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                rows = list(reader)
        except UnicodeDecodeError:
            # Fallback para latin-1 se UTF-8 falhar
            with open(file_path, 'r', encoding='latin-1') as f:
                reader = csv.reader(f)
                rows = list(reader)

        if rows:
            # Headers
            headers = rows[0]
            # Garantir UTF-8 para headers
            safe_headers = [str(h or "").encode('utf-8', errors='replace').decode('utf-8') for h in headers]
            markdown_lines.append("| " + " | ".join(safe_headers) + " |")
            markdown_lines.append("| " + " | ".join("---" for _ in headers) + " |")

            # Data rows
            for row in rows[1:]:
                if len(row) != len(headers):
                    row = row + [""] * (len(headers) - len(row))
                # Garantir UTF-8 para cada célula
                safe_row = [str(c or "").encode('utf-8', errors='replace').decode('utf-8') for c in row]
                markdown_lines.append("| " + " | ".join(safe_row) + " |")

        return "\n".join(markdown_lines)

    def json_to_markdown(self, file_path: str) -> str:
        """Convert JSON to Markdown (formatted JSON block)"""
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)

        markdown = f"""# JSON Data

```json
{json.dumps(data, indent=2, ensure_ascii=False)}
```
"""
        return markdown

    def txt_to_markdown(self, file_path: str) -> str:
        """Convert TXT to Markdown (passthrough)"""
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                return f.read()
        except UnicodeDecodeError:
            # Fallback para latin-1 se UTF-8 falhar
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()

    def xls_to_markdown(self, file_path: str) -> str:
        """Convert old XLS format to Markdown with fallback"""
        try:
            import xlrd
            workbook = xlrd.open_workbook(file_path)

            markdown_lines = []
            for sheet_name in workbook.sheet_names():
                sheet = workbook.sheet_by_name(sheet_name)
                markdown_lines.append(f"## Sheet: {sheet_name}\n")

                if sheet.nrows > 0:
                    # Headers
                    headers = sheet.row_values(0)
                    # Garantir UTF-8 para headers
                    safe_headers = [str(h).encode('utf-8', errors='replace').decode('utf-8') for h in headers]
                    markdown_lines.append("| " + " | ".join(safe_headers) + " |")
                    markdown_lines.append("| " + " | ".join("---" for _ in headers) + " |")

                    # Data rows
                    for row_idx in range(1, sheet.nrows):
                        row = sheet.row_values(row_idx)
                        # Garantir UTF-8 para cada célula
                        safe_row = [str(c).encode('utf-8', errors='replace').decode('utf-8') for c in row]
                        markdown_lines.append("| " + " | ".join(safe_row) + " |")

                markdown_lines.append("\n")

            return "\n".join(markdown_lines)

        except ImportError:
            raise ImportError("xlrd not installed. Run: pip install xlrd")
        except Exception as e:
            # Fallback: Try to read as XLSX (some .xls files are actually XLSX)
            try:
                from openpyxl import load_workbook
                return self.xlsx_to_markdown(file_path)
            except Exception:
                # Last resort: Return file info instead of crashing
                return f"""# XLS File: {Path(file_path).name}

## File Information
- **File**: {Path(file_path).name}
- **Size**: {Path(file_path).stat().st_size} bytes
- **Format**: Excel Spreadsheet (.xls)

## Note
The file could not be automatically converted. Please convert it to .xlsx format using:
- Microsoft Excel: File > Export As > Excel Workbook
- LibreOffice Calc: File > Save As > Microsoft Excel 2007-365 (.xlsx)
- Online tools: https://cloudconvert.com

Original error: {str(e)}
"""

    def svg_to_markdown(self, file_path: str) -> str:
        """Convert SVG to Markdown (embedded)"""
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                svg_content = f.read()
        except UnicodeDecodeError:
            # Fallback para latin-1 se UTF-8 falhar
            with open(file_path, 'r', encoding='latin-1') as f:
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

            with Image.open(file_path) as img:
                text = pytesseract.image_to_string(img)

                if text.strip():
                    markdown += "## Extracted Text\n\n"
                    markdown += text
        except ImportError:
            markdown += "*(Install pytesseract + Tesseract for OCR support)*\n"
        except Exception as e:
            # OCR failed, but conversion can proceed without it
            markdown += f"*(OCR failed: {type(e).__name__})*\n"

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

        # ebooklib item type constants: 0=NCX, 1=CSS, 2=Image, 3=XHTML, 4=Other
        EPUB_ITEM_TYPE_XHTML = 3

        for item in book.get_items():
            if item.get_type() == EPUB_ITEM_TYPE_XHTML:
                try:
                    content = item.get_content().decode('utf-8', errors='replace')
                except (UnicodeDecodeError, AttributeError) as e:
                    # Fallback para latin-1
                    try:
                        content = item.get_content().decode('latin-1', errors='replace')
                    except Exception as fallback_err:
                        # Skip this item if both decodings fail
                        continue
                # Simple strip HTML tags
                text = re.sub(r'<[^>]+>', '', content)
                # Garantir UTF-8
                safe_text = text.encode('utf-8', errors='replace').decode('utf-8')
                if safe_text.strip():
                    markdown_lines.append(safe_text)

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
                # Garantir UTF-8
                safe_text = para.text.encode('utf-8', errors='replace').decode('utf-8')
                markdown_lines.append(safe_text)

        # Add tables
        for table in doc.tables:
            rows = []
            for row in table.rows:
                row_data = [cell.text.encode('utf-8', errors='replace').decode('utf-8') for cell in row.cells]
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
                    # Garantir UTF-8
                    safe_text = shape.text.encode('utf-8', errors='replace').decode('utf-8')
                    markdown_lines.append(safe_text)

            markdown_lines.append("")

        return "\n".join(markdown_lines)
