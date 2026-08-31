from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mdmax",
    version="2.2.0",
    author="Bruno Madeira",
    author_email="brn.madeira@gmail.com",
    description="Compress files by ~80% and save tokens with Claude",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/brnmadeira/mdmax",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "mdmax=scripts.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "setuptools>=60.0.0",
        "wheel>=0.35.0",
        "PyPDF2>=3.0.0",
        "openpyxl>=3.0.0",
        "python-docx>=0.8.10",
        "python-pptx>=0.6.20",
        "xlrd>=2.0.0",
        "requests>=2.25.0",
    ],
    extras_require={
        "api": [
            "fastapi>=0.90.0",
            "uvicorn>=0.20.0",
            "pydantic>=1.10.0",
        ],
        "epub": [
            "ebooklib>=0.18.0",
        ],
        "ods": [
            "odfpy>=1.4.0",
        ],
        "ocr": [
            "Pillow>=9.0.0",
        ],
        "all": [
            "fastapi>=0.90.0",
            "uvicorn>=0.20.0",
            "pydantic>=1.10.0",
            "ebooklib>=0.18.0",
            "odfpy>=1.4.0",
            "Pillow>=9.0.0",
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "flake8>=5.0.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
        ],
    },
    keywords="markdown pdf excel spreadsheet conversion token economy claude",
)
