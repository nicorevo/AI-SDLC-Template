"""Persistent XML snapshot orchestration."""

from __future__ import annotations

import os
import tempfile
import threading
import time
import xml.etree.ElementTree as ET
from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from pathlib import Path

from .config import Config
from .generator import generate_project_xml

# ai-generated: Codex | human-reviewed: no | date: 2026-07-28

SnapshotGenerator = Callable[[str, Config], str]


class SnapshotRefreshInProgress(RuntimeError):
    """Raised when a second refresh is requested while one is active."""


@dataclass
class SnapshotState:
    """Observable state for the most recent snapshot attempt."""

    status: str = "unavailable"
    reason: str | None = None
    last_success_at: str | None = None
    last_attempt_at: str | None = None
    last_refresh_duration_ms: int | None = None
    snapshot_size_bytes: int | None = None
    last_error: str | None = None


class SnapshotManager:
    """Generate, validate, and atomically publish a single XML snapshot."""

    def __init__(
        self,
        config: Config,
        generator: SnapshotGenerator = generate_project_xml,
    ) -> None:
        self.config = config
        self.output_path = Path(config.snapshot.output_path)
        self.state = SnapshotState()
        self._generator = generator
        self._refresh_lock = threading.Lock()

    def refresh(self, reason: str) -> SnapshotState:
        """Publish a new snapshot or preserve the last valid one on failure."""
        if not self._refresh_lock.acquire(blocking=False):
            raise SnapshotRefreshInProgress("A snapshot refresh is already in progress")

        started = time.perf_counter()
        self.state.reason = reason
        self.state.last_attempt_at = self._utc_now()
        temp_path: Path | None = None
        try:
            xml = self._generator(self.config.project_root, self.config)
            try:
                ET.fromstring(xml)
            except ET.ParseError as exc:
                raise ValueError("Generated snapshot is not valid XML") from exc

            self.output_path.parent.mkdir(parents=True, exist_ok=True)
            temp_path = self._write_temporary(xml)
            os.replace(temp_path, self.output_path)
            temp_path = None

            self.state.status = "ok"
            self.state.last_success_at = self._utc_now()
            self.state.snapshot_size_bytes = self.output_path.stat().st_size
            self.state.last_error = None
        except Exception as exc:
            self.state.status = "degraded" if self.has_valid_snapshot() else "unavailable"
            self.state.last_error = f"{type(exc).__name__}: {exc}"
            raise
        finally:
            self.state.last_refresh_duration_ms = round(
                (time.perf_counter() - started) * 1000
            )
            if temp_path is not None:
                temp_path.unlink(missing_ok=True)
            self._refresh_lock.release()
        return replace(self.state)

    def has_valid_snapshot(self) -> bool:
        """Return whether the published path contains valid XML."""
        try:
            ET.parse(self.output_path)
        except (OSError, ET.ParseError):
            return False
        return True

    def _write_temporary(self, xml: str) -> Path:
        """Write and flush a temporary next to the final snapshot."""
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=self.output_path.parent,
            prefix=f".{self.output_path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            handle.write(xml)
            handle.flush()
            os.fsync(handle.fileno())
            return Path(handle.name)

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(UTC).isoformat()
