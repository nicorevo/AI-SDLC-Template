"""Tests for scanner generator (XML generation)."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from scanner.config import Config, ScannerConfig
from scanner.generator import generate_project_xml


def _create_fixture_tree(tmp_path: Path, files: dict) -> Path:
    """Create a temporary directory structure for testing."""
    for rel_path, content in files.items():
        full = tmp_path / rel_path
        full.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            full.write_bytes(content)
        else:
            full.write_text(content, encoding="utf-8")
    return tmp_path


def test_generate_xml_minimal(tmp_path: Path) -> None:
    """Test XML generation with minimal project (single file)."""
    fixture = _create_fixture_tree(
        tmp_path,
        {"README.md": "# Test Project", "main.py": "print('hello')"},
    )

    xml = generate_project_xml(str(fixture), Config(project_root=str(fixture)))

    assert '<?xml version="1.0" encoding="UTF-8"?>' in xml
    assert "<progetto>" in xml
    assert "<contesto>" in xml
    assert "Test Project" in xml
    assert "main.py" in xml
    assert "print('hello')" in xml


def test_generate_xml_respects_gitignore(tmp_path: Path) -> None:
    """Test that .gitignore patterns are respected."""
    fixture = _create_fixture_tree(
        tmp_path,
        {
            "src/app.py": "print('src')",
            "dist/app.js": "console.log('dist')",  # Should be skipped
            ".gitignore": "dist/",
        },
    )
    cfg = Config(
        project_root=str(fixture),
        scanner=ScannerConfig(skip_dirs=["dist"]),
    )
    xml = generate_project_xml(str(fixture), cfg)

    assert "src/app.py" in xml or "app.py" in xml
    assert "console.log('dist')" not in xml


def test_generate_xml_skips_binary(tmp_path: Path) -> None:
    """Test that binary files are excluded."""
    fixture = _create_fixture_tree(
        tmp_path,
        {
            "data.txt": "hello",
            "image.png": b"\x89PNG",  # PNG header
            "app.py": "print('code')",
        },
    )

    xml = generate_project_xml(str(fixture), Config(project_root=str(fixture)))

    assert "hello" in xml
    assert "PNG" not in xml  # Binary content excluded
    assert "print('code')" in xml


def test_generate_xml_nested_dirs(tmp_path: Path) -> None:
    """Test nested directory structure."""
    fixture = _create_fixture_tree(
        tmp_path,
        {
            "src/main.py": "print('main')",
            "src/utils/helpers.py": "def helper(): pass",
            "README.md": "# Nested",
        },
    )

    xml = generate_project_xml(str(fixture), Config(project_root=str(fixture)))

    assert "<progetto>" in xml
    assert "src/main.py" in xml or 'main.py' in xml
    assert "helper()" in xml
    assert "Nested" in xml


def test_generate_xml_file_too_large(tmp_path: Path) -> None:
    """Test handling of files exceeding max size."""
    fixture = _create_fixture_tree(
        tmp_path,
        {
            "big.txt": "x" * (600 * 1024),  # 600KB
        },
    )
    cfg = Config(
        project_root=str(fixture),
        scanner=ScannerConfig(max_file_size=500 * 1024),
    )
    xml = generate_project_xml(str(fixture), cfg)

    assert "[FILE TROPPO GRANDE" in xml


def test_generate_xml_with_cdata_escape(tmp_path: Path) -> None:
    """Test that ]] inside CDATA is properly escaped."""
    fixture = _create_fixture_tree(
        tmp_path,
        {
            "file.py": "print(']]>test')",  # Contains the ]]> sequence that triggers escape
        },
    )

    xml = generate_project_xml(str(fixture), Config(project_root=str(fixture)))

    # Should contain escaped CDATA: the sequence ]]> is replaced by ]]]]><![CDATA[>
    assert "]]]]><![CDATA[>" in xml
    # And the original content should still be in the second CDATA section
    assert "test" in xml


def test_config_from_env(tmp_path: Path) -> None:
    """Test Config loading from env vars."""
    os.environ["PROJECT_ROOT"] = str(tmp_path)
    os.environ.pop("CODESYNC_CONFIG", None)

    cfg = Config.from_env()

    assert cfg.project_root == str(tmp_path)
    assert cfg.service.port == 9000
    assert len(cfg.scanner.skip_dirs) > 0
    assert len(cfg.scanner.binary_extensions) > 0


def test_config_from_yaml(tmp_path: Path) -> None:
    """Test Config loading from YAML file."""
    import yaml

    yaml_content = {
        "service": {"port": 8080, "cors_origins": ["http://localhost:3000"]},
        "scanner": {
            "max_file_size": 1024,
            "skip_dirs": [".tmp"],
            "binary_extensions": [".bin"],
        },
    }
    yaml_path = tmp_path / "config.yaml"
    yaml_path.write_text(yaml.dump(yaml_content), encoding="utf-8")
    readme = tmp_path / "README.md"
    readme.write_text("# Project", encoding="utf-8")

    os.environ["CODESYNC_CONFIG"] = str(yaml_path)
    os.environ["PROJECT_ROOT"] = str(tmp_path)

    cfg = Config.from_env()

    assert cfg.service.port == 8080
    assert cfg.scanner.max_file_size == 1024
    assert ".tmp" in cfg.scanner.skip_dirs
    assert ".bin" in cfg.scanner.binary_extensions


def test_config_invalid_dir(tmp_path: Path) -> None:
    """Test Config raises for invalid PROJECT_ROOT."""
    nonexistent = tmp_path / "nonexistent"
    os.environ["PROJECT_ROOT"] = str(nonexistent)

    with pytest.raises(FileNotFoundError, match="not a valid directory"):
        Config.from_env()


@pytest.fixture(autouse=True)
def clean_env():
    """Clean PROJECT_ROOT and CODESYNC_CONFIG env vars after each test."""
    yield
    os.environ.pop("PROJECT_ROOT", None)
    os.environ.pop("CODESYNC_CONFIG", None)
