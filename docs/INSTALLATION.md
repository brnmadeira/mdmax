# Installation Guide

## Quick Start

```bash
pip install mdmax
```

## From Source

```bash
git clone https://github.com/brnmadeira/mdmax.git
cd mdmax
pip install -e ".[all]"
```

## Docker

```bash
docker build -t mdmax .
docker run -v $(pwd):/workspace mdmax --help
```

## Requirements

- Python 3.8+
- 500MB disk space
- Optional: Tesseract for OCR (images)

## Verify Installation

```bash
mdmax --version
```
