#!/usr/bin/env python3
"""Codesync entry point — starts the FastAPI server.

Usage:
    python main.py [OPTIONS]

Options:
    --host TEXT          Host to bind (default: 0.0.0.0)
    --port INTEGER       Port to bind (default: 9000)
    --reload             Enable auto-reload for development
    --project-root TEXT  Path to the project to scan (overrides env)
"""

from __future__ import annotations

import argparse
import os

from scanner.config import Config
from app import run_server


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Codesync - Serve project context as XML")
    parser.add_argument("--host", default=None, help="Host to bind (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=None, help="Port to bind (default: 9000)")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--project-root", default=None, help="Path to project to scan")
    args = parser.parse_args()

    cfg = None
    if args.project_root:
        os.environ["PROJECT_ROOT"] = os.path.abspath(args.project_root)
        cfg = Config.from_env(args.project_root)

    host = args.host or os.getenv("SERVICE_HOST", "0.0.0.0")
    port = args.port or int(os.getenv("SERVICE_PORT", "9000"))

    if not cfg:
        cfg_path = os.getenv("CODESYNC_CONFIG")
        cfg = Config.from_env(cfg_path or None)

    project_dir = args.project_root or cfg.project_root

    print(f"Codesync running on {host}:{port}")
    print(f"Scanning: {project_dir}")

    run_server(
        host=host,
        port=port,
        reload=args.reload,
    )


if __name__ == "__main__":
    main()
