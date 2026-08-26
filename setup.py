#!/usr/bin/env python3
"""
MDMAX - Universal Document to Markdown Converter
Wraps anydoc (Firecrawl) with token economy tracking and unified interface
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mdmax",
    version="3.0.0",
    author="brn.madeira@gmail.com",
    author_email="brn.madeira@gmail.com",
    description="Convert any document format to optimized Markdown with token economy tracking",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/brnmadeira/mdmax",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8+",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Office/Business",
        "Topic :: Text Processing :: Markup",
    ],
    python_requires=">=3.8",
    install_requires=[
        "firecrawl-anydoc>=0.1.0",  # Core converter (Rust-backed)
        "click>=8.0",               # CLI framework
        "tqdm>=4.65",               # Progress bars
        "tabulate>=0.9",            # Pretty tables
        "pydantic>=2.0",            # Data validation
        "httpx>=0.24",              # HTTP client (for API)
    ],
    extras_require={
        "ocr": ["pytesseract>=0.3.10"],  # OCR for image fallback
        "dev": ["pytest>=7.0", "black>=23.0", "mypy>=1.0"],
        "api": ["fastapi>=0.100", "uvicorn>=0.23"],
    },
    entry_points={
        "console_scripts": [
            "mdmax=mdmax.cli:main",
        ],
    },
    include_package_data=True,
)
