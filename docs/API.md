# API Documentation

## REST API

Start the server:

```bash
mdmax --server
```

Default: `http://localhost:8000`

## Endpoints

### POST /convert

Convert a file to markdown.

**Request:**
```bash
curl -X POST -F "file=@document.pdf" http://localhost:8000/convert
```

**Response:**
```json
{
  "markdown": "# Document Title\n...",
  "tokens": 285,
  "compression": "90%"
}
```

### GET /health

Check server status.

```bash
curl http://localhost:8000/health
```
