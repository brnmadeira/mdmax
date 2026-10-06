"""Claude Code hook, MCP server, CLI, savings log and the skill launcher."""

import json
import os
import subprocess
import sys
from pathlib import Path

from fixtures import make_docx, make_pdf
from mdmax import hook, storage
from mdmax.cli import main as cli_main

ROOT = Path(__file__).resolve().parents[1]


def _event(path, tmp_path, **extra):
    event = {
        "hook_event_name": "PreToolUse",
        "tool_name": "Read",
        "tool_input": {"file_path": str(path)},
        "session_id": "s1",
        "cwd": str(tmp_path),
    }
    event.update(extra)
    return event


def _doc(tmp_path):
    return make_docx(tmp_path / "relatorio.docx", [("h", 1, "Título"), ("p", "Conteúdo do relatório.")])


# --------------------------------------------------------------------------- hook

def test_hook_redirects_read_to_converted_copy(tmp_path):
    doc = _doc(tmp_path)
    scratch = tmp_path / "scratch"
    out = hook.handle(_event(doc, tmp_path, scratchpad_dir=str(scratch)))
    spec = out["hookSpecificOutput"]
    new_path = Path(spec["updatedInput"]["file_path"])
    assert new_path.parent == scratch / "mdmax"
    assert "# Título" in new_path.read_text(encoding="utf-8")
    assert "permissionDecision" not in spec  # scratchpad needs no extra permission
    assert "mdmax" in spec["additionalContext"]


def test_hook_second_read_gets_the_original(tmp_path):
    doc = _doc(tmp_path)
    assert hook.handle(_event(doc, tmp_path)) is not None
    assert hook.handle(_event(doc, tmp_path)) is None
    assert hook.handle(_event(doc, tmp_path, session_id="other")) is not None


def test_hook_allows_cache_copy_only_for_project_files(tmp_path):
    doc = _doc(tmp_path)
    inside = hook.handle(_event(doc, tmp_path))["hookSpecificOutput"]
    assert inside["permissionDecision"] == "allow"
    outside = hook.handle(_event(doc, tmp_path / "elsewhere", session_id="s2"))["hookSpecificOutput"]
    assert "permissionDecision" not in outside


def test_hook_respects_deny_and_ask_rules(tmp_path):
    doc = _doc(tmp_path)
    settings = tmp_path / ".claude" / "settings.json"
    settings.parent.mkdir()
    settings.write_text(json.dumps({"permissions": {"deny": ["Read(**/*.docx)"]}}), encoding="utf-8")
    assert hook.handle(_event(doc, tmp_path)) is None
    settings.write_text(json.dumps({"permissions": {"ask": ["Read(./relatorio.docx)"]}}), encoding="utf-8")
    assert hook.handle(_event(doc, tmp_path)) is None
    settings.write_text(json.dumps({"permissions": {"deny": ["Read(./secrets/**)"]}}), encoding="utf-8")
    assert hook.handle(_event(doc, tmp_path)) is not None


def test_hook_ignores_text_files_other_tools_and_off_switch(tmp_path, monkeypatch):
    csv = tmp_path / "a.csv"
    csv.write_text("a,b\n1,2\n")
    assert hook.handle(_event(csv, tmp_path)) is None
    doc = _doc(tmp_path)
    assert hook.handle({**_event(doc, tmp_path), "tool_name": "Edit"}) is None
    monkeypatch.setenv("MDMAX_HOOK", "off")
    assert hook.handle(_event(doc, tmp_path)) is None


def _text_page(i):
    return [f"page {i} " + "texto corrido de um relatório com bastante conteúdo " * 2] * 6


def test_hook_pdf_pages_are_passed_to_the_converter(tmp_path):
    pdf = make_pdf(tmp_path / "r.pdf", [_text_page(i) for i in range(1, 6)])
    out = hook.handle(_event(pdf, tmp_path, tool_input={"file_path": str(pdf), "pages": "4-5"}))
    spec = out["hookSpecificOutput"]
    assert "pages" not in spec["updatedInput"]
    text = Path(spec["updatedInput"]["file_path"]).read_text(encoding="utf-8")
    assert "page 4" in text and "page 1 " not in text


