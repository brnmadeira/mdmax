# Architecture

## Core Components

### Converters
- **converters.py**: Multi-format conversion (PDF, Excel, DOCX, etc.)
- Supports 16 formats
- Extensible converter pattern

### Optimizers
- **optimizers.py**: 7 compression methods
  1. Boilerplate removal
  2. Metadata stripping
  3. Whitespace optimization
  4. URL compression
  5. Code minification
  6. Duplicate detection
  7. Incremental caching

### CLI
- **cli.py**: Command-line interface
- Entry point for all operations

### Dashboard
- **dashboard.py**: Token economy visualization
- Real-time statistics
- Export to JSON/CSV

## Data Flow

```
File Input
    ↓
Converter (format detection)
    ↓
Optimizers (compression)
    ↓
Markdown Output
    ↓
Dashboard (token tracking)
```

## Extensibility

Add a new format:
1. Create converter method in `converters.py`
2. Register in `config.json`
3. Add tests in `tests/`
