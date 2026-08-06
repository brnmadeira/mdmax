# MdMax API v2.1 - Enterprise REST API

## Quick Start

### Start API Server
```bash
pip install -e ".[all]"
python -m scripts.api
```

API will be available at: `http://localhost:8000`

### Start Dashboard
```bash
python -m scripts.dashboard_web
```

Dashboard will be available at: `http://localhost:8001`

---

## API Endpoints

### Health Check
```bash
GET /health

Response:
{
  "status": "healthy",
  "version": "2.1.0"
}
```

### Convert Single File
```bash
POST /convert
Content-Type: multipart/form-data

Parameters:
  - file: (required) File to convert
  - optimize: [none|basic|full|all] (default: full)
  - real_tokens: true/false (default: false)
  - summarize: true/false (default: false)

Example:
curl -X POST "http://localhost:8000/convert" \
  -F "file=@products.xlsx" \
  -F "optimize=full" \
  -F "real_tokens=false"

Response:
{
  "status": "success",
  "filename": "products.xlsx",
  "format": ".xlsx",
  "original_size_bytes": 4631473,
  "optimized_size_bytes": 1279429,
  "reduction_percent": 72.4,
  "tokens": {
    "original": 1158,
    "optimized": 320,
    "saved": 838,
    "savings_percent": 72.4,
    "status": "ESTIMATED"
  },
  "optimizations_applied": {
    "boilerplate_removal": true,
    "url_shortening": true,
    "summarization": false
  },
  "markdown_preview": "## Sheet: Pedido\n\n| | | | Premium | ... (truncated)",
  "markdown_full_length": 1249401
}
```

### Convert Batch
```bash
POST /convert-batch
Content-Type: multipart/form-data

Parameters:
  - files: (required) Multiple files to convert

Example:
curl -X POST "http://localhost:8000/convert-batch" \
  -F "files=@file1.xlsx" \
  -F "files=@file2.xlsx" \
  -F "files=@file3.csv"

Response:
{
  "total_files": 3,
  "successful": 3,
  "failed": 0,
  "total_tokens_saved": 2500,
  "results": [
    {
      "filename": "file1.xlsx",
      "status": "success",
      "tokens_saved": 821
    },
    {
      "filename": "file2.xlsx",
      "status": "success",
      "tokens_saved": 838
    },
    {
      "filename": "file3.csv",
      "status": "success",
      "tokens_saved": 841
    }
  ]
}
```

### Get Statistics
```bash
GET /stats

Response:
{
  "total_conversions": 15,
  "total_tokens_saved": 12500,
  "total_files_processed": 15,
  "formats_used": {
    ".xlsx": 5,
    ".csv": 4,
    ".pdf": 3,
    ".json": 2,
    ".txt": 1
  },
  "uptime": "active"
}
```

---

## Python Client Library

### Basic Usage
```python
import requests

api_url = "http://localhost:8000"

# Convert single file
with open("data.xlsx", "rb") as f:
    files = {"file": f}
    params = {"optimize": "full", "real_tokens": False}
    response = requests.post(f"{api_url}/convert", files=files, params=params)
    result = response.json()
    
    print(f"Status: {result['status']}")
    print(f"Tokens saved: {result['tokens']['saved']}")
```

### Batch Processing
```python
import requests

files = [
    ("files", open("file1.xlsx", "rb")),
    ("files", open("file2.xlsx", "rb")),
    ("files", open("file3.csv", "rb")),
]

response = requests.post("http://localhost:8000/convert-batch", files=files)
result = response.json()

print(f"Total saved: {result['total_tokens_saved']} tokens")
```

---

## Integration Examples

### JavaScript/Node.js
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('optimize', 'full');
formData.append('real_tokens', false);

const response = await fetch('http://localhost:8000/convert', {
  method: 'POST',
  body: formData
});

const result = await response.json();
console.log(`Tokens saved: ${result.tokens.saved}`);
```

### cURL
```bash
# Convert file with optimization
curl -X POST "http://localhost:8000/convert" \
  -F "file=@report.xlsx" \
  -F "optimize=full" \
  -F "real_tokens=true" | jq '.'

# Get API stats
curl http://localhost:8000/stats | jq '.'

# API docs (Swagger UI)
curl http://localhost:8000/docs
```

---

## Supported Formats

| Format | Extension | Status |
|--------|-----------|--------|
| PDF    | .pdf      | ✅ Full support with OCR |
| Excel  | .xlsx     | ✅ Tables with optimization |
| Excel  | .xls      | ✅ Legacy format |
| CSV    | .csv      | ✅ Markdown tables |
| JSON   | .json     | ✅ Code blocks |
| Text   | .txt      | ✅ Passthrough |
| Word   | .docx     | ✅ Content extraction |
| PowerPoint | .pptx  | ✅ Slide content |
| EPUB   | .epub     | ✅ E-book extraction |
| SVG    | .svg      | ✅ Code blocks |
| Image  | .jpg/.png | ✅ With optional OCR |

---

## Performance Benchmarks

### File Conversion Speed
- Small files (<1MB): <500ms
- Medium files (1-10MB): <2s
- Large files (>10MB): <5s

### Token Economy
- Average savings: 72% across formats
- Best case (PDFs): 90%
- Duplicate files: 100%

### API Response Time
- Single file: <1s (average)
- Batch (10 files): <10s
- 99th percentile: <5s

---

## Configuration

### Environment Variables
```bash
# API Settings
API_HOST=0.0.0.0
API_PORT=8000

# Dashboard Settings
DASHBOARD_HOST=0.0.0.0
DASHBOARD_PORT=8001

# Claude API (for real token counting)
ANTHROPIC_API_KEY=your-api-key-here

# File upload limits
MAX_FILE_SIZE=100MB
```

---

## Security

### Authentication (Optional)
For production deployments, add authentication:

```python
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.post("/convert")
async def convert_file(credentials: HTTPAuthCredentials = Depends(security)):
    # Verify token
    pass
```

### Rate Limiting
Use a reverse proxy (nginx, Cloudflare) for rate limiting.

### CORS
CORS is enabled for `*` origins. Restrict in production:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)
```

---

## Docker Deployment

```bash
# Build Docker image
docker build -t mdmax-api:latest .

# Run API server
docker run -p 8000:8000 mdmax-api:latest

# Run with environment variables
docker run \
  -p 8000:8000 \
  -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
  mdmax-api:latest
```

---

## Troubleshooting

### API won't start
```bash
# Check port availability
lsof -i :8000

# Check Python dependencies
pip install -e ".[all]"
```

### Conversion fails
- Ensure file format is supported
- Check file permissions
- Verify system dependencies (Tesseract for OCR, etc)

### Token counting inaccurate
- Enable `real_tokens=true` for Claude API integration
- Requires `ANTHROPIC_API_KEY` environment variable

---

## Future Enhancements

- [ ] WebSocket support for real-time conversion progress
- [ ] Multi-user authentication and quotas
- [ ] Advanced caching strategies
- [ ] GPU acceleration for OCR
- [ ] Webhook callbacks for batch processing
- [ ] GraphQL API alternative

---

## Support & Documentation

- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **GitHub**: https://github.com/brnmadeira/mdmax
- **Issues**: https://github.com/brnmadeira/mdmax/issues
