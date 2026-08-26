# MDMAX Phase 2: Native Python Implementation

**Goal:** Replace anydoc dependency with native Python converters

**Timeline:** MDMAX 4.0 (Q4 2026)

---

## Current State (Phase 1)

✅ **MDMAX 3.0 - Wrapper Architecture**
- anydoc as backend (Rust, ultra-fast)
- Your dashboard + economy tracking on top
- Unified CLI interface
- Agent Skill published
- All references renamed from "anydoc" to "MDMAX"

---

## Phase 2 Roadmap

### 1. **Document Converters** (Priority: HIGH)

#### PDF → Markdown
```python
# mdmax/converters/pdf.py
class PDFConverter:
    def convert(pdf_bytes: bytes) -> str:
        # Use: pdfplumber, PyPDF2, or fitz
        # Extract: text, tables, images
        # Output: clean markdown
```

**Dependencies:**
- `pdfplumber` (fast, accurate table extraction)
- `pdf2image` (for image-heavy PDFs)
- `pytesseract` (OCR fallback)

#### Word → Markdown
```python
# mdmax/converters/docx.py
class DocxConverter:
    def convert(docx_bytes: bytes) -> str:
        # Use: python-docx
        # Extract: text, images, tables, styles
        # Output: markdown with formatting preserved
```

**Dependencies:**
- `python-docx` (native)

#### PowerPoint → Markdown
```python
# mdmax/converters/pptx.py
class PptxConverter:
    def convert(pptx_bytes: bytes) -> str:
        # Use: python-pptx
        # Extract: slide text, speaker notes, images
        # Output: slide-by-slide markdown
```

**Dependencies:**
- `python-pptx` (native)

#### Excel → Markdown
```python
# mdmax/converters/xlsx.py
class XlsxConverter:
    def convert(xlsx_bytes: bytes) -> str:
        # Use: openpyxl or pandas
        # Extract: sheets, tables, formulas
        # Output: markdown tables with metadata
```

**Dependencies:**
- `openpyxl` (native, fast)
- `pandas` (alternative, for complex data)

#### CSV/TSV → Markdown
```python
# mdmax/converters/csv.py
class CsvConverter:
    def convert(csv_bytes: bytes, format: str) -> str:
        # Use: csv module + pandas for complex cases
        # Extract: rows, columns
        # Output: markdown tables
```

**Dependencies:**
- None (stdlib csv module)

#### Image → Markdown
```python
# mdmax/converters/image.py
class ImageConverter:
    def convert(image_bytes: bytes) -> str:
        # Fallback to OCR (Tesseract)
        # Or: extract metadata, dimensions
        # Output: image link + description
```

**Dependencies:**
- `pytesseract` (OCR)
- `Pillow` (image metadata)

#### EPUB → Markdown
```python
# mdmax/converters/epub.py
class EpubConverter:
    def convert(epub_bytes: bytes) -> str:
        # Use: ebooklib
        # Extract: chapters, text, TOC
        # Output: chapter-based markdown
```

**Dependencies:**
- `ebooklib` (native EPUB support)

#### JSON → Markdown
```python
# mdmax/converters/json.py
class JsonConverter:
    def convert(json_bytes: bytes) -> str:
        # Parse JSON
        # Output: formatted markdown code blocks or tables
```

**Dependencies:**
- None (stdlib json)

#### Text → Markdown
```python
# mdmax/converters/txt.py
class TxtConverter:
    def convert(txt_bytes: bytes) -> str:
        # Just format text nicely
        # Detect: sections, lists, etc.
        # Output: structured markdown
```

**Dependencies:**
- None (stdlib)

---

### 2. **Converter Registry** (Priority: HIGH)

```python
# mdmax/converters/__init__.py
class ConverterRegistry:
    CONVERTERS = {
        'pdf': PDFConverter,
        'docx': DocxConverter,
        'pptx': PptxConverter,
        'xlsx': XlsxConverter,
        'csv': CsvConverter,
        'json': JsonConverter,
        'png': ImageConverter,
        'jpg': ImageConverter,
        # ... etc
    }
    
    @staticmethod
    def get_converter(format: str):
        return CONVERTERS.get(format.lower())
    
    @staticmethod
    def convert(data: bytes, format: str) -> str:
        converter_class = CONVERTERS.get(format.lower())
        if not converter_class:
            raise ValueError(f"No converter for {format}")
        return converter_class().convert(data)
```

---

### 3. **Streaming & Large Files** (Priority: MEDIUM)

