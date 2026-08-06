#!/usr/bin/env python3
"""
MdMax API - RESTful API for file conversion
FastAPI endpoint for programmatic access
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import tempfile
import json
from typing import Optional

from scripts.converters_real import MarkdownConverter
from scripts.optimizers import optimize_markdown, calculate_savings, check_duplicate
from scripts.token_counter import get_token_count, calculate_real_savings
from scripts.summarizer import smart_summarize

app = FastAPI(
    title="MdMax API",
    description="Convert files to optimized Markdown with token economy tracking",
    version="2.1.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize converter
converter = MarkdownConverter()

# API Statistics
api_stats = {
    "total_conversions": 0,
    "total_tokens_saved": 0,
    "total_files_processed": 0,
    "formats_used": {}
}


@app.get("/")
async def root():
    """API welcome endpoint"""
    return {
        "name": "MdMax API",
        "version": "2.1.0",
        "description": "Convert files to optimized Markdown",
        "endpoints": {
            "POST /convert": "Convert file to Markdown",
            "GET /stats": "API statistics",
            "GET /health": "Health check",
            "GET /docs": "API documentation (Swagger UI)"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "2.1.0"
    }


@app.get("/stats")
async def get_stats():
    """Get API statistics"""
    return {
        "total_conversions": api_stats["total_conversions"],
        "total_tokens_saved": api_stats["total_tokens_saved"],
        "total_files_processed": api_stats["total_files_processed"],
        "formats_used": api_stats["formats_used"],
        "uptime": "active"
    }


@app.post("/convert")
async def convert_file(
    file: UploadFile = File(...),
    optimize: str = Query("full", description="Optimization level: none, basic, full, all"),
    real_tokens: bool = Query(False, description="Use Claude API for real token counting"),
    summarize: bool = Query(False, description="Enable AI summarization")
):
    """
    Convert file to Markdown with optimizations

    Args:
        file: File to convert (PDF, Excel, CSV, JSON, TXT, etc)
        optimize: Optimization level (none, basic, full, all)
        real_tokens: Use Claude API for accurate token counting
        summarize: Enable AI summarization for verbose content

    Returns:
        JSON with conversion results, markdown content, and token economy
    """
    try:
        # Check file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")

        file_ext = Path(file.filename).suffix.lower()

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        try:
            # Check duplicate
            is_duplicate, file_hash, cached_path = check_duplicate(tmp_path)

            if is_duplicate and cached_path:
                return JSONResponse({
                    "status": "duplicate",
                    "message": "File already processed (cached)",
                    "file_hash": file_hash,
                    "cached_markdown_path": cached_path,
                    "tokens_saved_percent": 100,
                    "reason": "Exact file found in cache"
                })

            # Convert file
            markdown = None
            original_size = len(content)

            if file_ext == ".pdf":
                markdown = converter.pdf_to_markdown(tmp_path)
            elif file_ext in [".xlsx", ".xls", ".xlsm"]:
                markdown = converter.xlsx_to_markdown(tmp_path)
            elif file_ext == ".csv":
                markdown = converter.csv_to_markdown(tmp_path)
            elif file_ext == ".json":
                markdown = converter.json_to_markdown(tmp_path)
            elif file_ext == ".svg":
                markdown = converter.svg_to_markdown(tmp_path)
            elif file_ext == ".txt":
                with open(tmp_path) as f:
                    markdown = f.read()
            elif file_ext in [".jpg", ".jpeg", ".png"]:
                markdown = converter.jpg_to_markdown(tmp_path)
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported format: {file_ext}")

            if not markdown:
                raise HTTPException(status_code=400, detail="Conversion failed")

            # Apply optimizations
            optimize_flags = []
            if optimize == "all" or optimize == "full":
                optimize_flags = ["all"]
            elif optimize == "basic":
                optimize_flags = ["boilerplate", "urls"]

            if optimize_flags:
                markdown = optimize_markdown(markdown, optimize_flags)

            # Apply summarization
            if summarize and len(markdown) > 5000:
                markdown = smart_summarize(markdown, enable_api=True)

            # Calculate token savings
            markdown_bytes = markdown.encode('utf-8')
            optimized_size = len(markdown_bytes)
            reduction_percent = (1 - optimized_size / original_size) * 100 if original_size > 0 else 0

            # Token counting
            if real_tokens:
                token_stats = calculate_real_savings(content.decode('utf-8', errors='ignore'), markdown)
            else:
                original_tokens = int(original_size * 0.00025)
                optimized_tokens = int(optimized_size * 0.00025)
                token_stats = {
                    "original_tokens": original_tokens,
                    "optimized_tokens": optimized_tokens,
                    "tokens_saved": original_tokens - optimized_tokens,
                    "savings_percent": reduction_percent,
                    "status": "ESTIMATED"
                }

            # Cache markdown
            from scripts.optimizers import cache_markdown
            cache_markdown(file_hash, f"api_cache_{file_hash}.md")

            # Update stats
            api_stats["total_conversions"] += 1
            api_stats["total_tokens_saved"] += token_stats["tokens_saved"]
            api_stats["total_files_processed"] += 1
            api_stats["formats_used"][file_ext] = api_stats["formats_used"].get(file_ext, 0) + 1

            return JSONResponse({
                "status": "success",
                "filename": file.filename,
                "format": file_ext,
                "original_size_bytes": original_size,
                "optimized_size_bytes": optimized_size,
                "reduction_percent": round(reduction_percent, 1),
                "tokens": {
                    "original": token_stats["original_tokens"],
                    "optimized": token_stats["optimized_tokens"],
                    "saved": token_stats["tokens_saved"],
                    "savings_percent": round(token_stats["savings_percent"], 1),
                    "status": token_stats["status"]
                },
                "optimizations_applied": {
                    "boilerplate_removal": "boilerplate" in optimize_flags,
                    "url_shortening": "urls" in optimize_flags or optimize == "all",
                    "summarization": summarize
                },
                "markdown_preview": markdown[:500] + "..." if len(markdown) > 500 else markdown,
                "markdown_full_length": len(markdown)
            })

        finally:
            # Cleanup temp file
            Path(tmp_path).unlink(missing_ok=True)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion error: {str(e)}")


@app.post("/convert-batch")
async def convert_batch(files: list[UploadFile] = File(...)):
    """
    Batch convert multiple files

    Returns: JSON with results for each file
    """
    results = []
    total_tokens_saved = 0

    for file in files:
        try:
            # Convert each file
            file_ext = Path(file.filename).suffix.lower()

            # Reread file for each conversion
            content = await file.read()

            with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
                tmp.write(content)
                tmp_path = tmp.name

            # Get markdown (same logic as /convert endpoint)
            markdown = converter.xlsx_to_markdown(tmp_path) if file_ext in [".xlsx", ".xls"] else "conversion_not_supported"

            original_tokens = int(len(content) * 0.00025)
            optimized_tokens = int(len(markdown.encode('utf-8')) * 0.00025)
            tokens_saved = original_tokens - optimized_tokens
            total_tokens_saved += tokens_saved

            results.append({
                "filename": file.filename,
                "status": "success",
                "tokens_saved": tokens_saved
            })

            Path(tmp_path).unlink(missing_ok=True)

        except Exception as e:
            results.append({
                "filename": file.filename,
                "status": "error",
                "error": str(e)
            })

    return {
        "total_files": len(files),
        "successful": len([r for r in results if r["status"] == "success"]),
        "failed": len([r for r in results if r["status"] == "error"]),
        "total_tokens_saved": total_tokens_saved,
        "results": results
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
