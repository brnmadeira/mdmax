# Auto-Convert Setup — 100% Automatic

Complete setup so the skill runs automatically without any commands.

## Prerequisites

1. **Python dependencies installed:**
```bash
pip install pdfplumber pandas openpyxl tabulate
```

2. **Skill installed** — Copy the skill folder to:
   - **Claude Code:** `~/.claude/skills/auto-convert-to-markdown/`
   - **Claude.ai:** Upload via skill interface

## Setup Option 1: Hook-Based (Recommended)

This makes the skill run automatically when Claude detects a PDF or spreadsheet file.

### 1. Create a wrapper script

Save as `convert-any-file.sh` (or `.bat` on Windows) in your project root:

```bash
#!/bin/bash
# Detect file type and convert automatically

if [[ "$1" == *.pdf ]] || [[ "$1" == *.xlsx ]] || [[ "$1" == *.csv ]] || [[ "$1" == *.ods ]]; then
    python ~/.claude/skills/auto-convert-to-markdown/scripts/convert_to_markdown.py "$1" markdown
fi
```

On Windows (PowerShell):
```powershell
# convert-any-file.ps1
param([string]$File)
if ($File -match '\.(pdf|xlsx|csv|ods)$') {
    python "$env:APPDATA\Claude\skills\auto-convert-to-markdown\scripts\convert_to_markdown.py" "$File" markdown
}
```

### 2. Add hook to `.claude/settings.json`

In your project root:

```json
{
  "version": 1,
  "hooks": {
    "PostFileRead": {
      "description": "Auto-convert PDFs and spreadsheets to Markdown",
      "command": "python",
      "args": ["~/.claude/skills/auto-convert-to-markdown/scripts/convert_to_markdown.py", "{file}", "markdown"]
    }
  }
}
```

**Note:** The `{file}` variable is replaced with the file path Claude is about to read.

## Setup Option 2: Manual Invocation

If hooks aren't available in your environment, you can manually convert files:

```bash
# When you want to convert a file
python ~/.claude/skills/auto-convert-to-markdown/scripts/convert_to_markdown.py "path/to/file.pdf"
```

Then Claude reads the generated `markdown/file.md`.

## Workflow After Setup

### With Option 1 (Automatic Hook):
```
You: "Analyze this sales report" [sales.xlsx]
↓
Hook fires automatically
↓
Skill converts → markdown/sales.md
↓
Claude reads markdown/sales.md
↓
Claude: "Based on the data..." (analysis of converted file)
```

### With Option 2 (Manual):
```
You: "Convert this for me" [report.pdf]
↓
Claude: "Let me convert this to Markdown first"
↓
Claude runs: python convert_to_markdown.py report.pdf
↓
Skill converts → markdown/report.md
↓
Claude reads markdown/report.md and analyzes it
```

## Verification

Test that everything works:

1. **Verify hook is loaded:**
```bash
claude config settings
# Should show PostFileRead hook is active
```

2. **Test with a sample file:**
```bash
# Put test file in project
python ~/.claude/skills/auto-convert-to-markdown/scripts/convert_to_markdown.py "test.xlsx"

# Check output
ls markdown/
# Should see: test.md, .metadata/test.json
```

3. **Verify markdown quality:**
```bash
cat markdown/test.md
# Should show well-formatted Markdown with tables
```

## Troubleshooting

### Hook not firing
- Check `.claude/settings.json` syntax (valid JSON)
- Verify file path in hook command is absolute
- Restart Claude Code after editing settings

### "Command not found" errors
- Ensure Python is in PATH: `python --version`
- Verify skill path is absolute: `python ~/.claude/skills/...` (not relative)

### Encoding issues with CSV
- Script auto-detects (UTF-8, Latin-1, CP1252, ISO-8859-1)
- If still failing, pre-convert CSV to UTF-8 before using

### PDF text extraction poor
- Some PDFs are image-based (scanned); OCR needed first
- Script will extract what's available

## Advanced: Custom Output Directory

By default, Markdown is saved to `markdown/` in your project root.

To change location, edit the hook command:
```json
"args": ["~/.claude/skills/auto-convert-to-markdown/scripts/convert_to_markdown.py", "{file}", "/path/to/custom/dir"]
```

## Performance Notes

- **CSV:** ~50ms for 10K rows
- **Excel:** ~200ms for 3 sheets
- **PDF:** ~500ms for 50 pages
- **File limit:** Optimal up to 50MB (larger works but slower)

## Disabling Auto-Conversion

To temporarily disable:

1. **Remove the hook** from `.claude/settings.json`, or
2. **Rename the skill folder** (temporarily disable), or  
3. **Delete the wrapper script**

Restart Claude Code to apply changes.

## Integration with Other Skills

This skill complements other tools:

- **With `/token-saver`:** Converted Markdown is automatically indexed
- **With `/run`:** Keep markdown/ in `.gitignore` (temporary conversion output)
- **With Synapse:** Conversion metadata is logged to `.metadata/`

---

**That's it!** Once set up, the skill runs automatically. No commands needed. Just attach files and Claude reads the efficient Markdown version.