```python
# mdmax/streaming.py
class StreamingConverter:
    """Handle files > 500MB"""
    
    def convert_streaming(
        file_path: Path,
        chunk_size: int = 10_000_000
    ) -> Iterator[str]:
        """Yield markdown chunks"""
        pass
```

---

### 4. **Custom Transformation Pipeline** (Priority: MEDIUM)

```python
# mdmax/pipeline.py
class TransformPipeline:
    """
    Apply custom transformations to markdown output
    """
    
    def add_transform(self, transform: Callable):
        """Register custom transformer"""
        
    def remove_metadata(self):
        """Strip author, dates, etc."""
        
    def compress_tables(self):
        """Optimize table formatting"""
        
    def flatten_references(self):
        """Convert footnotes to inline"""
        
    def normalize_headings(self):
        """Standardize heading hierarchy"""
```

---

### 5. **REST API** (Priority: LOW)

```python
# mdmax/api.py
from fastapi import FastAPI

app = FastAPI()

@app.post("/convert")
async def convert(file: UploadFile):
    """Convert uploaded file to markdown"""
    
@app.get("/stats")
async def get_stats():
    """Get economy statistics"""
    
@app.post("/batch")
async def batch_convert(files: List[UploadFile]):
    """Batch convert multiple files"""
```

---

### 6. **WebAssembly (Browser)** (Priority: LOW)

```javascript
// mdmax-wasm/index.js
import init, { convert, convertBytes } from './wasm';

await init();
const markdown = convertBytes(pdfBytes, 'pdf');
```

---

## Implementation Plan

### Week 1-2: PDF + Word + Excel
```bash
pip install pdfplumber python-docx openpyxl
```

- [ ] Create `converters/pdf.py`
- [ ] Create `converters/docx.py`
- [ ] Create `converters/xlsx.py`
- [ ] Register converters
- [ ] Unit tests for each

### Week 3: PowerPoint + CSV
- [ ] Create `converters/pptx.py`
- [ ] Create `converters/csv.py`
- [ ] Integration tests

### Week 4: Images + EPUB + JSON
- [ ] Create `converters/image.py`
- [ ] Create `converters/epub.py`
- [ ] Create `converters/json.py`

### Week 5: Pipeline + Streaming
- [ ] Create `pipeline.py`
- [ ] Create `streaming.py`
- [ ] Performance testing

### Week 6: API + Polish
- [ ] Create REST API
- [ ] Full test coverage
- [ ] Release MDMAX 4.0

---

## Performance Target

| Format | Phase 1 (anydoc) | Phase 2 (Native) | Target |
|--------|-----------------|-----------------|--------|
| PDF (50MB) | 2-5s | 3-8s | Match anydoc |
| Excel (10MB) | 1-3s | 1-2s | **Faster** |
| Word (2MB) | 1-2s | <1s | **Faster** |
| PowerPoint (8MB) | 3-6s | 3-5s | Match anydoc |
| Overall | 100% | 95-105% | ≤ 10% slower |

---

## Dependencies Tree

```
MDMAX 4.0
├── PDF
│   ├── pdfplumber (primary)
│   ├── pdf2image (images)
│   └── pytesseract (OCR fallback)
├── Word
│   └── python-docx
├── PowerPoint
│   └── python-pptx
├── Excel
│   ├── openpyxl (primary)
│   └── pandas (complex data)
├── EPUB
│   └── ebooklib
├── Images
│   ├── Pillow (metadata)
│   └── pytesseract (OCR)
└── Common
    ├── click (CLI)
    ├── tqdm (progress)
    └── pydantic (validation)
```

---

## Removal of anydoc

Once Phase 2 is complete:

1. ✅ All tests pass with native converters
2. ✅ Performance is acceptable
3. ✅ All 16 formats working
4. Remove from `requirements.txt`
5. Remove from `setup.py`
6. Final release: MDMAX 4.0 (Pure Python, Zero External Dependencies)

---

## Success Criteria

- [ ] All 16 formats convert natively
- [ ] Test coverage > 85%
- [ ] Performance within 10% of anydoc
- [ ] No external tool dependencies (Tesseract optional)
- [ ] Token economy tracking maintained
- [ ] CLI + API + Python all working
- [ ] Agent Skill still compatible

---

## Notes

- **Keep anydoc as fallback** during transition (optional flag)
- **Run parallel testing** with both implementations
- **Monitor performance** on real-world documents
- **Gather user feedback** before final release
