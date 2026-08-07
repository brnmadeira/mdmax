# MdMax Skill for Claude Code & Cowork

Transform files to optimized Markdown with automatic token economy tracking.

## Installation

1. **Ensure MdMax is installed:**
   ```bash
   pip install mdmax
   ```

2. **Skill files are ready:**
   - `.claude/mdmax.md` - Skill definition
   - `.claude/mdmax-runner.py` - Command executor
   - `.claude/settings.json` - Configuration

## Usage

### In Claude Code

```
/mdmax convert document.pdf
/mdmax convert spreadsheet.xlsx
/mdmax stats
/mdmax dashboard
```

### In Claude Cowork

Mention the skill in your workflow:
```
Use /mdmax to convert our documents to Markdown
/mdmax convert report.docx
/mdmax stats --export json
```

## Supported Commands

| Command | Usage | Example |
|---------|-------|---------|
| convert | `mdmax convert <file>` | `/mdmax convert file.pdf` |
| stats | `mdmax stats` | `/mdmax stats` |
| dashboard | `mdmax dashboard` | `/mdmax dashboard` |
| config | `mdmax config --show` | `/mdmax config --show` |
| init | `mdmax init` | `/mdmax init` |

## Formats Supported (16 total)

**Documents:** PDF, DOCX, PPTX  
**Spreadsheets:** XLSX, XLS, XLSM, CSV, TSV, ODS  
**Data:** JSON, TXT  
**Images:** PNG, JPG, JPEG, SVG  
**E-books:** EPUB  

## Features

✅ Auto-detect file format  
✅ One-command conversion  
✅ Real-time token savings  
✅ Batch processing  
✅ Statistics export  
✅ Dashboard visualization  

## Examples

### Convert PDF with output
```bash
/mdmax convert research.pdf -o research.md
```

### View statistics
```bash
/mdmax stats
```

### Export data
```bash
/mdmax stats --export json
/mdmax stats --export csv
```

### Dashboard
```bash
/mdmax dashboard
/mdmax dashboard --html
```

## Configuration

Edit `~/.mdmax/config.json`:

```json
{
  "default_mode": "ultra",
  "optimize_tokens": {
    "aggressive": true,
    "remove_metadata": true,
    "compress_tables": true
  }
}
```

## Troubleshooting

### "mdmax not found"
Install with: `pip install mdmax`

### Permission denied
Ensure `.claude/settings.json` has `bash_execute: true`

### File conversion failing
Check format is supported: `mdmax --help`

## API Integration

For programmatic access:

```python
from mdmax import MdMax

converter = MdMax()
markdown = converter.convert("document.pdf")
stats = converter.get_stats()
```

## Performance Tips

1. **Large files:** Use `--batch` for multiple files
2. **OCR images:** Pre-install Tesseract for best results
3. **API mode:** Run `mdmax --server` for daemon mode

## Support

- GitHub: https://github.com/brnmadeira/mdmax
- Issues: https://github.com/brnmadeira/mdmax/issues
- Email: brn.madeira@gmail.com

---

**Version:** 2.2.0 | **Type:** Skill | **Status:** Ready for Claude Code & Cowork
