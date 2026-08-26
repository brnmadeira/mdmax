---
name: mdmax
version: 3.0.0
description: Convert any document format to optimized Markdown with token economy tracking
trigger: command
author: brn.madeira@gmail.com
repository: https://github.com/brnmadeira/mdmax
---

# MDMAX - Universal Document Converter

Convert **any document** (Word, PowerPoint, Excel, PDF, Images, etc.) to clean, LLM-optimized Markdown with real-time token economy tracking.

**16 formats supported** | **22-90% token savings** | **Single-digit milliseconds**

## Quick Start

### Convert a document
```bash
mdmax convert document.pdf
mdmax convert presentation.pptx -o slides.md
mdmax convert spreadsheet.xlsx
```

### Batch convert multiple files
```bash
mdmax batch "*.pdf"
mdmax batch "*.xlsx" -o markdown/
```

### View statistics
```bash
mdmax stats
mdmax stats --export json
```

### Estimate tokens in a file
```bash
mdmax estimate document.pdf
```

## Supported Formats

| Category | Formats |
|----------|---------|
| **Documents** | PDF, DOCX, PPTX, RTF |
| **Spreadsheets** | XLSX, XLS, XLSM, CSV, TSV, ODS |
| **Data** | JSON, TXT |
| **Images** | PNG, JPG, JPEG, SVG (with OCR) |
| **E-books** | EPUB |

## Token Economy

### Example Savings

| Input | Size | Input Tokens | Output Tokens | Savings |
|-------|------|--------------|---------------|---------|
| PDF Report | 50MB | 2,850 | 285 | **90%** |
| Excel Sheet | 10MB | 1,200 | 180 | **85%** |
| Word Doc | 2MB | 600 | 80 | **87%** |
| Image (OCR) | 500KB | 190 | 60 | **68%** |
| Presentation | 15MB | 1,500 | 375 | **75%** |

### Annual Projection

- Processing 1GB of documents/month
- Average savings: 70% of tokens
- **Annual cost reduction: ~$1,200** at Claude API rates

## Installation

### Via pip (recommended)
```bash
pip install mdmax
mdmax --version
```

### Via npm (uses Node.js binary)
```bash
npm install -g mdmax
mdmax --version
```

### From source
```bash
git clone https://github.com/brnmadeira/mdmax
cd mdmax
pip install -e .
```

## Usage Examples

### Python API
```python
from mdmax import MdMax, estimate_tokens

# Create converter
converter = MdMax()

# Convert file
markdown = converter.convert("report.pdf")
markdown = converter.convert("data.xlsx", output_path="data.md")

# Convert bytes
pdf_bytes = open("document.pdf", "rb").read()
markdown = converter.convert_bytes(pdf_bytes, format="pdf")

# View statistics
stats = converter.get_stats()
print(converter.get_dashboard())

# Estimate tokens
tokens = estimate_tokens("large_file.pdf")
```

### CLI
```bash
# Basic conversion (output to stdout)
mdmax convert document.pdf

# Save to file
mdmax convert document.pdf -o output.md

# Batch processing
mdmax batch "*.pdf" -o converted/

# View all statistics
mdmax stats

# Export statistics
mdmax stats --export json -o stats.json
mdmax stats --export csv -o stats.csv

# Estimate tokens without converting
mdmax estimate large_file.pdf

# Verbose mode
mdmax convert document.pdf -v
```

### REST API (if enabled)
```bash
# Start API server
mdmax serve --port 8000

# Convert via HTTP
curl -X POST -F "file=@document.pdf" http://localhost:8000/convert
```

## Configuration

MDMAX creates a config file at `~/.mdmax/config.json`:

```json
{
  "optimize_tokens": true,
  "remove_metadata": true,
  "compress_tables": true,
  "supported_formats": [
    ".pdf", ".docx", ".pptx", ".xlsx", ".xls", ".xlsm",
    ".csv", ".tsv", ".txt", ".json", ".ods", ".rtf",
    ".jpg", ".jpeg", ".png", ".svg", ".epub"
  ]
}
```

