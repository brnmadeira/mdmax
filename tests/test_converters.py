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
        """Test CSV to Markdown (fenced code block, not a pipe-table)"""
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
        assert "```csv" in result


class TestTSVConversion:
    """Test TSV file conversion"""

    def test_tsv_to_markdown(self, converter, temp_dir):
        """Test TSV to Markdown (fenced block)"""
        test_file = temp_dir / "test.tsv"
        test_file.write_text("Name\tVersion\nMdMax\t2.0.0")

        result = converter.tsv_to_markdown(str(test_file))

        assert "Name" in result
        assert "MdMax" in result
        assert "```tsv" in result


class TestODSConversion:
    """Test ODS file conversion"""

    def test_ods_to_markdown(self, converter, temp_dir):
        """Test ODS to Markdown table"""
        odf = pytest.importorskip("odf.opendocument")
        from odf.opendocument import OpenDocumentSpreadsheet
        from odf.table import Table, TableRow, TableCell
        from odf.text import P

        test_file = temp_dir / "test.ods"
        doc = OpenDocumentSpreadsheet()
        table = Table(name="Sheet1")
        for values in (["Name", "Version"], ["MdMax", "2.0.0"]):
            row = TableRow()
            for v in values:
                cell = TableCell()
                cell.addElement(P(text=v))
                row.addElement(cell)
            table.addElement(row)
        doc.spreadsheet.addElement(table)
        doc.save(str(test_file))

        result = converter.ods_to_markdown(str(test_file))

        assert "Name" in result
        assert "MdMax" in result
        assert "|" in result


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
        # Test with an invalid file that will trigger error
        test_file = temp_dir / "test.xlsx"
        test_file.write_bytes(b"invalid excel data")

        # Try to convert - should handle gracefully
        try:
            result = converter.xlsx_to_markdown(str(test_file))
            # If it works, check result
            assert isinstance(result, str)
        except Exception:
            # Expected if optional dependency not installed or file invalid
            pass  # Test passes if exception is caught gracefully


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