def test_hook_leaves_visual_pdfs_to_claude(tmp_path):
    """A poster with a few words: the page image is the content, so no conversion."""
    poster = make_pdf(tmp_path / "banner.pdf", [["PROMOÇÃO", "Whey 900g", "R$ 99,90"]])
    assert hook.handle(_event(poster, tmp_path)) is None
    assert hook.handle(_event(poster, tmp_path, session_id="s9")) is None  # remembered, not retried
    from mdmax import convert
    assert "Whey 900g" in convert(poster).text  # an explicit conversion still works


def test_hook_script_end_to_end(tmp_path):
    """hooks/run.sh with real stdin/stdout, as Claude Code runs it."""
    doc = _doc(tmp_path)
    env = {**os.environ, "CLAUDE_PLUGIN_ROOT": str(ROOT), "MDMAX_HOME": str(tmp_path / "mh")}
    event = json.dumps(_event(doc, tmp_path, session_id="e2e"))
    try:
        done = subprocess.run(["sh", str(ROOT / "hooks" / "run.sh"), "read"], input=event,
                              capture_output=True, text=True, env=env, timeout=60)
    except FileNotFoundError:
        import pytest
        pytest.skip("no sh on this system")
    assert done.returncode == 0, done.stderr
    assert json.loads(done.stdout)["hookSpecificOutput"]["updatedInput"]["file_path"].endswith(".md")
    skipped = subprocess.run(["sh", str(ROOT / "hooks" / "run.sh"), "read"],
                             input=json.dumps(_event(tmp_path / "x.ts", tmp_path)),
                             capture_output=True, text=True, env=env, timeout=60)
    assert skipped.returncode == 0 and skipped.stdout == ""


# --------------------------------------------------------------------------- MCP

def _rpc(proc, message):
    proc.stdin.write((json.dumps(message) + "\n").encode())
    proc.stdin.flush()
    if "id" not in message:
        return None
    return json.loads(proc.stdout.readline())


def test_mcp_server_lists_and_calls_tools(tmp_path):
    doc = _doc(tmp_path)
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src"), "MDMAX_HOME": str(tmp_path / "mh")}
    proc = subprocess.Popen([sys.executable, "-m", "mdmax.mcp_server"], stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, env=env)
    try:
        init = _rpc(proc, {"jsonrpc": "2.0", "id": 1, "method": "initialize",
                           "params": {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "t"}}})
        assert init["result"]["protocolVersion"] == "2025-06-18"
        _rpc(proc, {"jsonrpc": "2.0", "method": "notifications/initialized"})
        tools = _rpc(proc, {"jsonrpc": "2.0", "id": 2, "method": "tools/list"})["result"]["tools"]
        assert {t["name"] for t in tools} == {"convert_document", "token_savings"}
        call = _rpc(proc, {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                           "params": {"name": "convert_document", "arguments": {"path": str(doc)}}})
        assert call["result"]["isError"] is False
        assert "Conteúdo do relatório." in call["result"]["content"][0]["text"]
        small = _rpc(proc, {"jsonrpc": "2.0", "id": 4, "method": "tools/call",
                            "params": {"name": "convert_document", "arguments": {"path": str(doc), "max_chars": 1000}}})
        assert "isError" in small["result"]
        missing = _rpc(proc, {"jsonrpc": "2.0", "id": 5, "method": "tools/call",
                              "params": {"name": "convert_document", "arguments": {"path": str(tmp_path / "no.pdf")}}})
        assert missing["result"]["isError"] is True
        savings = _rpc(proc, {"jsonrpc": "2.0", "id": 6, "method": "tools/call",
                              "params": {"name": "token_savings", "arguments": {}}})
        assert "Files converted: 1" in savings["result"]["content"][0]["text"]
        unknown = _rpc(proc, {"jsonrpc": "2.0", "id": 7, "method": "nope"})
        assert unknown["error"]["code"] == -32601
    finally:
        proc.stdin.close()
        proc.wait(timeout=10)


