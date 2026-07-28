"""Integration tests for the FastAPI app endpoints."""

from __future__ import annotations

import importlib
from pathlib import Path

from fastapi.testclient import TestClient

import app as app_module
from app import app


def _setup_config(tmp_path: Path) -> None:
    """Initialize the global _config to scan tmp_path.

    This must be called INSIDE the test method after any client setup
    that might trigger lifespan.
    """
    from scanner.config import Config

    cfg = Config.from_env(str(tmp_path))
    app_module._config = cfg
    app_module._xml_cache = None
    app_module._cache_timestamp = 0.0


class TestXML:
    """Test suite for the XML endpoint."""

    def test_health_check(self, tmp_path: Path) -> None:
        """Test that /health returns ok."""
        Path(tmp_path, "test.txt").write_text("hello")

        with TestClient(app) as client:
            _setup_config(tmp_path)
            response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["project_root"] == str(tmp_path)

    def test_root_endpoint_returns_xml(self, tmp_path: Path) -> None:
        """Test that / returns valid XML with requested content."""
        Path(tmp_path, "README.md").write_text("# Test Project")
        Path(tmp_path, "main.py").write_text("print('hello')")

        with TestClient(app) as client:
            _setup_config(tmp_path)
            response = client.get("/")
        assert response.status_code == 200
        assert "application/xml" in response.headers["content-type"]
        xml_content = response.text
        assert "<?xml version" in xml_content
        assert "<progetto>" in xml_content
        assert "Test Project" in xml_content
        assert "print('hello')" in xml_content

    def test_cache_parameter_respects_rescan(self, tmp_path: Path) -> None:
        """Test that ?cache=false forces rescan."""
        Path(tmp_path, "file.py").write_text("print('cache test')")

        with TestClient(app) as client:
            _setup_config(tmp_path)
            # First request (populates cache)
            response1 = client.get("/")
            assert response1.status_code == 200
            assert "print('cache test')" in response1.text

            # Second request with cache=false
            response2 = client.get("/?cache=false")
            assert response2.status_code == 200
            assert "print('cache test')" in response2.text

    def test_pretty_parameter(self, tmp_path: Path) -> None:
        """Test that ?pretty=true adds indentation."""
        Path(tmp_path, "test.py").write_text("# comment")

        with TestClient(app) as client:
            _setup_config(tmp_path)
            # Without pretty
            response_compact = client.get("/?cache=false")
            # With pretty
            response_pretty = client.get("/?cache=false&pretty=true")
            assert response_pretty.status_code == 200
            # Check that pretty response has more lines (indented)
            assert len(response_pretty.text.split("\n")) > len(response_compact.text.split("\n"))

    def test_xml_structure_completeness(self, tmp_path: Path) -> None:
        """Test that XML has expected structure."""
        src_dir = Path(tmp_path, "src")
        src_dir.mkdir()
        Path(src_dir, "main.py").write_text("print('main')")
        Path(tmp_path, "README.md").write_text("# Readme")

        with TestClient(app) as client:
            _setup_config(tmp_path)
            response = client.get("/")
        assert response.status_code == 200
        xml = response.text

        # Check structure
        assert '<?xml version="1.0" encoding="UTF-8"?>' in xml
        assert "<progetto>" in xml
        assert "<contesto>" in xml
        assert "<struttura>" in xml
        assert "</progetto>" in xml
        assert "</contesto>" in xml
        assert "</struttura>" in xml
        # Contains file with extension attribute
        assert 'ext="py"' in xml
