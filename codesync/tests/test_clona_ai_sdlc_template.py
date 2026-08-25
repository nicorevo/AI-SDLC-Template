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


def test_rimuovi_file_template_elimina_solo_materiale_interno(
    tmp_path: Path,
) -> None:
    for relative_path in cloner.TEMPLATE_ONLY_PATHS:
        target = tmp_path / relative_path
        if relative_path.endswith(".py"):
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("template-only", encoding="utf-8")
        else:
            target.mkdir(parents=True, exist_ok=True)
            (target / "marker.txt").write_text("template-only", encoding="utf-8")

    kept = tmp_path / ".opencode" / "skills" / "using-agent-skills" / "SKILL.md"
    kept.parent.mkdir(parents=True)
    kept.write_text("keep", encoding="utf-8")

    cloner.rimuovi_file_template(tmp_path)

    assert all(not (tmp_path / path).exists() for path in cloner.TEMPLATE_ONLY_PATHS)
    assert kept.exists()


def test_main_uses_positional_arguments_without_prompt(monkeypatch) -> None:
    create = Mock()
    monkeypatch.setattr(cloner, "crea_progetto_da_template", create)

    cloner.main(["https://example.test/template.git", "progetto", "/tmp"])

    create.assert_called_once_with(
        "https://example.test/template.git", "progetto", "/tmp"
    )
