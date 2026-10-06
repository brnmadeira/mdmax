import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


@pytest.fixture(autouse=True)
def isolated_home(tmp_path, monkeypatch):
    """Every test gets its own mdmax data folder and an empty user home."""
    monkeypatch.setenv("MDMAX_HOME", str(tmp_path / "mdmax-home"))
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.setenv("USERPROFILE", str(tmp_path / "home"))
    monkeypatch.delenv("MDMAX_EXACT_TOKENS", raising=False)
    monkeypatch.delenv("MDMAX_HOOK", raising=False)
    monkeypatch.delenv("CLAUDE_PROJECT_DIR", raising=False)
    (tmp_path / "home").mkdir()
    yield
