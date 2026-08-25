"""Tests for persistent and atomic XML snapshots."""

from __future__ import annotations

import threading
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from scanner.config import Config, SnapshotConfig
from scanner.snapshot import SnapshotManager, SnapshotRefreshInProgress

# ai-generated: Codex | human-reviewed: no | date: 2026-07-28


def _config(project_root: Path, output_path: Path) -> Config:
    return Config(
        project_root=str(project_root),
        snapshot=SnapshotConfig(interval_seconds=180, output_path=str(output_path)),
    )


def test_refresh_publishes_valid_xml_and_metadata(tmp_path: Path) -> None:
    output_path = tmp_path / "data" / "project.xml"
    manager = SnapshotManager(
        _config(tmp_path, output_path),
        generator=lambda _root, _config: "<?xml version='1.0'?><progetto />",
    )

    result = manager.refresh("manual")

    assert output_path.read_text(encoding="utf-8").endswith("<progetto />")
    assert result.status == "ok"
    assert result.reason == "manual"
    assert result.snapshot_size_bytes == output_path.stat().st_size
    assert result.last_success_at is not None
    assert result.last_refresh_duration_ms is not None
    assert result.last_refresh_duration_ms == manager.state.last_refresh_duration_ms
    assert not list(output_path.parent.glob("*.tmp"))


@pytest.mark.parametrize(
    "generated",
    [pytest.param("<progetto>", id="invalid-xml"), pytest.param(None, id="generator-error")],
)
def test_failed_refresh_preserves_previous_snapshot(
    tmp_path: Path, generated: str | None
) -> None:
    output_path = tmp_path / "project.xml"
    previous = b"<?xml version='1.0'?><progetto><old /></progetto>"
    output_path.write_bytes(previous)

    def failing_generator(_root: str, _config: Config) -> str:
        if generated is None:
            raise RuntimeError("scan failed")
        return generated

    manager = SnapshotManager(
        _config(tmp_path, output_path), generator=failing_generator
    )

    with pytest.raises((RuntimeError, ValueError)):
        manager.refresh("scheduled")

    assert output_path.read_bytes() == previous
    assert manager.state.status == "degraded"
    assert manager.state.last_error


def test_concurrent_refresh_is_rejected(tmp_path: Path) -> None:
    output_path = tmp_path / "project.xml"
    started = threading.Event()
    release = threading.Event()

    def slow_generator(_root: str, _config: Config) -> str:
        started.set()
        assert release.wait(timeout=2)
        return "<progetto />"

    manager = SnapshotManager(_config(tmp_path, output_path), generator=slow_generator)
    worker = threading.Thread(target=manager.refresh, args=("scheduled",))
    worker.start()
    assert started.wait(timeout=2)

    with pytest.raises(SnapshotRefreshInProgress):
        manager.refresh("manual")

    release.set()
    worker.join(timeout=2)
    assert not worker.is_alive()


def test_refresh_excludes_only_its_own_output_path(tmp_path: Path) -> None:
    output_path = tmp_path / "data" / "project-context.xml"
    output_path.parent.mkdir()
    output_path.write_text("<progetto />", encoding="utf-8")
    same_name = tmp_path / "src" / "project-context.xml"
    same_name.parent.mkdir()
    same_name.write_text("<different />", encoding="utf-8")
    manager = SnapshotManager(_config(tmp_path, output_path))

    manager.refresh("manual")

    root = ET.parse(output_path).getroot()
    matching_files = [
        node for node in root.findall(".//file") if node.get("name") == "project-context.xml"
    ]
    assert len(matching_files) == 1
    assert "<different />" in (matching_files[0].text or "")


def test_refresh_result_is_stable_after_a_later_refresh(tmp_path: Path) -> None:
    output_path = tmp_path / "project.xml"
    manager = SnapshotManager(
        _config(tmp_path, output_path), generator=lambda _root, _config: "<progetto />"
    )

    manual_result = manager.refresh("manual")
    manager.refresh("scheduled")

    assert manual_result.reason == "manual"
    assert manager.state.reason == "scheduled"
