# MDMAX Deduplication & Caching

**3 layers of protection against duplicate processing:**

1. **Persistent Cache** (SQLite) - Survives sessions
2. **Session Deduplication** (In-memory) - Current session
3. **Smart Batch Processing** - Intelligent batch handling

---

## Feature 1: Persistent Cache

Stores all conversions in SQLite database at `~/.mdmax/cache/conversions.db`

### Usage

```bash
# View cache statistics
mdmax cache --show

# List cached files
mdmax cache --list

# Clear all cache
mdmax cache --clear

# Clear files older than 30 days
mdmax cache --clear-old 30
```

### Cache Statistics

```
Cached Files:        42
Cache Size:          125,432,156 bytes
Total Input Tokens:  8,234,567
Total Output Tokens: 5,123,456
Saved via Cache:     3,111,111
```

### API Usage

```python
from mdmax.cache import CacheManager

# Initialize cache
cache = CacheManager()

# Check if file was cached
cached_info = cache.check_cache(Path("document.pdf"))
if cached_info:
    print(f"Already processed: {cached_info['processed_at']}")

# Store new conversion
cache.store_conversion(
    file_path=Path("document.pdf"),
    markdown="# Content...",
    input_tokens=1000,
    output_tokens=500
)

# Get statistics
stats = cache.get_stats()
print(f"Cached: {stats['cached_files']} files")

# Clear old entries
cache.clear_cache(older_than_days=30)
```

---

## Feature 2: Session Deduplication

In-memory duplicate detection during current session

### How It Works

```python
from mdmax.deduplication import DeduplicationEngine

dedup = DeduplicationEngine()

# Check if file was processed in this session
if dedup.is_duplicate(file_path):
    print("Already processed in this session")
else:
    # Process file
    result = convert(file_path)
    dedup.mark_processed(file_path)
```

### Use Case: Prevent Re-processing

```bash
# First run: processes all 100 PDFs
mdmax batch "*.pdf"

# Later in same script: detects duplicates, skips them
mdmax batch "*.pdf"  # Skips already-processed files
```

---

## Feature 3: Smart Batch Processing

Combines deduplication + caching for intelligent batch operations

### Usage

```python
from mdmax.deduplication import BatchDeduplicator
from pathlib import Path

batch = BatchDeduplicator()

files = list(Path(".").glob("*.pdf"))

def process_file(path):
    return convert(path)

results = batch.process_batch(
    files=files,
    processor_func=process_file,
    skip_duplicates=True,
    verbose=True
)

# Get report
report = batch.get_report()
print(report)
# Output:
# {
#     'files_processed': 95,
#     'duplicates_skipped': 5,
#     'total_attempted': 100,
#     'dedup_rate': '5.0%'
# }
```

### Batch Processing with CLI

```bash
# Process batch (uses cache automatically)
mdmax batch "reports/*.pdf" -o markdown/

# Second run skips cached files
mdmax batch "reports/*.pdf" -o markdown/
# Output: Processed: 0, Skipped (cached): 42
```

---

## How They Work Together

### Scenario: Processing 1000 files across multiple sessions

**Session 1:**
```bash
mdmax batch "*.pdf"  # Processes 1000 files
# Stores in: ~/.mdmax/cache/conversions.db
# Time: 2 hours
```

**Session 2 (next day):**
```bash
mdmax batch "*.pdf"  # 1000 cached, 50 new
# Skips 1000 (cache hit)
# Processes 50 new
# Time: 5 minutes (50 × 3 seconds each)
```

---

## Configuration

### Enable/Disable Cache

```python
# Enable cache (default)
converter = MdMax(use_cache=True)

# Disable cache
converter = MdMax(use_cache=False)
```

### Cache Location

Default: `~/.mdmax/cache/conversions.db`

Custom location:
```python
from pathlib import Path
cache = CacheManager(cache_dir=Path("/custom/path"))
```

---

## Performance Impact

### Measurements (50MB PDF)

| Scenario | Time | Tokens |
|----------|------|--------|
| First conversion | 3.2s | 2,850 |
| Cache hit | 0.001s | 0 |
| Savings | 99.97% | 100% |

### Batch Processing (100 PDFs)

| Run | Mode | Time | Status |
|-----|------|------|--------|
| 1 | Convert all | 5 min | 100 new |
| 2 | With cache | 0.1 sec | 100 skipped |
| 3 | Add 10 new | 30 sec | 100 cached, 10 new |

---

## Hash-Based Matching

All deduplication uses **SHA256 hashing:**

```python
# Files are matched by content, not filename
file_hash = SHA256(file_bytes)
if file_hash in database:
    return cached_result
```

### Implications

- ✅ Same file, different names → detected as duplicate
- ✅ File moved to different folder → still detected
- ✅ File content unchanged → cached
- ✅ File renamed → still recognized

### Example

```
folder1/report.pdf (hash: abc123)
folder2/report_copy.pdf (hash: abc123)  ← Detected as same file

mdmax batch "folder1/*.pdf" "folder2/*.pdf"
# Processes report.pdf once, skips report_copy.pdf
```

---

## Troubleshooting

### Cache takes too much space

```bash
# Clear cache
mdmax cache --clear

# Or keep only recent:
mdmax cache --clear-old 7  # Keep only last 7 days
```

### Cache seems stale

```bash
# Check last access time
mdmax cache --list

# Force re-process (skip cache)
mdmax convert file.pdf --no-cache
```

### Cache file corrupted

```bash
# Remove database
rm ~/.mdmax/cache/conversions.db

# It will be recreated on next use
mdmax convert file.pdf
```

---

## Statistics & Analytics

### View cache stats

```bash
mdmax cache --show
```

### Export cache data

```python
from mdmax.cache import CacheManager

cache = CacheManager()
stats = cache.get_stats()

# Annual projection
annual_tokens = stats['total_saved_tokens'] * 365
annual_cost = annual_tokens * 0.00015  # Claude API rate
print(f"Annual savings: ${annual_cost:.2f}")
```

### Analyze over time

```bash
# Cache log (JSONL format)
cat ~/.mdmax/cache/conversions.db  # SQLite (binary)

# Export to CSV for analysis
sqlite3 ~/.mdmax/cache/conversions.db \
  "SELECT * FROM conversions" | \
  csv > cache_report.csv
```

---

## Best Practices

### ✅ DO

- ✅ Use cache for repeated batches
- ✅ Clear old entries periodically (`cache --clear-old 30`)
- ✅ Check cache stats before large batch (`cache --show`)
- ✅ Monitor annual savings projections

### ❌ DON'T

- ❌ Manually edit cache database
- ❌ Move cache directory without copying DB
- ❌ Disable cache for large batches
- ❌ Trust cache after file content changes

---

## Version History

- **v3.1.0** - Cache + Deduplication added
- **v3.0.0** - Token economy tracking
- **v2.2.0** - Initial release
