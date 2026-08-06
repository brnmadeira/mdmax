#!/usr/bin/env python3
"""
MdMax Incremental Processor - Smart caching and change tracking
Feature [4] of v2.2: Only reprocess changed files, massive token savings
"""

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple
import os


class IncrementalProcessor:
    """Process files incrementally, only reprocessing changes"""

    def __init__(self, cache_dir: Path = None):
        self.cache_dir = cache_dir or Path.home() / '.mdmax' / 'cache'
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.index_file = self.cache_dir / 'index.json'
        self.changelog_file = self.cache_dir / 'changelog.json'

        self._load_index()
        self._load_changelog()

    def _load_index(self):
        """Load file index from cache"""
        if self.index_file.exists():
            self.index = json.loads(self.index_file.read_text())
        else:
            self.index = {}

    def _load_changelog(self):
        """Load changelog from cache"""
        if self.changelog_file.exists():
            self.changelog = json.loads(self.changelog_file.read_text())
        else:
            self.changelog = {}

    def _save_index(self):
        """Save index to cache"""
        self.index_file.write_text(json.dumps(self.index, indent=2))

    def _save_changelog(self):
        """Save changelog to cache"""
        self.changelog_file.write_text(json.dumps(self.changelog, indent=2))

    def get_file_hash(self, file_path: str) -> str:
        """Calculate SHA256 hash of file"""
        sha256 = hashlib.sha256()

        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)

        return sha256.hexdigest()

    def get_file_size(self, file_path: str) -> int:
        """Get file size in bytes"""
        return os.path.getsize(file_path)

    def is_file_changed(self, file_path: str) -> bool:
        """Check if file has changed since last processing"""
        file_path_str = str(file_path)

        if file_path_str not in self.index:
            return True  # New file

        current_hash = self.get_file_hash(file_path)
        cached_hash = self.index[file_path_str].get('hash')

        return current_hash != cached_hash

    def track_file(self, file_path: str, markdown_output: str, tokens_saved: int):
        """Track file and its processing"""
        file_path_str = str(file_path)

        file_hash = self.get_file_hash(file_path)
        file_size = self.get_file_size(file_path)

        self.index[file_path_str] = {
            'hash': file_hash,
            'size': file_size,
            'timestamp': datetime.now().isoformat(),
            'output_size': len(markdown_output),
            'tokens_saved': tokens_saved,
        }

        # Record in changelog
        if file_path_str not in self.changelog:
            self.changelog[file_path_str] = []

        self.changelog[file_path_str].append({
            'timestamp': datetime.now().isoformat(),
            'hash': file_hash,
            'tokens_saved': tokens_saved,
            'change_type': 'new' if len(self.changelog[file_path_str]) == 0 else 'update',
        })

        self._save_index()
        self._save_changelog()

    def get_processing_status(self, file_path: str) -> Dict:
        """Get processing status of file"""
        file_path_str = str(file_path)

        if file_path_str not in self.index:
            return {
                'status': 'new',
                'needs_processing': True,
                'message': 'File not in cache - needs full processing',
            }

        cached_info = self.index[file_path_str]
        current_hash = self.get_file_hash(file_path)

        if current_hash == cached_info['hash']:
            return {
                'status': 'unchanged',
                'needs_processing': False,
                'tokens_saved': cached_info['tokens_saved'],
                'message': 'File unchanged - no processing needed',
            }
        else:
            return {
                'status': 'changed',
                'needs_processing': True,
                'previous_hash': cached_info['hash'],
                'current_hash': current_hash,
                'message': 'File changed - full reprocessing needed',
            }

    def get_delta_processing(self, file_path: str) -> Optional[Dict]:
        """Get info for delta processing (only changed parts)"""
        # For text files, could extract diffs
        # For now, returns None (full reprocessing needed)
        return None

    def estimate_processing_savings(self, file_paths: list) -> Dict:
        """Estimate token savings from cache"""
        stats = {
            'total_files': len(file_paths),
            'files_to_process': 0,
            'files_cached': 0,
            'estimated_tokens_saved': 0,
        }

        for file_path in file_paths:
            status = self.get_processing_status(str(file_path))

            if status['needs_processing']:
                stats['files_to_process'] += 1
            else:
                stats['files_cached'] += 1
                stats['estimated_tokens_saved'] += status['tokens_saved']

        return stats

    def get_version_history(self, file_path: str) -> list:
        """Get version history of file"""
        file_path_str = str(file_path)

        if file_path_str not in self.changelog:
            return []

        return self.changelog[file_path_str]

    def generate_version_report(self, file_path: str) -> str:
        """Generate version report for file"""
        file_path_str = str(file_path)
        history = self.get_version_history(file_path)

        if not history:
            return f"# Version History for {Path(file_path).name}\n\nNo history available."

        report = f"# Version History for {Path(file_path).name}\n\n"
        report += "| Version | Date | Change Type | Tokens Saved |\n"
        report += "|---------|------|-------------|---------------|\n"

        for i, entry in enumerate(history, 1):
            date = datetime.fromisoformat(entry['timestamp']).strftime('%Y-%m-%d %H:%M')
            report += f"| {i} | {date} | {entry['change_type']} | {entry['tokens_saved']:,} |\n"

        # Summary
        total_tokens = sum(e['tokens_saved'] for e in history)
        report += f"\n**Total tokens saved: {total_tokens:,}**\n"

        return report

    def cleanup_old_cache(self, days: int = 7):
        """Clean up cache older than N days"""
        cutoff = datetime.now().timestamp() - (days * 24 * 3600)

        removed_count = 0

        for file_path_str in list(self.index.keys()):
            timestamp_str = self.index[file_path_str].get('timestamp')

            if timestamp_str:
                timestamp = datetime.fromisoformat(timestamp_str).timestamp()

                if timestamp < cutoff:
                    del self.index[file_path_str]
                    if file_path_str in self.changelog:
                        del self.changelog[file_path_str]
                    removed_count += 1

        self._save_index()
        self._save_changelog()

        return removed_count

    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        total_tokens_saved = 0
        total_files = len(self.index)
        total_size = 0

        for info in self.index.values():
            total_tokens_saved += info.get('tokens_saved', 0)
            total_size += info.get('size', 0)

        return {
            'cached_files': total_files,
            'total_tokens_saved': total_tokens_saved,
            'total_data_processed': total_size,
            'cache_size_mb': sum(
                os.path.getsize(f)
                for f in self.cache_dir.glob('**/*')
                if f.is_file()
            ) / 1024 / 1024,
        }

    def export_statistics(self, output_file: str):
        """Export cache statistics to file"""
        stats = self.get_cache_stats()
        Path(output_file).write_text(json.dumps(stats, indent=2))


if __name__ == '__main__':
    processor = IncrementalProcessor()

    # Example usage
    print("Cache Statistics:")
    stats = processor.get_cache_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
