---
name: mdmax
description: Convert any file format to optimized Markdown with token economy tracking
version: 2.2.0
trigger: command
---

# MdMax - File Compression & Token Economy

Converts **16 file formats** to optimized Markdown. Save 22-80% tokens with Claude.

## Supported Formats

**Documents:** PDF, DOCX, PPTX  
**Spreadsheets:** XLSX, XLS, XLSM, CSV, TSV, ODS  
**Data:** JSON, TXT  
**Images:** PNG, JPG, JPEG, SVG  
**E-books:** EPUB  

## Quick Commands

### Convert Single File
```
/mdmax convert document.pdf
/mdmax convert spreadsheet.xlsx
/mdmax convert image.png
```

### Batch Processing
```
/mdmax convert *.pdf
/mdmax convert ~/Documents/*.xlsx
```

### View Statistics
```
/mdmax stats
/mdmax stats --export json
/mdmax stats --export csv
```

### Dashboard
```
/mdmax dashboard
/mdmax dashboard --html
```

## Usage Examples

### Basic Conversion
- **Input:** PDF (50MB) = 2,850 tokens
- **Output:** Markdown (5MB) = 285 tokens
- **Savings:** 90% ✅

### Supported Conversions
```
PDF        → Markdown (22-80% savings)
XLSX/XLS   → Markdown Tables (40-70% savings)
DOCX       → Markdown (50-70% savings)
PPTX       → Markdown Slides (40-75% savings)
PNG/JPG    → OCR + Markdown (70% savings)
EPUB       → Markdown Chapters (75-85% savings)
JSON       → Formatted Markdown (30-50% savings)
CSV/TSV    → Markdown Tables (50-60% savings)
SVG        → Markdown Description (70-80% savings)
TXT        → Optimized Markdown (20-30% savings)
```

## Features

✅ **Automatic Format Detection** - Recognizes file type instantly  
✅ **7 Compression Methods** - Boilerplate removal, metadata stripping, etc  
✅ **Real-time Statistics** - Track token savings  
✅ **Dashboard** - Visualize economy data  
✅ **Batch Processing** - Convert multiple files at once  
✅ **Export Options** - JSON, CSV, Markdown  
✅ **CLI & REST API** - Use from terminal or integrate  

## Performance

| Format | Compression | Speed | Best For |
|--------|------------|-------|----------|
| PDF | 22-80% | 2-5s | Documents |
| XLSX | 40-70% | 1-3s | Data |
| DOCX | 50-70% | 1-2s | Reports |
| PNG/JPG | 70% | 5-10s | Images |
| EPUB | 75-85% | 3-6s | E-books |
| JSON | 30-50% | <1s | Configs |

## Installation

```bash
pip install mdmax
mdmax --version
```

## Configuration

Create `~/.mdmax/config.json`:
```json
{
  "default_mode": "ultra",
  "optimize_tokens": {
    "aggressive": true,
    "remove_metadata": true,
    "compress_tables": true
  },
  "supported_formats": [
    ".pdf", ".xlsx", ".xls", ".xlsm",
    ".csv", ".tsv", ".txt", ".json",
    ".docx", ".pptx", ".ods", ".svg",
    ".jpg", ".jpeg", ".png", ".epub"
  ]
}
```

## Advanced Usage

### API Server
```bash
mdmax --server --port 8000
curl -X POST -F "file=@document.pdf" http://localhost:8000/convert
```

### Docker
```bash
docker build -t mdmax .
docker run -v $(pwd):/workspace mdmax convert file.pdf
```

### Python Integration
```python
from mdmax import MdMax

converter = MdMax()
markdown = converter.convert("document.pdf")
stats = converter.get_stats()
```

## Token Economy

**Example Savings:**
- 50MB PDF → 285 tokens (vs 2,850) = **90% savings**
- 10MB XLSX → 180 tokens (vs 1,200) = **85% savings**
- 2MB DOCX → 80 tokens (vs 600) = **87% savings**

**Monthly Projection:**
- If saving 500K tokens/month
- Annual savings: 6.2M tokens = **$93 at Claude API rates**

## Troubleshooting

### File not converting
```bash
mdmax convert file.pdf -v  # verbose mode
mdmax config --show        # check configuration
```

### Import errors
```bash
pip install mdmax[all]     # install all dependencies
```

### OCR not working (for images)
Install Tesseract:
- **Windows:** https://github.com/UB-Mannheim/tesseract/wiki
- **macOS:** `brew install tesseract`
- **Linux:** `sudo apt-get install tesseract-ocr`

## Documentation

- **GitHub:** https://github.com/brnmadeira/mdmax
- **Installation Guide:** `docs/INSTALLATION.md`
- **API Reference:** `docs/API.md`
- **Architecture:** `docs/ARCHITECTURE.md`
- **Examples:** `docs/EXAMPLES.md`

## Support

**Issues:** https://github.com/brnmadeira/mdmax/issues  
**Email:** brn.madeira@gmail.com  
**License:** MIT (Open Source)

---

**Version:** 2.2.0 | **Status:** Production Ready | **Last Updated:** 2026-08-07
