"""One module per family of formats. Each converter returns a ``Converted``."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Converted:
    text: str
    # What Claude would spend without mdmax, when there is a fair comparison point.
    baseline_text: Optional[str] = None
    baseline_tokens: Optional[int] = None
    baseline_kind: str = "none"
    pages: Optional[int] = None
    warnings: List[str] = field(default_factory=list)
