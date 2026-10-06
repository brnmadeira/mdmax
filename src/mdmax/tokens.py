"""Token counting.

Two methods:

* ``estimate_tokens`` - offline and instant. Calibrated in October 2026 against real
  counts from the tokenizer used by Claude Opus 4.7 and later (code, shell output,
  English docs and Portuguese prose): about 2.2 characters per token, mean error ~8%.
  Older models produce fewer tokens for the same text, so for them it over-estimates.
* ``count_tokens_exact`` - the official ``count_tokens`` endpoint, through the
  ``anthropic`` SDK (``pip install "mdmax[exact]"``). Free, but needs API credentials
  and a network call, so it is only used when asked for (``--exact`` or
  ``MDMAX_EXACT_TOKENS=1``).

Savings percentages compare two texts measured the same way, so they are more
reliable than the absolute numbers.
"""

from __future__ import annotations

import base64
import math
import os
from pathlib import Path
from typing import Optional

CHARS_PER_TOKEN = 2.2

# When Claude reads a PDF directly, every page is also sent as an image
# (docs: "Because each page is converted into an image, the same image-based cost
# calculations are applied"). 1,568 visual tokens is the cap per image on the
# standard resolution tier; models from Claude 4.7 on go up to 4,784. We use the
# lower number so the savings we report are never inflated.
PDF_IMAGE_TOKENS_PER_PAGE = 1568

DEFAULT_MODEL = "claude-opus-5-5"


def estimate_tokens(text: str) -> int:
    if not text:
        return 0
    return math.ceil(len(text) / CHARS_PER_TOKEN)


def exact_enabled(flag: Optional[bool] = None) -> bool:
    if flag is not None:
        return flag
    return os.environ.get("MDMAX_EXACT_TOKENS", "").strip().lower() in ("1", "true", "yes", "on")


def _model() -> str:
    return os.environ.get("MDMAX_MODEL", "").strip() or DEFAULT_MODEL


def _client():
    try:
        from anthropic import Anthropic
    except ImportError as exc:  # pragma: no cover - depends on the environment
        raise RuntimeError('exact counting needs the SDK: pip install "mdmax[exact]"') from exc
    return Anthropic()


def count_tokens_exact(text: str) -> int:
    """Tokens of ``text`` as a user message, minus the empty-message overhead."""
    client = _client()
    model = _model()
    full = client.messages.count_tokens(
        model=model, messages=[{"role": "user", "content": text or " "}]
    ).input_tokens
    empty = client.messages.count_tokens(
        model=model, messages=[{"role": "user", "content": " "}]
    ).input_tokens
    return max(0, full - empty)


def count_pdf_tokens_exact(path: Path) -> int:
    """What Claude spends reading the PDF itself (text plus one image per page)."""
    client = _client()
    model = _model()
    data = base64.standard_b64encode(Path(path).read_bytes()).decode("ascii")
    full = client.messages.count_tokens(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {"type": "base64", "media_type": "application/pdf", "data": data},
                    },
                    {"type": "text", "text": " "},
                ],
            }
        ],
    ).input_tokens
    empty = client.messages.count_tokens(
        model=model, messages=[{"role": "user", "content": " "}]
    ).input_tokens
    return max(0, full - empty)
