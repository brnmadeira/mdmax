# MDMAX Installation Guide

## Prerequisites

- **Python 3.8+** (check: `python --version`)
- **pip** (comes with Python)
- **Git** (for cloning)

---

## Installation Methods

### Method 1: Via pip (Recommended)

```bash
pip install mdmax
```

Verify installation:
```bash
mdmax --version
# Output: 3.0.0
```

### Method 2: From GitHub (Latest Development)

```bash
git clone https://github.com/brnmadeira/mdmax.git
cd mdmax
pip install -e .
```

The `-e` flag installs in "editable" mode (development mode).

### Method 3: From Source (Manual)

```bash
git clone https://github.com/brnmadeira/mdmax.git
cd mdmax
pip install -r requirements.txt
python -m mdmax.cli --version
```

---

## Dependencies

MDMAX automatically installs:

- **firecrawl-anydoc** — Document converter backend
- **click** — CLI framework
- **tqdm** — Progress bars
- **pydantic** — Data validation
- **httpx** — HTTP client

Optional:
- **pytesseract** — OCR for images
- **fastapi** — REST API server
- **uvicorn** — ASGI server

---

## Platform-Specific Setup

### macOS

```bash
# Install Python 3.8+ (if needed)
brew install python@3.11

# Install MDMAX
pip install mdmax

# Optional: Install Tesseract for OCR
brew install tesseract
```

### Linux (Ubuntu/Debian)

```bash
# Install Python 3.8+
sudo apt-get update
sudo apt-get install python3.11 python3-pip

# Install MDMAX
pip3 install mdmax

# Optional: Install Tesseract for OCR
sudo apt-get install tesseract-ocr
```

### Windows (PowerShell / CMD)

```powershell
# Install Python from python.org or Microsoft Store
# Then:

pip install mdmax

# Optional: Install Tesseract
# Download: https://github.com/UB-Mannheim/tesseract/wiki
# Or: choco install tesseract
```

---

## Virtual Environment Setup (Recommended)

Using `venv`:

```bash
# Create virtual environment
python -m venv mdmax-env

# Activate (macOS/Linux)
source mdmax-env/bin/activate

# Activate (Windows)
mdmax-env\Scripts\activate

# Install MDMAX
pip install mdmax

# Deactivate when done
deactivate
```

Using `conda`:

```bash
# Create environment
conda create -n mdmax python=3.11

# Activate
conda activate mdmax

# Install
pip install mdmax
```

---

## Configuration

### First Run

MDMAX creates `~/.mdmax/config.json` on first run:

```bash
mdmax config --show
```

Default configuration:
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

### Reset Configuration

```bash
mdmax config --reset
```

---

## Verify Installation

### Check CLI
```bash
mdmax --version
mdmax --help
```

### Test Conversion

```bash
# Create a test file
echo "# Test Document" > test.txt

# Convert
mdmax convert test.txt

# Expected output:
# # Test Document
```

### Test API
```python
from mdmax import MdMax

converter = MdMax()
print(converter.get_stats())

# Expected: stats dict with 0 conversions
```

---

## Optional Dependencies

### OCR for Images

For converting images (PNG, JPG) to text:

**macOS:**
```bash
brew install tesseract
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

**Windows:**
- Download installer: [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
- Or: `choco install tesseract`

Verify:
```bash
tesseract --version
```

### REST API

For running as a server:

```bash
pip install mdmax[api]
mdmax serve --port 8000
```

### Development Tools

For contributing:

```bash
pip install mdmax[dev]
# Includes: pytest, black, mypy
```

---

## Troubleshooting

### "Command not found: mdmax"

**Solution 1:** Ensure pip installed it to your PATH:
```bash
python -m mdmax.cli --version
```

**Solution 2:** Use the full path:
```bash
python -m mdmax convert document.pdf
```

**Solution 3:** Reinstall:
```bash
pip uninstall mdmax
pip install mdmax --force-reinstall
```

### "ModuleNotFoundError: No module named 'anydoc'"

Install anydoc:
```bash
pip install firecrawl-anydoc
```

### "No module named 'click'"

Install dependencies:
```bash
pip install -r requirements.txt
```

Or reinstall MDMAX:
```bash
pip install mdmax --force-reinstall
```

### OCR not working

1. Install Tesseract (see Optional Dependencies above)
2. Verify installation:
   ```bash
   tesseract --version
   ```
3. Try converting an image:
   ```bash
   mdmax convert scan.jpg -v
   ```

### Performance issues

Check system resources:
```bash
# On large files, increase temp space
export TMPDIR=/large/disk/path
mdmax convert huge_file.pdf
```

---

## Uninstallation

To remove MDMAX:

```bash
pip uninstall mdmax
```

To remove configuration files:

```bash
rm -rf ~/.mdmax
```

---

## Upgrade MDMAX

Check current version:
```bash
mdmax --version
```

Upgrade to latest:
```bash
pip install --upgrade mdmax
```

Check for updates:
```bash
pip index versions mdmax
```

---

## Docker (Optional)

Build image:
```dockerfile
FROM python:3.11-slim

RUN pip install mdmax

ENTRYPOINT ["mdmax"]
CMD ["--help"]
```

Build and run:
```bash
docker build -t mdmax .
docker run mdmax convert /data/document.pdf
```

---

## Development Installation

Clone and setup for development:

```bash
git clone https://github.com/brnmadeira/mdmax.git
cd mdmax

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest tests/

# Format code
black mdmax/

# Type checking
mypy mdmax/
```

---

## Getting Help

- **GitHub Issues:** https://github.com/brnmadeira/mdmax/issues
- **Documentation:** See README.md
- **Email:** brn.madeira@gmail.com

---

**Happy converting! 🚀**
