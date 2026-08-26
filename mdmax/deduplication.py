"""
MDMAX Deduplication - In-memory duplicate detection
Prevents processing the same file multiple times in one session
"""

import hashlib
from pathlib import Path
from typing import Optional, Dict, Set


class DeduplicationEngine:
    """In-memory deduplication for current session"""

    def __init__(self):
        self.processed_hashes: Set[str] = set()
        self.file_map: Dict[str, dict] = {}  # hash -> file info

    @staticmethod
    def compute_hash(file_path: Path) -> str:
        """Compute file hash for deduplication"""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        return sha256.hexdigest()

    def is_duplicate(self, file_path: Path) -> bool:
        """Check if file was already processed in this session"""
        file_hash = self.compute_hash(file_path)
        return file_hash in self.processed_hashes

    def mark_processed(self, file_path: Path, metadata: Optional[dict] = None):
        """Mark file as processed"""
        file_hash = self.compute_hash(file_path)
        self.processed_hashes.add(file_hash)

        self.file_map[file_hash] = {
            "path": str(file_path),
            "filename": file_path.name,
            "size": file_path.stat().st_size,
            "format": file_path.suffix.lower(),
            **(metadata or {}),
        }

    def get_duplicate_info(self, file_path: Path) -> Optional[dict]:
        """Get info about duplicate file"""
        file_hash = self.compute_hash(file_path)
        return self.file_map.get(file_hash)

    def get_stats(self) -> dict:
        """Get deduplication statistics"""
        return {
            "unique_files": len(self.processed_hashes),
            "duplicates_blocked": 0,  # Would be set by caller
            "total_files_map": len(self.file_map),
        }

    def reset(self):
        """Clear session cache"""
        self.processed_hashes.clear()
        self.file_map.clear()


class BatchDeduplicator:
    """Smart batch processing with deduplication"""

    def __init__(self):
        self.session_dedup = DeduplicationEngine()
        self.duplicates_found: int = 0
        self.files_processed: int = 0

    def process_batch(
        self,
        files: list,
        processor_func,
        skip_duplicates: bool = True,
        verbose: bool = False,
    ) -> list:
        """
        Process batch of files with deduplication

        Args:
            files: List of file paths
            processor_func: Function to process each file (takes Path, returns result)
            skip_duplicates: Skip duplicate files
            verbose: Print duplicate info

        Returns:
            List of (file_path, result, is_duplicate) tuples
        """
        results = []

        for file_path in files:
            file_path = Path(file_path)

            # Check for duplicates
            if self.session_dedup.is_duplicate(file_path):
                self.duplicates_found += 1
                if verbose:
                    dup_info = self.session_dedup.get_duplicate_info(file_path)
                    print(f"  [SKIP] {file_path.name} (duplicate of {dup_info.get('filename')})")

                if skip_duplicates:
                    results.append((file_path, None, True))
                    continue

            # Process file
            try:
                result = processor_func(file_path)
                self.files_processed += 1
                self.session_dedup.mark_processed(file_path, {"result": result})
                results.append((file_path, result, False))

                if verbose:
                    print(f"  [DONE] {file_path.name}")

            except Exception as e:
                if verbose:
                    print(f"  [ERROR] {file_path.name}: {e}")
                results.append((file_path, str(e), False))

        return results

    def get_report(self) -> dict:
        """Get batch processing report"""
        return {
            "files_processed": self.files_processed,
            "duplicates_skipped": self.duplicates_found,
            "total_attempted": self.files_processed + self.duplicates_found,
            "dedup_rate": f"{(self.duplicates_found / max(1, self.files_processed + self.duplicates_found) * 100):.1f}%",
        }
