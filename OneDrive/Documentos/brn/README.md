# MdMax - Token Economy for Claude

[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-green.svg)](https://www.python.org/downloads/)
[![Docker Ready](https://img.shields.io/badge/Docker-Ready-blue.svg)](Dockerfile)

**Compress files by ~80% and save tokens with Claude AI**

## Features

✅ **16 File Formats** - PDF, Excel, Word, Images, E-books, JSON, CSV, and more  
✅ **22-80% Token Savings** - Real compression, real results  
✅ **7 Optimization Methods** - Boilerplate removal, metadata stripping, and more  
✅ **CLI + REST API** - Use from terminal or integrate with applications  
✅ **Docker Support** - Deploy anywhere  
✅ **MIT License** - Free and open source  
✅ **Real-time Dashboard** - Track token economy with visualizations  

## Quick Start

### Installation

```bash
pip install mdmax
```

### Usage

```bash
# Convert a file
mdmax document.pdf

# Batch processing
mdmax *.xlsx

# View statistics
mdmax --stats

# Start API server
mdmax --server
```

### Docker

```bash
docker build -t mdmax .
docker run -v $(pwd):/workspace mdmax document.pdf
```

## Performance

| Format | Compression | Example |
|--------|------------|---------|
| PDF | 22-80% | 50MB → 5MB |
| XLSX | 40-70% | Full optimization |
| DOCX | 50-70% | Removes formatting overhead |
| PNG/JPG | 70% | OCR + compression |
| EPUB | 75-85% | E-book optimization |

**Real example:** 50MB PDF = 2,850 tokens → 285 tokens (**90% savings!**)

## Supported Formats

```
Documents: PDF, DOCX, PPTX
Spreadsheets: XLSX, XLS, XLSM, CSV, TSV, ODS
Data: JSON, TXT
Images: PNG, JPG, JPEG, SVG
E-books: EPUB
```

## Architecture

- **converters.py** - Format detection and conversion
- **optimizers.py** - 7 compression methods
- **cli.py** - Command-line interface
- **api.py** - REST API server
- **dashboard.py** - Token economy visualization

## Documentation

- [Installation](docs/INSTALLATION.md)
- [API Reference](docs/API.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Examples](docs/EXAMPLES.md)

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - See [LICENSE](LICENSE) for details

## Author

**Bruno Madeira** - [brn.madeira@gmail.com](mailto:brn.madeira@gmail.com)

---

**Status:** Production Ready | **Version:** 2.2 | **Last Updated:** 2026-08-06
