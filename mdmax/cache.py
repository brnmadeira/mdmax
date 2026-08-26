"""
MDMAX Cache System - Persistent deduplication via SQLite
Prevents reprocessing of identical files
"""

import sqlite3
import hashlib
from pathlib import Path
from typing import Optional, Tuple
from datetime import datetime


class CacheManager:
    """Manage conversion cache to prevent duplicates"""

    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or Path.home() / ".mdmax" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.cache_dir / "conversions.db"
        self._init_db()

    def _init_db(self):
        """Initialize SQLite database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_hash TEXT UNIQUE NOT NULL,
                    filename TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    format TEXT NOT NULL,
                    markdown_hash TEXT NOT NULL,
                    markdown_size INTEGER NOT NULL,
                    input_tokens INTEGER,
                    output_tokens INTEGER,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_file_hash ON conversions(file_hash)
            """)
            conn.commit()

    @staticmethod
    def _compute_file_hash(file_path: Path, chunk_size: int = 8192) -> str:
        """Compute SHA256 hash of file"""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(chunk_size):
                sha256.update(chunk)
        return sha256.hexdigest()

    def check_cache(self, file_path: Path) -> Optional[dict]:
        """
        Check if file was already processed
        Returns cached markdown info or None
        """
        file_hash = self._compute_file_hash(file_path)

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM conversions WHERE file_hash = ?",
                (file_hash,)
            )
            row = cursor.fetchone()

            if row:
                # Update accessed time
                conn.execute(
                    "UPDATE conversions SET accessed_at = CURRENT_TIMESTAMP WHERE file_hash = ?",
                    (file_hash,)
                )
                conn.commit()

                return {
                    "file_hash": row["file_hash"],
                    "filename": row["filename"],
                    "file_size": row["file_size"],
                    "format": row["format"],
                    "markdown_hash": row["markdown_hash"],
                    "markdown_size": row["markdown_size"],
                    "input_tokens": row["input_tokens"],
                    "output_tokens": row["output_tokens"],
                    "processed_at": row["processed_at"],
                    "accessed_at": row["accessed_at"],
                }

            return None

    def store_conversion(
        self,
        file_path: Path,
        markdown: str,
        input_tokens: int,
        output_tokens: int,
    ) -> str:
        """
        Store conversion in cache
        Returns file_hash
        """
        file_hash = self._compute_file_hash(file_path)
        markdown_hash = hashlib.sha256(markdown.encode()).hexdigest()

        with sqlite3.connect(self.db_path) as conn:
            try:
                conn.execute("""
                    INSERT INTO conversions
                    (file_hash, filename, file_size, format, markdown_hash, markdown_size, input_tokens, output_tokens)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    file_hash,
                    file_path.name,
                    file_path.stat().st_size,
                    file_path.suffix.lower(),
                    markdown_hash,
                    len(markdown.encode()),
                    input_tokens,
                    output_tokens,
                ))
                conn.commit()
            except sqlite3.IntegrityError:
                # Already exists, just update accessed time
                conn.execute(
                    "UPDATE conversions SET accessed_at = CURRENT_TIMESTAMP WHERE file_hash = ?",
                    (file_hash,)
                )
                conn.commit()

        return file_hash

    def get_stats(self) -> dict:
        """Get cache statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) as total FROM conversions")
            total = cursor.fetchone()[0]

            cursor = conn.execute("SELECT SUM(markdown_size) as total_size FROM conversions")
            total_size = cursor.fetchone()[0] or 0

            cursor = conn.execute("SELECT SUM(input_tokens) as total_input FROM conversions")
            total_input = cursor.fetchone()[0] or 0

            cursor = conn.execute("SELECT SUM(output_tokens) as total_output FROM conversions")
            total_output = cursor.fetchone()[0] or 0

        return {
            "cached_files": total,
            "cache_size_bytes": total_size,
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "total_saved_tokens": total_input - total_output,
        }

    def get_dashboard(self) -> str:
        """Format cache statistics"""
        stats = self.get_stats()

        lines = [
            "=" * 60,
            "MDMAX - Cache Statistics",
            "=" * 60,
            "",
            f"Cached Files:        {stats['cached_files']}",
            f"Cache Size:          {stats['cache_size_bytes']:,} bytes",
            f"Total Input Tokens:  {stats['total_input_tokens']:,}",
            f"Total Output Tokens: {stats['total_output_tokens']:,}",
            f"Saved via Cache:     {stats['total_saved_tokens']:,}",
            "",
            f"Cache Location: {self.db_path}",
        ]

        return "\n".join(lines)

    def clear_cache(self, older_than_days: Optional[int] = None):
        """Clear cache (optionally old entries only)"""
        with sqlite3.connect(self.db_path) as conn:
            if older_than_days:
                conn.execute(f"""
                    DELETE FROM conversions
                    WHERE accessed_at < datetime('now', '-{older_than_days} days')
                """)
            else:
                conn.execute("DELETE FROM conversions")
            conn.commit()

    def list_cached(self, limit: int = 50) -> list:
        """List cached conversions"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT filename, format, file_size, processed_at, accessed_at FROM conversions ORDER BY processed_at DESC LIMIT ?",
                (limit,)
            )
            return [dict(row) for row in cursor.fetchall()]
