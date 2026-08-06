from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mdmax",
    version="2.0.0",
    author="MdMax Developer",
    author_email="brn.madeira@gmail.com",
    description="Compress files by 79.7% + track token economy with Claude",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/brnmadeira/mdmax",
    packages=["scripts"],
    package_dir={"": "."},
    py_modules=["scripts.cli"],
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
        "openpyxl>=3.0.0",
        "PyPDF2>=3.0.0",
    ],
    extras_require={
        "ocr": ["pytesseract>=0.3.10", "pillow>=9.0.0"],
        "epub": ["ebooklib>=0.18"],
        "docx": ["python-docx>=0.8.10"],
        "pptx": ["python-pptx>=0.6.20"],
        "xls": ["xlrd>=2.0.0"],
        "dev": ["pytest>=7.0.0", "pytest-cov>=3.0.0"],
        "all": [
            "pytesseract>=0.3.10",
            "pillow>=9.0.0",
            "ebooklib>=0.18",
            "python-docx>=0.8.10",
            "python-pptx>=0.6.20",
            "xlrd>=2.0.0",
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
        ],
    },
    keywords="markdown pdf excel spreadsheet conversion token economy claude",
)
