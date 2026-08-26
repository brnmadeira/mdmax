"""
MDMAX - Universal Document to Markdown Converter
Wraps anydoc (Firecrawl) with token economy tracking + caching

Version: 3.1.0
Author: brn.madeira@gmail.com
License: MIT
"""

__version__ = "3.1.0"
__author__ = "brn.madeira@gmail.com"

from .converter import MdMax, convert, convert_bytes
from .economy import TokenEconomy, estimate_tokens
from .cache import CacheManager
from .deduplication import DeduplicationEngine, BatchDeduplicator

__all__ = [
    "MdMax",
    "convert",
    "convert_bytes",
    "TokenEconomy",
    "estimate_tokens",
    "CacheManager",
    "DeduplicationEngine",
    "BatchDeduplicator",
]
