#!/usr/bin/env python3
"""FastAPI application exposing project context as XML."""

from __future__ import annotations

import logging
import os
import time
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Query, Response
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

from scanner.config import Config
from scanner.generator import generate_project_xml


# Global state
_config: Config | None = None
_xml_cache: str | None = None
_cache_timestamp: float = 0.0
_CACHE_TTL: int = 60  # seconds — configurable via CACHE_TTL_SEC/env


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle."""
    global _config, _CACHE_TTL
    cfg_path = os.getenv("CODESYNC_CONFIG")
    _config = Config.from_env(cfg_path or None)
    _CACHE_TTL = int(os.getenv("CACHE_TTL_SEC", "60"))
    if _config is not None and _config.project_root:
        logger.info(
            "Codesync service starting — scanning '%s' on %s:%d",
            _config.project_root,
            _config.service.host,
            _config.service.port,
        )
    yield
    logger.info("Codesync service shutting down.")


def get_config() -> Config:
    """Return the current config, or raise."""
    if _config is None:
        raise RuntimeError("Codesync is not initialized (missing Config).")
    return _config


app = FastAPI(
    title="Codesync",
    description="Service that serves project context as an XML snapshot.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _pretty_xml(xml: str) -> str:
    """Simple pretty-printer: split by tag boundaries and indent."""
    lines = xml.split(">")
    indented: list[str] = []
    depth = 0
    for line in lines:
        if line.startswith("</"):
            depth -= 1
            if depth < 0:
                depth = 0
        prefix = "  " * depth
        stripped = line.strip()
        if stripped and not stripped.startswith("<?"):
            indented.append(f"{prefix}{stripped}>")
        elif stripped.startswith("<?"):
            # Keep XML declaration at root
            indented.append(f"{stripped}>")
        if line.startswith("<") and not line.startswith("</") and not line.startswith("<?"):
            depth += 1
    return "\n".join(indented)


@app.get("/", summary="Get project XML context")
def get_project_xml(
    cache: bool = Query(True, description="Use cached XML if available"),
    pretty: bool = Query(False, description="Pretty-print XML indentation"),
) -> Response:
    """Expose project context as XML."""
    global _xml_cache, _cache_timestamp

    cfg = get_config()
    now = time.time()

    if cache and _xml_cache and (now - _cache_timestamp) < _CACHE_TTL:
        xml = _xml_cache
        logger.debug("Returning cached XML (TTL=%ds) — %d bytes", _CACHE_TTL, len(xml))
    else:
        logger.info("Scanning project: '%s'", cfg.project_root)
        xml = generate_project_xml(cfg.project_root, cfg)
        if cache:
            _xml_cache = xml
            _cache_timestamp = now
            logger.info("Cache updated — %d bytes", len(xml))

    if pretty:
        xml = _pretty_xml(xml)

    return Response(content=xml, media_type="application/xml")


@app.get("/health", summary="Health check endpoint")
def health_check() -> dict[str, str]:
    """Health check — returns service and scanner status."""
    cfg = get_config()
    return {
        "status": "ok",
        "project_root": cfg.project_root,
        "cache_hits": "1.0",
    }


def run_server(
    host: str = "0.0.0.0",
    port: int = 9000,
    reload: bool = False,
):
    """Start the server (for manual invocation)."""
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=reload,
    )


if __name__ == "__main__":
    run_server()