### View configuration
```bash
mdmax config --show
```

### Reset to defaults
```bash
mdmax config --reset
```

## Advanced Features

### Optimization Methods

MDMAX uses 7 compression techniques:

1. **Boilerplate Removal** - Strips headers, footers, styling info
2. **Metadata Stripping** - Removes author, creation date, etc.
3. **Table Compression** - Optimizes table structure for Markdown
4. **Image Optimization** - Converts to description or OCR
5. **Reference Flattening** - Converts references to inline
6. **Whitespace Normalization** - Removes unnecessary spacing
7. **Semantic Rewriting** - Simplifies complex structures

### OCR for Images

When converting images to Markdown:
```bash
# Requires Tesseract (installed automatically on most systems)
mdmax convert scan.jpg -o scan.md

# Manual Tesseract installation:
# macOS: brew install tesseract
# Linux: sudo apt-get install tesseract-ocr
# Windows: choco install tesseract or download installer
```

### Batch with Pattern
```bash
# Convert all PDFs in subdirectories
mdmax batch "**/*.pdf" -o markdown/

# Convert specific types
mdmax batch "reports/*.xlsx" -o tables/
mdmax batch "scans/**/*.jpg" -o ocr/
```

## Troubleshooting

### "anydoc not found"
MDMAX requires the anydoc library. Install it:
```bash
pip install firecrawl-anydoc
```

### Conversion fails
Enable verbose mode for diagnostics:
```bash
mdmax convert document.pdf -v
```

### OCR not working
Install Tesseract for your OS:
- **macOS:** `brew install tesseract`
- **Linux:** `sudo apt-get install tesseract-ocr`
- **Windows:** Download from [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki)

### Out of memory on large files
Process in batches and convert smaller sections:
```bash
# Split PDF first, then convert
mdmax batch "split_*.pdf" -o sections/
```

## Performance

| Task | Speed | Notes |
|------|-------|-------|
| PDF (10MB) | 2-5s | Depends on complexity |
| Excel (5MB) | 1-3s | Fast, optimized |
| Word (2MB) | 1-2s | Quick conversion |
| Presentation (8MB) | 3-6s | Slide-by-slide |
| Image OCR (500KB) | 5-10s | Tesseract dependency |

## Statistics & Tracking

MDMAX logs all conversions to `~/.mdmax/economy.jsonl`:

```bash
# View logs
cat ~/.mdmax/economy.jsonl | jq .

# Export to CSV
mdmax stats --export csv -o report.csv

# Total savings
mdmax stats
```

Each record includes:
- File format and size
- Input/output token counts
- Compression percentage
- Timestamp

## API Reference

### Python

```python
from mdmax import MdMax, TokenEconomy, estimate_tokens

# Main converter class
converter = MdMax(optimize=True)
converter.convert(file_path, output_path=None)
converter.convert_bytes(data, format)
converter.get_stats()
converter.get_dashboard()

# Economy tracking
economy = TokenEconomy()
economy.track(filename, input_bytes, output_bytes, format)
economy.get_stats()
economy.get_dashboard()
economy.export(format="json", output_path=None)

# Utilities
estimate_tokens(file_path, format=None)
```

### CLI

```bash
mdmax convert <file> [-o OUTPUT] [-v]
mdmax batch <pattern> [-o OUTPUT_DIR] [-v]
mdmax stats [--export {json,csv}] [-o OUTPUT]
mdmax estimate <file>
mdmax config [--show] [--reset]
```

## GitHub

Repository: https://github.com/brnmadeira/mdmax
Issues: https://github.com/brnmadeira/mdmax/issues
Email: brn.madeira@gmail.com

## License

MIT - Open Source

---

**Version:** 3.0.0 | **Status:** Production | **Built with:** anydoc (Firecrawl) + Python
