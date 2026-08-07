---
name: mdmax
description: Convert files to Markdown with token economy tracking
type: command
trigger: /mdmax
---

# MdMax Skill

Convert documents to optimized Markdown format with automatic token economy tracking.

## Quick Start

```
/mdmax convert document.pdf
/mdmax stats
/mdmax dashboard
```

## Commands

### Convert Files
```
/mdmax convert <file> [-o output.md]
```
Converts any of 16 supported formats to Markdown.

### Show Statistics
```
/mdmax stats [--export json|csv]
```
Display token savings and economy metrics.

### Dashboard
```
/mdmax dashboard [-f console|html]
```
Visualize token economy data.

### Configuration
```
/mdmax config --show
/mdmax init
```

## Supported Formats (16)

- **Documents:** PDF, DOCX, PPTX
- **Spreadsheets:** XLSX, XLS, XLSM, CSV, TSV, ODS
- **Data:** JSON, TXT
- **Images:** PNG, JPG, JPEG, SVG
- **E-books:** EPUB

## Examples

### Basic Conversion
```
/mdmax convert report.pdf
→ Saves report.md (90% smaller)
```

### Batch Processing
```
/mdmax convert *.pdf
→ Converts all PDFs in current folder
```

### Export Statistics
```
/mdmax stats --export json
→ Saves mdmax_stats.json
```

## Token Economy

**Example Savings:**
- 50MB PDF → 285 tokens (vs 2,850) = **90% savings**
- 10MB Excel → 180 tokens (vs 1,200) = **85% savings**
- 2MB Word → 80 tokens (vs 600) = **87% savings**

**Monthly Projection:**
- Average save: 500K tokens
- Annual value: ~$93 at Claude API rates

## Installation

```bash
pip install mdmax
```

Verify:
```bash
mdmax --version
```

## Troubleshooting

- **Command not found:** `pip install mdmax`
- **Import errors:** `pip install mdmax[all]`
- **OCR not working:** Install Tesseract on your system

---

**Version:** 2.2.0 | **Status:** Ready | **License:** MIT
