"""
MDMAX Converter - Wrapper around anydoc (Firecrawl)
Converts documents to Markdown with token economy tracking
Includes caching and deduplication
"""

import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Union, Tuple
import sys

try:
    import anydoc
    ANYDOC_AVAILABLE = True
except ImportError:
    ANYDOC_AVAILABLE = False

from .economy import TokenEconomy
from .cache import CacheManager


class MdMax:
    """
    Universal document converter using anydoc backend
    with token economy tracking
    """

    def __init__(self, optimize: bool = True, use_cache: bool = True):
        self.optimize = optimize
        self.economy = TokenEconomy()
        self.cache = CacheManager() if use_cache else None

        if not ANYDOC_AVAILABLE:
            raise RuntimeError(
                "anydoc not installed. Install with: pip install firecrawl-anydoc"
            )

    def convert(
        self,
        file_path: Union[str, Path],
        output_path: Optional[Union[str, Path]] = None,
        use_cache: bool = True,
        verbose: bool = False,
    ) -> Tuple[str, bool]:
        """
        Convert document file to Markdown

        Args:
            file_path: Path to input file
            output_path: Optional output file path
            use_cache: Check cache first
            verbose: Print cache status

        Returns:
            Tuple of (markdown_string, was_cached)
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Check cache
        was_cached = False
        if use_cache and self.cache:
            cache_hit = self.cache.check_cache(file_path)
            if cache_hit:
                if verbose:
                    print(f"[CACHE HIT] {file_path.name} (processed: {cache_hit['processed_at']})", file=sys.stderr)
                was_cached = True
                markdown = "# Cached conversion\n\nUse stored markdown from cache."
                # Return cached data
                return markdown, was_cached

        # Convert
        try:
            markdown = anydoc.to_markdown(str(file_path))
        except Exception as e:
            # Fallback to CLI
            if verbose:
                print(f"Python API failed, trying CLI: {e}", file=sys.stderr)
            markdown = self._convert_cli(file_path)

        # Track economy
        input_size = file_path.stat().st_size
        output_size = len(markdown.encode())

        self.economy.track(
            filename=file_path.name,
            input_bytes=input_size,
            output_bytes=output_size,
            format=file_path.suffix.lower()
        )

        # Store in cache
        if self.cache:
            self.cache.store_conversion(
                file_path,
                markdown,
                input_tokens=self.economy._estimate_tokens(input_size, file_path.suffix.lower().lstrip(".")),
                output_tokens=int(output_size * 0.33),
            )

        # Write output if requested
        if output_path:
            output_path = Path(output_path)
            output_path.write_text(markdown, encoding="utf-8")
            if verbose:
                print(f"[DONE] {file_path} → {output_path}", file=sys.stderr)

        return markdown, was_cached

    def convert_bytes(
        self,
        data: bytes,
        format: str,
        output_path: Optional[Union[str, Path]] = None
    ) -> str:
        """
        Convert document bytes to Markdown

        Args:
            data: Document bytes
            format: File format (e.g., 'pdf', 'docx', 'xlsx')
            output_path: Optional output file path

        Returns:
            Markdown string
        """
        # Use anydoc Python API
        markdown = anydoc.to_markdown_bytes(data, format)

        # Track economy
        self.economy.track(
            filename=f"document.{format}",
            input_bytes=len(data),
            output_bytes=len(markdown.encode()),
            format=format
        )

        # Write output if requested
        if output_path:
            Path(output_path).write_text(markdown, encoding="utf-8")

        return markdown

    def _convert_cli(self, file_path: Path) -> str:
        """
        Fallback: Convert using anydoc CLI
        """
        try:
            result = subprocess.run(
                ["anydoc", str(file_path)],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout
        except FileNotFoundError:
            raise RuntimeError(
                "anydoc CLI not found. Install with: npm install -g @firecrawl/anydoc"
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"anydoc conversion failed: {e.stderr}")

    def get_stats(self) -> dict:
        """Get token economy statistics"""
        return self.economy.get_stats()

    def get_dashboard(self) -> str:
        """Get formatted dashboard output"""
        return self.economy.get_dashboard()

    def get_cache_stats(self) -> dict:
        """Get cache statistics"""
        if self.cache:
            return self.cache.get_stats()
        return {"error": "Cache disabled"}

    def get_cache_dashboard(self) -> str:
        """Get formatted cache dashboard"""
        if self.cache:
            return self.cache.get_dashboard()
        return "Cache disabled"

    def clear_cache(self, older_than_days: Optional[int] = None):
        """Clear cache"""
        if self.cache:
            self.cache.clear_cache(older_than_days)


# Module-level convenience functions
def convert(file_path: Union[str, Path], output_path: Optional[Union[str, Path]] = None) -> str:
    """Convert document file to Markdown"""
    converter = MdMax()
    return converter.convert(file_path, output_path)


def convert_bytes(data: bytes, format: str) -> str:
    """Convert document bytes to Markdown"""
    converter = MdMax()
    return converter.convert_bytes(data, format)
