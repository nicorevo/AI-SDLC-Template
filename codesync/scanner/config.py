"""Configuration loader using pyyaml."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List

import yaml


@dataclass(frozen=True)
class ScannerConfig:
    """Scanning options (immutable after construction)."""

    skip_dirs: List[str] = field(
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
    binary_extensions: List[str] = field(
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
    cors_origins: List[str] = field(default_factory=lambda: ["*"])


@dataclass(frozen=True)
class Config:
    """Top-level configuration."""

    project_root: str = ""
    service: ServiceConfig = field(default_factory=ServiceConfig)
    scanner: ScannerConfig = field(default_factory=ScannerConfig)

    @classmethod
    def from_env(cls, config_path: str | None = None) -> "Config":
        """Build Config from env vars and optional YAML file."""
        # 1. Project root
        project_root = config_path or os.getenv(
            "PROJECT_ROOT", os.path.abspath(os.path.dirname(__file__) + "/..")
        )

        # 2. Service defaults
        svc = ServiceConfig(
            host=os.getenv("SERVICE_HOST", "0.0.0.0"),
            port=int(os.getenv("SERVICE_PORT", "9000")),
        )

        # Defaults (will be overwritten by YAML if present)
        default_scanner = ScannerConfig()

        # 3. Try loading YAML config
        yaml_path = os.getenv(
            "CODESYNC_CONFIG",
            os.path.join(project_root, "config.yaml"),
        )
        scanner = default_scanner
        if os.path.isfile(yaml_path):
            with open(yaml_path, encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            svc_cfg = data.get("service", {})
            scan_cfg = data.get("scanner", {})
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

        project_root = os.path.abspath(project_root)
        if not os.path.isdir(project_root):
            raise FileNotFoundError(
                f"PROJECT_ROOT '{project_root}' is not a valid directory"
            )

        return cls(
            project_root=project_root,
            service=svc,
            scanner=scanner,
        )
