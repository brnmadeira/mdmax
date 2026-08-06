# Usage Examples

## CLI

### Basic Conversion

```bash
mdmax document.pdf
mdmax spreadsheet.xlsx
mdmax report.docx
```

### Batch Processing

```bash
mdmax *.pdf
mdmax ~/Documents/*.xlsx
```

### View Statistics

```bash
mdmax --stats
mdmax --stats --export json
```

### Server Mode

```bash
mdmax --server --port 8000
```

## Python API

```python
from mdmax import MdMax

converter = MdMax()

# Convert file
markdown = converter.convert("document.pdf")
print(markdown)

# Get statistics
stats = converter.get_stats()
print(f"Tokens saved: {stats['tokens_saved']}")
```

## Docker

```bash
# Build
docker build -t mdmax .

# Convert file
docker run -v $(pwd):/workspace mdmax document.pdf

# Server
docker run -p 8000:8000 mdmax --server
```
