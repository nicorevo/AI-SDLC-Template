"""FastAPI application exposing a persistent project XML snapshot."""

from __future__ import annotations

import asyncio
import logging
import os
from contextlib import asynccontextmanager, suppress
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from scanner.config import Config
from scanner.snapshot import SnapshotManager, SnapshotRefreshInProgress, SnapshotState

# ai-generated: Codex | human-reviewed: no | date: 2026-07-28

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

_config: Config | None = None
_manager: SnapshotManager | None = None
_scheduler_task: asyncio.Task[None] | None = None


class RefreshResponse(BaseModel):
    """Metadata returned after a successful manual refresh."""

    status: str
    reason: str
    last_success_at: str
    last_refresh_duration_ms: int
    snapshot_size_bytes: int
    snapshot_path: str


class HealthResponse(BaseModel):
    """Current scheduler and snapshot health."""

    status: str
    project_root: str
    snapshot_path: str
    snapshot_exists: bool
    last_success_at: str | None
    last_attempt_at: str | None
    last_refresh_duration_ms: int | None
    snapshot_size_bytes: int | None
    scheduler_interval_seconds: int
    last_error: str | None


async def _scheduler_loop(manager: SnapshotManager) -> None:
    """Refresh sequentially, counting each interval after the prior attempt."""
    interval = manager.config.snapshot.interval_seconds
    while True:
        await asyncio.sleep(interval)
        try:
            await asyncio.to_thread(manager.refresh, "scheduled")
        except SnapshotRefreshInProgress:
            logger.info("Scheduled refresh skipped because another refresh is active")
        except Exception:
            logger.exception("Scheduled snapshot refresh failed; preserving previous snapshot")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Generate the initial snapshot and own the periodic task."""
    global _config, _manager, _scheduler_task
    _config = Config.from_env(config_path=os.getenv("CODESYNC_CONFIG"))
    _manager = SnapshotManager(_config)
    try:
        await asyncio.to_thread(_manager.refresh, "startup")
    except Exception:
        if not _manager.has_valid_snapshot():
            logger.exception("Initial snapshot failed and no valid snapshot exists")
            raise
        _manager.state.status = "degraded"
        _manager.state.snapshot_size_bytes = _manager.output_path.stat().st_size
        logger.exception("Initial snapshot failed; serving previous valid snapshot")

    if _config.snapshot.interval_seconds > 0:
        _scheduler_task = asyncio.create_task(_scheduler_loop(_manager))
    logger.info("Codesync ready — snapshot '%s'", _manager.output_path)
    try:
        yield
    finally:
        if _scheduler_task is not None:
            _scheduler_task.cancel()
            with suppress(asyncio.CancelledError):
                await _scheduler_task
        _scheduler_task = None
        logger.info("Codesync service shutting down")


app = FastAPI(
    title="Codesync",
    description="Service that serves a persistent project context XML snapshot.",
    version="0.1.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_manager() -> SnapshotManager:
    """Return initialized snapshot state."""
    if _manager is None:
        raise RuntimeError("Codesync is not initialized")
    return _manager


def _pretty_xml(xml: str) -> str:
    """Preserve the existing lightweight response-only pretty formatting."""
    lines = xml.split(">")
    indented: list[str] = []
    depth = 0
    for line in lines:
        if line.startswith("</"):
            depth = max(depth - 1, 0)
        stripped = line.strip()
        if stripped:
            indented.append(f"{'  ' * depth}{stripped}>")
        if line.startswith("<") and not line.startswith(("</", "<?")):
            depth += 1
    return "\n".join(indented)


@app.get("/", summary="Get the current project XML snapshot")
def get_project_xml(
    pretty: bool = Query(False, description="Pretty-print only the HTTP response"),
) -> Response:
    """Serve the published file without scanning the project."""
    manager = get_manager()
    try:
        xml = manager.output_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise HTTPException(status_code=503, detail="No valid snapshot is available") from exc
    if pretty:
        xml = _pretty_xml(xml)
    return Response(content=xml, media_type="application/xml")


@app.post(
    "/refresh",
    response_model=RefreshResponse,
    responses={409: {"description": "Refresh already active"}, 500: {"description": "Refresh failed"}},
    summary="Refresh the project XML snapshot",
)
async def refresh_project_xml() -> RefreshResponse:
    """Synchronously request a new atomic snapshot."""
    manager = get_manager()
    try:
        state = await asyncio.to_thread(manager.refresh, "manual")
    except SnapshotRefreshInProgress as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Manual snapshot refresh failed")
        raise HTTPException(status_code=500, detail="Snapshot refresh failed") from exc
    return _refresh_response(state, manager.output_path)


def _refresh_response(state: SnapshotState, output_path: Path) -> RefreshResponse:
    assert state.reason is not None
    assert state.last_success_at is not None
    assert state.last_refresh_duration_ms is not None
    assert state.snapshot_size_bytes is not None
    return RefreshResponse(
        status=state.status,
        reason=state.reason,
        last_success_at=state.last_success_at,
        last_refresh_duration_ms=state.last_refresh_duration_ms,
        snapshot_size_bytes=state.snapshot_size_bytes,
        snapshot_path=str(output_path),
    )


@app.get("/health", response_model=HealthResponse, summary="Get snapshot health")
def health_check() -> HealthResponse:
    """Expose real snapshot and scheduler metadata."""
    manager = get_manager()
    state = manager.state
    return HealthResponse(
        status=state.status,
        project_root=manager.config.project_root,
        snapshot_path=str(manager.output_path),
        snapshot_exists=manager.has_valid_snapshot(),
        last_success_at=state.last_success_at,
        last_attempt_at=state.last_attempt_at,
        last_refresh_duration_ms=state.last_refresh_duration_ms,
        snapshot_size_bytes=state.snapshot_size_bytes,
        scheduler_interval_seconds=manager.config.snapshot.interval_seconds,
        last_error=state.last_error,
    )


def run_server(host: str = "0.0.0.0", port: int = 9000, reload: bool = False) -> None:
    """Start the server for manual invocation."""
    uvicorn.run("app:app", host=host, port=port, reload=reload)


if __name__ == "__main__":
    run_server()
