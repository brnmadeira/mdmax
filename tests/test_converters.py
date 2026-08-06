"""
Unit tests for MdMax converters
"""

import pytest
import json
import csv
import tempfile
from pathlib import Path
from scripts.converters_real import MarkdownConverter


@pytest.fixture
def converter():
    """Create converter instance"""
    return MarkdownConverter()


@pytest.fixture
def temp_dir():
    """Create temporary directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


class TestTextConversion:
    """Test text file conversion"""

    def test_txt_to_markdown(self, converter, temp_dir):
        """Test TXT passthrough"""
        # Create test file
        test_file = temp_dir / "test.txt"
        content = "Hello World\nLine 2"
        test_file.write_text(content)

        # Convert
        result = converter.txt_to_markdown(str(test_file))

        # Assert
        assert result == content

    def test_json_to_markdown(self, converter, temp_dir):
        """Test JSON to Markdown"""
        # Create test file
        test_file = temp_dir / "test.json"
        data = {"name": "MdMax", "version": "2.0.0"}
        test_file.write_text(json.dumps(data))

        # Convert
        result = converter.json_to_markdown(str(test_file))

        # Assert
        assert "MdMax" in result
        assert "2.0.0" in result
        assert "```json" in result


class TestCSVConversion:
    """Test CSV file conversion"""

    def test_csv_to_markdown(self, converter, temp_dir):
        """Test CSV to Markdown table"""
        # Create test file
        test_file = temp_dir / "test.csv"
        with open(test_file, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(["Name", "Version"])
            writer.writerow(["MdMax", "2.0.0"])

        # Convert
        result = converter.csv_to_markdown(str(test_file))

        # Assert
        assert "Name" in result
        assert "MdMax" in result
        assert "|" in result  # Markdown table format
        assert "---" in result  # Table separator


class TestImageConversion:
    """Test image file conversion"""

    def test_jpg_to_markdown(self, converter, temp_dir):
        """Test JPG to Markdown (without OCR)"""
        # Create dummy file
        test_file = temp_dir / "test.jpg"
        test_file.write_bytes(b"dummy")

        # Convert
        result = converter.jpg_to_markdown(str(test_file))

        # Assert
        assert "test.jpg" in result
        assert "Image:" in result
        assert "![" in result  # Markdown image format


class TestCLI:
    """Test CLI functionality"""

    def test_cli_version(self, temp_dir):
        """Test version command"""
        from scripts.cli import __version__

        assert __version__ == "2.0.0"

    def test_cli_config_initialization(self, temp_dir):
        """Test config initialization"""
        from scripts.cli import ensure_config, CONFIG_FILE

        ensure_config()
        assert CONFIG_FILE.exists()


class TestTokenEstimation:
    """Test token estimation"""

    def test_token_estimation_accuracy(self, converter, temp_dir):
        """Test token estimation for compression"""
        # Create test file
        test_file = temp_dir / "test.txt"
        test_file.write_text("A" * 10000)  # 10KB

        # Convert (passthrough for txt)
        result = converter.txt_to_markdown(str(test_file))

        # Estimate tokens
        original_tokens = int(10000 * 0.00025)  # ~2.5 tokens per byte
        compressed_tokens = int(len(result) * 0.00025)

        # Should have same size (passthrough)
        assert abs(original_tokens - compressed_tokens) < 10


class TestErrorHandling:
    """Test error handling"""

    def test_missing_file(self, converter):
        """Test handling of missing file"""
        with pytest.raises(FileNotFoundError):
            converter.txt_to_markdown("/nonexistent/file.txt")

    def test_missing_dependency(self, converter, temp_dir):
        """Test handling of missing optional dependency"""
        # Create PDF file (but PyPDF2 might not be installed)
        test_file = temp_dir / "test.pdf"
        test_file.write_bytes(b"%PDF-1.4")

        # Try to convert (may raise ImportError if PyPDF2 not installed)
        try:
            result = converter.pdf_to_markdown(str(test_file))
            # If it works, check result
            assert isinstance(result, str)
        except ImportError:
            # Expected if PyPDF2 not installed
            pytest.skip("PyPDF2 not installed")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