def test_mcp_long_document_comes_in_parts(tmp_path):
    from mdmax.mcp_server import _convert_tool

    path = tmp_path / "long.txt"
    path.write_text("linha de texto\n" * 3000, encoding="utf-8")
    first = _convert_tool({"path": str(path), "max_chars": 5000})["content"][0]["text"]
    assert "next_offset=" in first
    offset = int(first.split("next_offset=")[1].split()[0])
    second = _convert_tool({"path": str(path), "max_chars": 5000, "offset": offset})["content"][0]["text"]
    assert "linha de texto" in second


# --------------------------------------------------------------------------- CLI and log

def test_cli_convert_stats_and_shorthand(tmp_path, capsys):
    doc = _doc(tmp_path)
    assert cli_main(["convert", str(doc)]) == 0
    assert (tmp_path / "relatorio.md").exists()
    assert cli_main([str(doc), "--stdout", "-q"]) == 0  # `mdmax file` = `mdmax convert file`
    assert "# Título" in capsys.readouterr().out
    assert cli_main(["stats", "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["totals"]["files"] == 2
    log = (storage.home() / "savings.jsonl").read_text(encoding="utf-8")
    assert "Conteúdo" not in log  # names and numbers only


def test_cli_never_overwrites_a_markdown_input(tmp_path):
    md = tmp_path / "notes.md"
    md.write_text("# Notes\n\n\n\ntext   \n", encoding="utf-8")
    assert cli_main(["convert", str(md), "-q"]) == 0
    assert md.read_text(encoding="utf-8") == "# Notes\n\n\n\ntext   \n"
    assert (tmp_path / "notes.mdmax.md").exists()


def test_cli_batch_continues_after_a_bad_file(tmp_path, capsys):
    bad = tmp_path / "bad.xlsx"
    bad.write_bytes(b"not a zip")
    good = _doc(tmp_path)
    assert cli_main(["convert", str(bad), str(good), "-o", str(tmp_path / "out")]) == 0
    assert (tmp_path / "out" / "relatorio.md").exists()
    assert "bad.xlsx" in capsys.readouterr().err


def test_claude_ai_skill_zip_works_on_its_own(tmp_path):
    """The zip for claude.ai must run with no repository and no installed mdmax."""
    import zipfile

    sys.path.insert(0, str(ROOT / "tools"))
    from build_skill_zip import build

    archive = build(tmp_path / "skill.zip")
    with zipfile.ZipFile(archive) as zf:
        zf.extractall(tmp_path / "skills")
        frontmatter = zf.read("mdmax/SKILL.md").decode("utf-8").split("---")[1]
    assert "allowed-tools" not in frontmatter and "name: mdmax" in frontmatter
    doc = _doc(tmp_path)
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    env["MDMAX_HOME"] = str(tmp_path / "mh")
    done = subprocess.run([sys.executable, "-S", str(tmp_path / "skills" / "mdmax" / "scripts" / "mdmax_run.py"),
                           "convert", str(doc), "--stdout", "-q"], capture_output=True, text=True,
                          env=env, timeout=60, encoding="utf-8", cwd=str(tmp_path))
    assert done.returncode == 0, done.stderr
    assert "# Título" in done.stdout


def test_skill_launcher_runs_from_repository(tmp_path):
    doc = _doc(tmp_path)
    env = {**os.environ, "MDMAX_HOME": str(tmp_path / "mh")}
    env.pop("PYTHONPATH", None)
    done = subprocess.run([sys.executable, str(ROOT / "skills" / "mdmax" / "scripts" / "mdmax_run.py"),
                           "convert", str(doc), "--stdout", "-q"], capture_output=True, text=True,
                          env=env, timeout=60, encoding="utf-8")
    assert done.returncode == 0, done.stderr
    assert "# Título" in done.stdout
