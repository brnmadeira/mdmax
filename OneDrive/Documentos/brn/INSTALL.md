# Installation Guide

## Quick Install (Recommended)

```bash
pip install mdmax
```

## Install from Source

```bash
git clone https://github.com/brnmadeira/mdmax.git
cd mdmax
pip install -e .
```

## Install with Optional Features

```bash
# With API server
pip install mdmax[api]

# With E-book support
pip install mdmax[epub]

# With OCR (requires Tesseract on system)
pip install mdmax[ocr]

# With all features
pip install mdmax[all]

# Development setup
pip install mdmax[dev]
```

## System Dependencies

### For OCR (Optional)

If you want to use OCR for images, install Tesseract:

**Windows:**
```bash
# Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
# Then add to Python:
pip install mdmax[ocr]
```

**macOS:**
```bash
brew install tesseract
pip install mdmax[ocr]
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr
pip install mdmax[ocr]
```

## Verify Installation

```bash
mdmax --version
mdmax --help
```

## Troubleshooting

### Error: "command not found: mdmax"

Make sure pip is in your PATH:
```bash
python -m mdmax --help
```

### Error: "No module named 'scripts'"

Reinstall in development mode:
```bash
pip install -e .
```

### ImportError on specific modules

Install the optional dependencies:
```bash
pip install mdmax[all]
```

## Docker Installation

```bash
docker build -t mdmax .
docker run -v $(pwd):/workspace mdmax --help
```
