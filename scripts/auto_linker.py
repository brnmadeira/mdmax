#!/usr/bin/env python3
"""
MdMax Auto-Linker - Automatic cross-references between documents
Feature [2] of v2.2: Create wiki-style links between documents
"""

import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
import json


class AutoLinker:
    """Create automatic wiki-style links between documents"""

    def __init__(self):
        self.documents: Dict[str, Dict] = {}
        self.link_index: Dict[str, Set[str]] = {}

    def add_document(self, doc_path: str, content: str, metadata: Dict = None):
        """Add document to linking index"""
        path = Path(doc_path)
        doc_id = path.stem

        # Extract key terms from content
        key_terms = self._extract_key_terms(content)

        self.documents[doc_id] = {
            'path': str(path),
            'content': content,
            'metadata': metadata or {},
            'key_terms': key_terms,
        }

    def _extract_key_terms(self, content: str) -> Set[str]:
        """Extract potential link targets from content"""
        terms = set()

        # Extract headings (## Title)
        headings = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)
        for heading in headings:
            # Clean heading
            clean = heading.strip().lower()
            if len(clean) > 3:
                terms.add(clean)

        # Extract capitalized phrases (potential titles)
        capitalized = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', content)
        for term in capitalized:
            if len(term) > 4 and term not in ['The', 'And', 'For']:
                terms.add(term.lower())

        return terms

    def find_cross_references(self) -> Dict[str, List[Tuple[str, str]]]:
        """Find cross-references between documents"""
        cross_refs = {}

        doc_ids = list(self.documents.keys())

        for i, doc_id in enumerate(doc_ids):
            doc = self.documents[doc_id]
            refs = []

            # Compare with other documents
            for other_id in doc_ids[i+1:]:
                if other_id == doc_id:
                    continue

                other_doc = self.documents[other_id]
                other_terms = other_doc['key_terms']

                # Find matching terms
                matches = doc['key_terms'] & other_terms

                if matches:
                    refs.append((other_id, len(matches)))

            if refs:
                # Sort by match count
                refs.sort(key=lambda x: x[1], reverse=True)
                cross_refs[doc_id] = refs

        return cross_refs

    def create_link(self, source_content: str, target_doc_id: str, context: str = None) -> str:
        """Create a wiki-style link in markdown"""
        if context:
            return f"[{context}]({target_doc_id})"
        else:
            return f"[[{target_doc_id}]]"

    def add_cross_reference_links(self, doc_id: str, cross_refs: List[Tuple[str, int]]) -> str:
        """Add cross-reference links to document"""
        doc = self.documents[doc_id]
        content = doc['content']

        # Add references section at the end
        refs_section = "\n\n---\n\n## Cross-References\n\n"

        for ref_id, match_count in cross_refs[:5]:  # Top 5 references
            ref_doc = self.documents[ref_id]
            title = ref_doc['metadata'].get('title', ref_id)
            refs_section += f"- [{title}]({ref_id}) ({match_count} related topics)\n"

        return content + refs_section

    def build_reference_index(self) -> Dict[str, List[str]]:
        """Build index of all references"""
        index = {}

        cross_refs = self.find_cross_references()

        for doc_id, refs in cross_refs.items():
            index[doc_id] = [ref[0] for ref in refs]

        return index

    def generate_wiki_structure(self) -> str:
        """Generate a wiki structure showing all interconnections"""
        index = self.build_reference_index()

        structure = "# Document Graph\n\n"

        structure += "## Documents\n\n"
        for doc_id in sorted(self.documents.keys()):
            doc = self.documents[doc_id]
            title = doc['metadata'].get('title', doc_id)
            structure += f"- **{title}** (`{doc_id}`)\n"

        structure += "\n## Cross-References\n\n"
        for doc_id, refs in sorted(index.items()):
            if refs:
                doc = self.documents[doc_id]
                title = doc['metadata'].get('title', doc_id)
                ref_titles = [
                    self.documents[ref]['metadata'].get('title', ref)
                    for ref in refs
                ]
                structure += f"- **{title}** links to:\n"
                for ref_title in ref_titles:
                    structure += f"  - {ref_title}\n"

        return structure

    def export_as_json(self, filepath: str):
        """Export index as JSON"""
        index = self.build_reference_index()

        export = {
            'documents': {
                doc_id: {
                    'title': doc['metadata'].get('title', doc_id),
                    'path': doc['path'],
                }
                for doc_id, doc in self.documents.items()
            },
            'references': index,
        }

        Path(filepath).write_text(json.dumps(export, indent=2, ensure_ascii=False))


class BatchAutoLinker:
    """Process multiple documents and create automatic links"""

    def __init__(self, markdown_dir: Path):
        self.markdown_dir = Path(markdown_dir)
        self.linker = AutoLinker()

    def load_all_documents(self):
        """Load all markdown documents from directory"""
        for md_file in self.markdown_dir.glob('*.md'):
            content = md_file.read_text(encoding='utf-8')

            # Extract metadata from frontmatter
            metadata = {}
            if content.startswith('---'):
                end_idx = content.find('---', 3)
                if end_idx > 0:
                    frontmatter = content[3:end_idx]
                    for line in frontmatter.split('\n'):
                        if ':' in line:
                            key, val = line.split(':', 1)
                            metadata[key.strip()] = val.strip()

            self.linker.add_document(str(md_file), content, metadata)

    def process_and_link(self):
        """Process all documents and add cross-reference links"""
        cross_refs = self.linker.find_cross_references()

        for doc_id, refs in cross_refs.items():
            doc = self.linker.documents[doc_id]
            linked_content = self.linker.add_cross_reference_links(doc_id, refs)

            # Save back
            output_path = self.markdown_dir / f"{doc_id}_linked.md"
            output_path.write_text(linked_content, encoding='utf-8')

    def generate_navigation(self) -> str:
        """Generate navigation markdown"""
        nav = "# Navigation\n\n"
        nav += self.linker.generate_wiki_structure()
        return nav


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        markdown_dir = Path(sys.argv[1])
        batch_linker = BatchAutoLinker(markdown_dir)
        batch_linker.load_all_documents()
        batch_linker.process_and_link()

        # Generate navigation
        nav = batch_linker.generate_navigation()
        nav_path = markdown_dir / '_navigation.md'
        nav_path.write_text(nav, encoding='utf-8')

        print(f"✅ Linked {len(batch_linker.linker.documents)} documents")
        print(f"📊 Navigation saved to: {nav_path}")
    else:
        print("Usage: auto_linker.py <markdown_directory>")
