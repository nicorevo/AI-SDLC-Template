"""Configuration loader using pyyaml."""

from __future__ import annotations

import os
from dataclasses import dataclass, field

import yaml

# ai-generated: Codex | human-reviewed: no | date: 2026-07-28


@dataclass(frozen=True)
class ScannerConfig:
    """Scanning options (immutable after construction)."""

    skip_dirs: list[str] = field(
        default_factory=lambda: [
            ".git",
            "__pycache__",
            "node_modules",
            ".idea",
            ".vscode",
            ".metadata",
            "target",
            "dist",
            "env",
            ".environment",
            "LOGS",
            ".settings",
            "temp",
        ]
    )
    max_file_size: int = 500 * 1024  # 500 KB
    binary_extensions: list[str] = field(
        default_factory=lambda: [
            ".class",
            ".jar",
            ".war",
            ".exe",
            ".app",
            ".pyc",
            ".pyo",
            ".pyd",
            ".so",
            ".dll",
            ".dylib",
            ".o",
            ".a",
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".bmp",
            ".ico",
            ".svg",
            ".webp",
            ".mp4",
            ".avi",
            ".mov",
            ".wmv",
            ".flv",
            ".tiff",
            ".zip",
            ".tar",
            ".gz",
            ".bz2",
            ".7z",
            ".rar",
            ".pdf",
            ".doc",
            ".docx",
            ".xls",
            ".xlsx",
            ".ppt",
            ".pptx",
            ".woff",
            ".woff2",
            ".ttf",
            ".eot",
            ".db",
            ".sqlite",
            ".sqlite3",
            ".iml",
        ]
    )


@dataclass(frozen=True)
class ServiceConfig:
    """HTTP service configuration."""

    host: str = "0.0.0.0"
    port: int = 9000
    cors_origins: list[str] = field(default_factory=lambda: ["*"])


@dataclass(frozen=True)
class SnapshotConfig:
    """Persistent XML snapshot settings."""

    interval_seconds: int = 180
    output_path: str = ""


@dataclass(frozen=True)
class Config:
    """Top-level configuration."""

    project_root: str = ""
    service: ServiceConfig = field(default_factory=ServiceConfig)
    scanner: ScannerConfig = field(default_factory=ScannerConfig)
    snapshot: SnapshotConfig = field(default_factory=SnapshotConfig)

    @classmethod
    def from_env(
        cls,
        project_root: str | None = None,
        config_path: str | None = None,
    ) -> Config:
        """Build Config from env vars and optional YAML file."""
        service_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        project_root = project_root or os.getenv("PROJECT_ROOT", service_root)
        project_root = os.path.abspath(project_root)
        if not os.path.isdir(project_root):
            raise FileNotFoundError(f"PROJECT_ROOT '{project_root}' is not a valid directory")

        svc = ServiceConfig(
            host=os.getenv("SERVICE_HOST", "0.0.0.0"),
            port=int(os.getenv("SERVICE_PORT", "9000")),
        )
        default_scanner = ScannerConfig()
        default_snapshot = SnapshotConfig(
            output_path=os.path.join(service_root, "data", "project-context.xml")
        )
        yaml_path = config_path or os.getenv(
            "CODESYNC_CONFIG", os.path.join(service_root, "config.yaml")
        )
        scanner = default_scanner
        snapshot_interval: object = default_snapshot.interval_seconds
        snapshot_output = default_snapshot.output_path
        if os.path.isfile(yaml_path):
            with open(yaml_path, encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            svc_cfg = data.get("service", {})
            scan_cfg = data.get("scanner", {})
            snapshot_cfg = data.get("snapshot", {})
            svc = ServiceConfig(
                host=svc_cfg.get("host", svc.host),
                port=int(svc_cfg.get("port", svc.port)),
                cors_origins=svc_cfg.get("cors_origins", svc.cors_origins),
            )
            scanner = ScannerConfig(
                skip_dirs=scan_cfg.get("skip_dirs", default_scanner.skip_dirs),
                max_file_size=int(
                    scan_cfg.get("max_file_size", default_scanner.max_file_size)
                ),
                binary_extensions=scan_cfg.get(
                    "binary_extensions", default_scanner.binary_extensions
                ),
            )
            snapshot_interval = snapshot_cfg.get(
                "interval_seconds", default_snapshot.interval_seconds
            )
            snapshot_output = cls._resolve_output_path(
                snapshot_cfg.get("output_path", default_snapshot.output_path), service_root
            )

        interval_raw = os.getenv("CODESYNC_INTERVAL_SECONDS")
        try:
            interval = int(interval_raw if interval_raw is not None else snapshot_interval)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "snapshot interval (CODESYNC_INTERVAL_SECONDS) must be an integer >= 0"
            ) from exc
        if interval < 0:
            raise ValueError(
                "snapshot interval (CODESYNC_INTERVAL_SECONDS) must be an integer >= 0"
            )
        output_path = cls._resolve_output_path(
            os.getenv("CODESYNC_OUTPUT_PATH", snapshot_output), service_root
        )

        return cls(
            project_root=project_root,
            service=svc,
            scanner=scanner,
            snapshot=SnapshotConfig(interval_seconds=interval, output_path=output_path),
        )

    @staticmethod
    def _resolve_output_path(path: str, service_root: str) -> str:
        """Resolve relative snapshot paths against the Codesync directory."""
        return os.path.abspath(path if os.path.isabs(path) else os.path.join(service_root, path))
