#!/usr/bin/env python3
"""
MdMax Smart Table Extractor - Automatic table detection and extraction from PDFs
Feature [1] of v2.2: Extract tables from PDFs as structured markdown
"""

import re
from typing import List, Optional, Tuple
from pathlib import Path


class TableExtractor:
    """Extract tables from various document formats"""

    def extract_from_pdf(self, pdf_path: str) -> List[str]:
        """Extract tables from PDF"""
        try:
            import pdfplumber
        except ImportError:
            # Fallback: try camelot or similar
            return self._extract_fallback(pdf_path)

        tables = []

        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_tables = page.extract_tables()

                    if page_tables:
                        for table in page_tables:
                            markdown_table = self._convert_table_to_markdown(table)
                            tables.append(markdown_table)
        except Exception as e:
            print(f"Warning: Could not extract tables: {e}")

        return tables

    def extract_from_text(self, content: str) -> List[str]:
        """Detect and extract ASCII tables from text"""
        tables = []

        # Pattern for ASCII tables (lines with | separators)
        lines = content.split('\n')
        current_table = []
        in_table = False

        for line in lines:
            # Detect table lines (contain | characters)
            if '|' in line and (line.strip().startswith('|') or '---' in line):
                if not in_table:
                    in_table = True
                current_table.append(line)
            elif in_table:
                # End of table
                if current_table:
                    tables.append('\n'.join(current_table))
                current_table = []
                in_table = False

        if current_table:
            tables.append('\n'.join(current_table))

        return tables

    def detect_table_regions(self, text: str) -> List[Tuple[int, int, str]]:
        """Detect potential table regions in text"""
        regions = []

        lines = text.split('\n')

        for i, line in enumerate(lines):
            # Look for header lines (uppercase, few words)
            if self._is_table_header(line):
                # Found potential table
                start = i
                end = i + 1

                # Find table bounds
                while end < len(lines) and self._is_table_content(lines[end]):
                    end += 1

                table_text = '\n'.join(lines[start:end])
                regions.append((start, end, table_text))

        return regions

    def _is_table_header(self, line: str) -> bool:
        """Check if line looks like table header"""
        # Headers have multiple columns (spaces/tabs/|)
        cols = len(re.split(r'\s{2,}|\t|\|', line.strip()))
        return cols >= 2 and len(line.strip()) > 10

    def _is_table_content(self, line: str) -> bool:
        """Check if line looks like table content"""
        return len(line.strip()) > 0 and (
            '|' in line or
            len(re.split(r'\s{2,}|\t', line.strip())) >= 2
        )

    def _convert_table_to_markdown(self, table_data: List[List]) -> str:
        """Convert extracted table to markdown format"""
        if not table_data:
            return ""

        markdown = ""

        # Header
        if table_data:
            header = table_data[0]
            markdown += "| " + " | ".join(str(cell or "") for cell in header) + " |\n"
            markdown += "| " + " | ".join("---" for _ in header) + " |\n"

        # Data rows
        for row in table_data[1:]:
            markdown += "| " + " | ".join(str(cell or "") for cell in row) + " |\n"

        return markdown

    def enhance_markdown_tables(self, markdown: str) -> str:
        """Enhance markdown with detected tables"""
        enhanced = markdown

        # Find and improve ASCII tables
        ascii_tables = self.extract_from_text(markdown)

        for table in ascii_tables:
            # Try to convert to proper markdown
            improved = self._improve_ascii_table(table)
            enhanced = enhanced.replace(table, improved)

        return enhanced

    def _improve_ascii_table(self, table_str: str) -> str:
        """Improve ASCII table formatting"""
        lines = table_str.split('\n')

        if not lines:
            return table_str

        # Try to parse columns
        if '|' in lines[0]:
            # Already pipe-separated
            return table_str

        # Parse space-separated columns
        parsed_rows = []

        for line in lines:
            if line.strip():
                # Split on multiple spaces
                cols = re.split(r'\s{2,}', line.strip())
                parsed_rows.append(cols)

        if not parsed_rows:
            return table_str

        # Convert to markdown
        markdown = ""

        if parsed_rows:
            # Header
            header = parsed_rows[0]
            markdown += "| " + " | ".join(header) + " |\n"
            markdown += "| " + " | ".join("---" for _ in header) + " |\n"

            # Data
            for row in parsed_rows[1:]:
                if len(row) < len(header):
                    row.extend([""] * (len(header) - len(row)))
                markdown += "| " + " | ".join(row[:len(header)]) + " |\n"

        return markdown

    def extract_and_annotate(self, content: str, source_format: str = "text") -> str:
        """Extract tables and annotate them in the content"""
        if source_format == "pdf":
            # Would use PDF extraction
            return content

        # For text, detect and enhance
        enhanced = self.enhance_markdown_tables(content)

        # Add table-of-contents comment if tables found
        if "| " in enhanced and "|" not in content:
            # Tables were added/enhanced
            annotation = "\n> **Note**: Tables have been automatically detected and formatted.\n\n"
            enhanced = annotation + enhanced

        return enhanced


class PDFTableExtractor:
    """Specialized extractor for PDF tables using OCR if needed"""

    def __init__(self):
        self.extractor = TableExtractor()

    def extract_with_fallback(self, pdf_path: str) -> List[str]:
        """Extract tables with OCR fallback"""
        tables = self.extractor.extract_from_pdf(pdf_path)

        if not tables:
            # Try OCR-based extraction
            tables = self._extract_with_ocr(pdf_path)

        return tables

    def _extract_with_ocr(self, pdf_path: str) -> List[str]:
        """Extract tables using OCR (for scanned PDFs)"""
        try:
            import pytesseract
            from PIL import Image
            import pdf2image

            tables = []

            # Convert PDF pages to images
            images = pdf2image.convert_from_path(pdf_path)

            for img in images:
                # Apply OCR
                text = pytesseract.image_to_string(img)

                # Extract tables from OCR text
                page_tables = TableExtractor().extract_from_text(text)
                tables.extend(page_tables)

            return tables

        except Exception as e:
            print(f"Warning: OCR extraction failed: {e}")
            return []


if __name__ == '__main__':
    import sys

    extractor = TableExtractor()

    if len(sys.argv) > 1:
        file_path = sys.argv[1]

        if file_path.endswith('.pdf'):
            tables = extractor.extract_from_pdf(file_path)
        else:
            content = Path(file_path).read_text()
            tables = extractor.extract_from_text(content)

        if tables:
            print(f"Found {len(tables)} tables:\n")
            for i, table in enumerate(tables, 1):
                print(f"--- Table {i} ---")
                print(table)
                print()
        else:
            print("No tables found")
    else:
        print("Usage: table_extractor.py <pdf_file_or_text_file>")
