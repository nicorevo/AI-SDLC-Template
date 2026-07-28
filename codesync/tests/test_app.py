"""Integration tests for the Codesync FastAPI lifecycle and endpoints."""

from __future__ import annotations

import asyncio
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import app as app_module
from app import app
from scanner.config import Config, SnapshotConfig
from scanner.snapshot import SnapshotManager

# ai-generated: Codex | human-reviewed: no | date: 2026-07-28


@pytest.fixture(autouse=True)
def configure_codesync(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Configure every test with an isolated project and disabled timer."""
    snapshot_path = tmp_path / "runtime" / "project-context.xml"
    monkeypatch.setenv("PROJECT_ROOT", str(tmp_path))
    monkeypatch.setenv("CODESYNC_OUTPUT_PATH", str(snapshot_path))
    monkeypatch.setenv("CODESYNC_INTERVAL_SECONDS", "0")
    monkeypatch.delenv("CODESYNC_CONFIG", raising=False)
    app_module._config = None
    app_module._manager = None
    app_module._scheduler_task = None
    return snapshot_path


def test_startup_generates_snapshot_before_health_is_ready(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# Startup Project", encoding="utf-8")

    with TestClient(app) as client:
        response = client.get("/health")
        assert app_module._scheduler_task is None

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["snapshot_exists"] is True
    assert data["last_success_at"]
    assert data["scheduler_interval_seconds"] == 0


def test_startup_uses_previous_snapshot_when_refresh_fails(
    configure_codesync: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    configure_codesync.parent.mkdir()
    configure_codesync.write_text("<progetto><previous /></progetto>", encoding="utf-8")

    def fail_refresh(self: SnapshotManager, _reason: str):
        self.state.status = "degraded"
        self.state.last_error = "RuntimeError: scan failed"
        raise RuntimeError("scan failed")

    monkeypatch.setattr(SnapshotManager, "refresh", fail_refresh)

    with TestClient(app) as client:
        health = client.get("/health")
        xml = client.get("/")

    assert health.json()["status"] == "degraded"
    assert xml.status_code == 200
    assert "<previous />" in xml.text


def test_startup_fails_without_valid_snapshot(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_refresh(_self: SnapshotManager, _reason: str):
        raise RuntimeError("scan failed")

    monkeypatch.setattr(SnapshotManager, "refresh", fail_refresh)

    with pytest.raises(RuntimeError, match="scan failed"), TestClient(app):
        pass


def test_root_serves_file_without_invoking_generator(tmp_path: Path) -> None:
    (tmp_path / "main.py").write_text("print('first')", encoding="utf-8")

    with TestClient(app) as client:
        assert app_module._manager is not None

        def unexpected_generator(_root, _config):
            raise AssertionError("GET / must not scan the project")

        app_module._manager._generator = unexpected_generator
        (tmp_path / "main.py").write_text("print('second')", encoding="utf-8")
        response = client.get("/")

    assert response.status_code == 200
    assert "application/xml" in response.headers["content-type"]
    assert "print('first')" in response.text
    assert "print('second')" not in response.text


def test_root_pretty_does_not_modify_snapshot(configure_codesync: Path) -> None:
    with TestClient(app) as client:
        before = configure_codesync.read_bytes()
        response = client.get("/?pretty=true")
        after = configure_codesync.read_bytes()

    assert response.status_code == 200
    assert len(response.text.splitlines()) > len(before.decode().splitlines())
    assert after == before


def test_manual_refresh_updates_snapshot(tmp_path: Path) -> None:
    source = tmp_path / "main.py"
    source.write_text("print('before')", encoding="utf-8")

    with TestClient(app) as client:
        source.write_text("print('after')", encoding="utf-8")
        refreshed = client.post("/refresh")
        xml = client.get("/")

    assert refreshed.status_code == 200
    assert refreshed.json()["reason"] == "manual"
    assert refreshed.json()["snapshot_size_bytes"] > 0
    assert "print('after')" in xml.text


def test_manual_refresh_returns_conflict_when_busy() -> None:
    with TestClient(app) as client:
        assert app_module._manager is not None
        assert app_module._manager._refresh_lock.acquire(blocking=False)
        try:
            response = client.post("/refresh")
        finally:
            app_module._manager._refresh_lock.release()

    assert response.status_code == 409


def test_openapi_documents_refresh_outcomes() -> None:
    schema = app.openapi()
    responses = schema["paths"]["/refresh"]["post"]["responses"]

    assert {"200", "409", "500"}.issubset(responses)


def test_scheduler_refreshes_and_stops_cleanly(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = Config(
        project_root=str(tmp_path),
        snapshot=SnapshotConfig(
            interval_seconds=1,
            output_path=str(tmp_path / "scheduled.xml"),
        ),
    )
    generated = 0

    def generator(_root, _config):
        nonlocal generated
        generated += 1
        return f"<progetto generation='{generated}' />"

    manager = SnapshotManager(config, generator=generator)
    real_sleep = asyncio.sleep
    sleep_calls = 0

    async def controlled_sleep(_seconds: float) -> None:
        nonlocal sleep_calls
        sleep_calls += 1
        if sleep_calls > 1:
            await real_sleep(60)

    monkeypatch.setattr(app_module.asyncio, "sleep", controlled_sleep)

    async def scenario() -> None:
        task = asyncio.create_task(app_module._scheduler_loop(manager))
        for _ in range(100):
            if generated == 1:
                break
            await real_sleep(0.001)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

    asyncio.run(scenario())

    assert generated == 1
    assert manager.state.reason == "scheduled"
