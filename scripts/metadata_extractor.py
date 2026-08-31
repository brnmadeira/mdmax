#!/usr/bin/env python3
"""
MdMax Metadata Extractor - Auto-generate YAML frontmatter
Feature [3] of v2.2: Extract metadata and generate frontmatter automatically
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import json


class MetadataExtractor:
    """Extract metadata from documents and generate YAML frontmatter"""

    PLACEHOLDER_VALUES = {'untitled', 'anonymous', 'unspecified', 'unknown', 'none', ''}

    def _is_placeholder(self, value) -> bool:
        """Detect generator defaults (e.g. reportlab's 'untitled'/'anonymous') that aren't real metadata"""
        return not value or str(value).strip().lower() in self.PLACEHOLDER_VALUES

    def _normalize_pdf_date(self, date_str: str) -> str:
        """PDF dates look like D:20260831095856-03'00' - pull out YYYY-MM-DD"""
        match = re.search(r'D:(\d{4})(\d{2})(\d{2})', str(date_str))
        if match:
            return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
        return self._normalize_date(str(date_str))

    def __init__(self):
        self.common_patterns = {
            'author': [
                r'(?im)^\s*(?:author|by|from|de|written by|criado por)\s*:\s*(.+)$',
            ],
            'date': [
                r'(?:date|data|created|data de criação)\s*:?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
                r'(\d{4}-\d{2}-\d{2})',
                r'(?:2026|2025|2024|2023)-\d{2}-\d{2}',
            ],
            'title': [
                r'(?:title|titulo|nome|subject)\s*:?\s*([^\n]+)',
                r'^#+\s+(.+)$',
            ],
            'tags': [
                r'(?:tags|keywords|palavras-chave)\s*:?\s*([^,\n]+(?:,[^,\n]+)*)',
            ],
        }

    def extract_from_text(self, text: str, filename: str) -> Dict:
        """Extract metadata from document text"""
        metadata = {
            'title': self._extract_title(text, filename),
            'date': self._extract_date(text),
            'author': self._extract_author(text),
            'tags': self._extract_tags(text),
            'summary': self._extract_summary(text),
        }
        return {k: v for k, v in metadata.items() if v}

    def extract_from_filename(self, filename: str) -> Dict:
        """Extract metadata from filename"""
        metadata = {}

        # Remove extension
        name = Path(filename).stem

        # Pattern: "TITLE - DATE" or "TITLE_DATE"
        date_pattern = r'\d{4}[-_]\d{2}[-_]\d{2}|\d{1,2}[-_]\d{1,2}[-_]\d{4}'
        date_match = re.search(date_pattern, name)

        if date_match:
            metadata['date'] = self._normalize_date(date_match.group())
            title = name[:date_match.start()].strip(' -_')
        else:
            title = name

        if title:
            metadata['title'] = self._clean_title(title)

        return metadata

    def extract_from_excel_metadata(self, excel_file_path: str) -> Dict:
        """Extract metadata from Excel file properties"""
        try:
            from openpyxl import load_workbook

            wb = load_workbook(excel_file_path)
            props = wb.properties

            metadata = {}
            if props.title and not self._is_placeholder(props.title):
                metadata['title'] = props.title
            if props.author and not self._is_placeholder(props.author):
                metadata['author'] = props.author
            if props.created:
                metadata['date'] = props.created.strftime('%Y-%m-%d')
            if props.subject and not self._is_placeholder(props.subject):
                metadata['tags'] = [props.subject]
            if props.keywords:
                metadata['tags'] = props.keywords.split(',')

            return metadata
        except Exception:
            return {}

    def extract_from_pdf_metadata(self, pdf_file_path: str) -> Dict:
        """Extract metadata from PDF properties"""
        try:
            import PyPDF2

            with open(pdf_file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                if reader.metadata:
                    metadata = {}

                    if reader.metadata.get('/Title') and not self._is_placeholder(reader.metadata.get('/Title')):
                        metadata['title'] = reader.metadata['/Title']
                    if reader.metadata.get('/Author') and not self._is_placeholder(reader.metadata.get('/Author')):
                        metadata['author'] = reader.metadata['/Author']
                    if reader.metadata.get('/CreationDate'):
                        metadata['date'] = self._normalize_pdf_date(reader.metadata['/CreationDate'])
                    if reader.metadata.get('/Subject') and not self._is_placeholder(reader.metadata.get('/Subject')):
                        metadata['tags'] = [reader.metadata['/Subject']]

                    return metadata
        except Exception:
            pass

        return {}

    def _extract_title(self, text: str, filename: str) -> Optional[str]:
        """Extract title from text"""
        # Skip mechanically-generated section headers (Slide 1, Page 2, Sheet: X, Image: X) -
        # they're converter artifacts, not real document titles
        # mdmax's own converters prefix output with a structural heading
        # (Page N, Sheet: name, Slide N, Image: name, Extracted Text, SVG Image,
        # XLS File: name) - none of those are a real document title
        generic_heading = re.compile(
            r'^(slide|page)\s*\d*$'
            r'|^sheet\s*:'
            r'|^image\s*:'
            r'|^extracted text$'
            r'|^svg image$'
            r'|^xls file\s*:'
            r'|^json data$',
            re.IGNORECASE
        )

        for heading_match in re.finditer(r'^#+\s+(.+)$', text, re.MULTILINE):
            candidate = heading_match.group(1).strip()
            if not generic_heading.match(candidate):
                return candidate

        # Fallback to filename
        return Path(filename).stem

    def _extract_date(self, text: str) -> Optional[str]:
        """Extract date from text"""
        for pattern in self.common_patterns['date']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return self._normalize_date(match.group(1) if match.lastindex else match.group())
        return None

    def _extract_author(self, text: str) -> Optional[str]:
        """Extract author from text"""
        for pattern in self.common_patterns['author']:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                return match.group(1).strip()
        return None

    def _extract_tags(self, text: str) -> Optional[List[str]]:
        """Extract tags from text"""
        tags = set()

        # Look for hashtags
        hashtags = re.findall(r'#(\w+)', text)
        tags.update(hashtags)

        # Look for keywords/tags patterns
        for pattern in self.common_patterns['tags']:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                tag_str = match.group(1)
                tag_list = [t.strip() for t in tag_str.split(',')]
                tags.update(tag_list)

        return sorted(list(tags))[:10] if tags else None

    def _extract_summary(self, text: str) -> Optional[str]:
        """Extract first meaningful paragraph as summary"""
        lines = text.split('\n')
        in_code_fence = False

        for line in lines:
            line = line.strip()

            if line.startswith('```'):
                in_code_fence = not in_code_fence
                continue
            if in_code_fence:
                continue

            # Skip headings, table rows/separators, frontmatter delimiters,
            # image embeds, and generated notices - none of those are prose
            if (line and len(line) > 20
                    and not line.startswith('#')
                    and not line.startswith('|')
                    and not line.startswith('---')
                    and not line.startswith('===')
                    and not line.startswith('![')
                    and not line.startswith('*(')):
                return line[:150]

        return None

    def _normalize_date(self, date_str: str) -> str:
        """Normalize date to YYYY-MM-DD format"""
        # Try various formats
        formats = [
            '%Y-%m-%d',
            '%Y/%m/%d',
            '%d-%m-%Y',
            '%d/%m/%Y',
            '%m-%d-%Y',
            '%m/%d/%Y',
        ]

        for fmt in formats:
            try:
                parsed = datetime.strptime(date_str.replace('_', '-'), fmt)
                return parsed.strftime('%Y-%m-%d')
            except ValueError:
                continue

        return date_str

    def _clean_title(self, title: str) -> str:
        """Clean title by removing special characters"""
        return re.sub(r'[_\-]+', ' ', title).title().strip()

    def generate_frontmatter(self, metadata: Dict) -> str:
        """Generate YAML frontmatter from metadata"""
        if not metadata:
            return ""

        frontmatter = "---\n"

        # Order matters
        keys_order = ['title', 'author', 'date', 'tags', 'summary']

        for key in keys_order:
            if key in metadata and metadata[key]:
                value = metadata[key]

                if isinstance(value, list):
                    # YAML list
                    frontmatter += f"{key}:\n"
                    for item in value:
                        frontmatter += f"  - {item}\n"
                elif isinstance(value, str):
                    # Check if needs quotes
                    if ':' in value or '"' in value:
                        frontmatter += f'{key}: "{value}"\n'
                    else:
                        frontmatter += f"{key}: {value}\n"

        frontmatter += "---\n"
        return frontmatter

    def add_frontmatter_to_markdown(self, markdown: str, metadata: Dict) -> str:
        """Add frontmatter to markdown content"""
        frontmatter = self.generate_frontmatter(metadata)

        if frontmatter == "---\n---\n":
            return markdown

        # Remove existing frontmatter if present
        if markdown.startswith("---"):
            lines = markdown.split('\n')
            if '---' in lines[1:]:
                end_idx = lines.index('---', 1)
                markdown = '\n'.join(lines[end_idx+1:]).lstrip()

        return frontmatter + markdown

    def detect_content_tags(self, text: str) -> List[str]:
        """Auto-detect tags based on content"""
        tags = set()

        # Content-based detection
        patterns = {
            'excel': r'(product|quantidade|estoque|pedido|venda)',
            'pdf': r'(relatório|report|documento)',
            'invoice': r'(invoice|nota fiscal|pedido)',
            'inventory': r'(estoque|inventário|stock)',
            'data': r'(tabela|table|dados|dados)',
            'financial': r'(preço|price|valor|valor|custo|cost)',
        }

        text_lower = text.lower()
        for tag, pattern in patterns.items():
            if re.search(pattern, text_lower, re.IGNORECASE):
                tags.add(tag)

        return sorted(list(tags))


if __name__ == '__main__':
    # Test
    extractor = MetadataExtractor()

    test_text = """
    # Sugestão de Pedido II

    Author: Way Suplementos
    Date: 2026-08-05
    Tags: pedido, inventário, suplementos

    Este é um documento de sugestão de pedido para Way Suplementos.
    """

    metadata = extractor.extract_from_text(test_text, "pedido.md")
    print("Extracted metadata:")
    print(json.dumps(metadata, indent=2, ensure_ascii=False))

    frontmatter = extractor.generate_frontmatter(metadata)
    print("\nGenerated frontmatter:")
    print(frontmatter)

    full_md = extractor.add_frontmatter_to_markdown(test_text, metadata)
    print("\nFull markdown with frontmatter:")
    print(full_md)
