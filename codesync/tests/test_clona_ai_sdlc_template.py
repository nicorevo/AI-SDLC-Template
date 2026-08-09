"""Tests for the template cloning script."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from unittest.mock import Mock


SCRIPT_PATH = Path(__file__).parents[2] / "clona-ai-sdlc-template.py"
SPEC = importlib.util.spec_from_file_location("clona_ai_sdlc_template", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
cloner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cloner)

# ai-generated: Codex | human-reviewed: no | date: 2026-08-09


def test_crea_progetto_clona_opcl_e_inizializza_main(
    tmp_path: Path, monkeypatch
) -> None:
    """The source is opcl, while the new repository starts on main."""
    run = Mock()
    monkeypatch.setattr(cloner.subprocess, "run", run)
    monkeypatch.setattr(cloner.os.path, "exists", lambda _path: False)

    cloner.crea_progetto_da_template(
        "https://example.test/template.git", "progetto", str(tmp_path)
    )

    clone_command = run.call_args_list[0].args[0]
    assert clone_command == [
        "git",
        "clone",
        "--depth",
        "1",
        "--branch",
        "opcl",
        "--single-branch",
        "https://example.test/template.git",
        "progetto",
    ]

    init_command = next(call.args[0] for call in run.call_args_list if call.args[0][:2] == ["git", "init"])
    assert init_command == ["git", "init", "-b", "main"]
