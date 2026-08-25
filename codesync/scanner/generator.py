"""Core scanning and XML generation logic (port from prj-context-extract.py)."""

from __future__ import annotations

import fnmatch
import os
import pathlib
from xml.sax.saxutils import escape

from .config import Config, ScannerConfig

# ai-generated: Codex | human-reviewed: no | date: 2026-07-28


ALWAYS_SKIP_DIRS = {
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
}


def load_gitignore_patterns(root_dir: str) -> list[str]:
    """Carica i pattern dal .gitignore nella root del progetto."""
    gitignore_path = os.path.join(root_dir, ".gitignore")
    patterns: list[str] = []
    if os.path.isfile(gitignore_path):
        with open(gitignore_path, encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    patterns.append(line)
    return patterns


def is_ignored_by_gitignore(
    rel_path: str, patterns: list[str], is_dir: bool
) -> bool:
    """Controlla se un path relativo corrisponde a uno dei pattern .gitignore."""
    name = os.path.basename(rel_path)
    # Normalizza il path con /
    rel_posix = rel_path.replace("\\", "/")
    if is_dir:
        rel_posix_slash = rel_posix + "/"
    else:
        rel_posix_slash = rel_posix

    for pat in patterns:
        pat_clean = pat.rstrip("/")
        # Pattern che matchano il nome del file / cartella
        if fnmatch.fnmatch(name, pat_clean):
            return True
        # Pattern che matchano il path completo
        if fnmatch.fnmatch(rel_posix, pat_clean):
            return True
        if fnmatch.fnmatch(rel_posix_slash, pat):
            return True
        # Pattern con ** (glob ricorsivo semplificato)
        if pat.startswith("**/"):
            sub = pat[3:]
            if fnmatch.fnmatch(name, sub.rstrip("/")):
                return True
    return False


def is_binary_file(filepath: str, binary_extensions: set) -> bool:
    """Euristica per stabilire se un file è binario."""
    ext = pathlib.Path(filepath).suffix.lower()
    if ext in binary_extensions:
        return True
    # Prova a leggere i primi byte
    try:
        with open(filepath, "rb") as f:
            chunk = f.read(1024)
            if b"\x00" in chunk:
                return True
    except (OSError, PermissionError):
        return True
    return False


def read_file_content(filepath: str, max_file_size: int) -> str | None:
    """Legge il contenuto di un file testuale. Ritorna None se non leggibile."""
    try:
        size = os.path.getsize(filepath)
    except OSError:
        return None
    if size > max_file_size:
        return f"[FILE TROPPO GRANDE - {size} bytes]"
    try:
        with open(filepath, encoding="utf-8", errors="replace") as f:
            return f.read()
    except (OSError, PermissionError):
        return None


def is_snapshot_artifact(filepath: str, snapshot_path: str | None) -> bool:
    """Exclude only the configured snapshot and its adjacent temporary files."""
    if not snapshot_path:
        return False
    candidate = os.path.abspath(filepath)
    snapshot = os.path.abspath(snapshot_path)
    if candidate == snapshot:
        return True
    snapshot_name = os.path.basename(snapshot)
    return (
        os.path.dirname(candidate) == os.path.dirname(snapshot)
        and os.path.basename(candidate).startswith(f".{snapshot_name}.")
        and candidate.endswith(".tmp")
    )
def build_tree_lines(
    root_dir: str,
    gitignore_patterns: list[str],
    scanner_cfg: ScannerConfig,
    prefix: str = "",
    rel_base: str = "",
    snapshot_path: str | None = None,
) -> list[str]:
    """Costruisce le linee dell'albero tipo 'tree' per l'abstract."""
    tree: list[str] = []
    try:
        entries = sorted(os.listdir(root_dir))
    except PermissionError:
        return tree

    binary_exts = set(scanner_cfg.binary_extensions)

    dirs: list[tuple] = []
    files: list[str] = []
    for e in entries:
        full = os.path.join(root_dir, e)
        if is_snapshot_artifact(full, snapshot_path):
            continue
        rel = os.path.join(rel_base, e) if rel_base else e
        is_d = os.path.isdir(full)
        if e in scanner_cfg.skip_dirs:
            continue
        if is_ignored_by_gitignore(rel, gitignore_patterns, is_d):
            continue
        if is_d:
            dirs.append((e, full, rel))
        else:
            if not is_binary_file(full, binary_exts):
                files.append(e)

    all_items = (
        [(d[0], True, d[1], d[2]) for d in dirs]
        + [(f, False, None, None) for f in files]
    )  # type: ignore[assignment]
    for i, (name, is_d, full_path, rel_path) in enumerate(all_items):
        connector = "├── " if i < len(all_items) - 1 else "└── "
        if is_d:
            assert full_path is not None and rel_path is not None
            tree.append(f"{prefix}{connector}{name}/")
            extension = "│   " if i < len(all_items) - 1 else "    "
            tree.extend(
                build_tree_lines(
                    full_path,
                    gitignore_patterns,
                    scanner_cfg,
                    prefix + extension,
                    rel_path,
                    snapshot_path,
                )
            )
        else:
            tree.append(f"{prefix}{connector}{name}")
    return tree


def folder_to_xml(
    root_dir: str,
    gitignore_patterns: list[str],
    scanner_cfg: ScannerConfig,
    indent: int = 2,
    rel_base: str = "",
    snapshot_path: str | None = None,
) -> list[str]:
    """Converte ricorsivamente una cartella in nodi XML."""
    xml_lines: list[str] = []
    pad = " " * indent

    try:
        entries = sorted(os.listdir(root_dir))
    except PermissionError:
        return xml_lines

    binary_exts = set(scanner_cfg.binary_extensions)

    for entry in entries:
        full_path = os.path.join(root_dir, entry)
        if is_snapshot_artifact(full_path, snapshot_path):
            continue
        rel_path = os.path.join(rel_base, entry) if rel_base else entry
        is_d = os.path.isdir(full_path)

        # Salta cartelle note
        if entry in scanner_cfg.skip_dirs:
            continue
        if is_ignored_by_gitignore(rel_path, gitignore_patterns, is_d):
            continue

        if is_d:
            xml_lines.append(f'{pad}<fld name="{escape(entry)}">')
            xml_lines.extend(
                folder_to_xml(
                    full_path,
                    gitignore_patterns,
                    scanner_cfg,
                    indent + 2,
                    rel_path,
                    snapshot_path,
                )
            )
            xml_lines.append(f"{pad}</fld>")
        else:
            if is_binary_file(full_path, binary_exts):
                continue
            ext = pathlib.Path(entry).suffix.lstrip(".")
            if not ext:
                ext = "txt"
            content = read_file_content(full_path, scanner_cfg.max_file_size)
            if content is None:
                continue
            # Escape ]]> dentro CDATA (split trick)
            safe_content = content.replace("]]>", "]]]]><![CDATA[>")
            xml_lines.append(
                f'{pad}<file name="{escape(entry)}" ext="{escape(ext)}"><![CDATA[{safe_content}]]></file>'
            )

    return xml_lines


def generate_abstract(root_dir: str, tree_lines: list[str]) -> str:
    """Genera un abstract in Markdown che descrive il progetto."""
    from datetime import UTC, datetime

    project_name = os.path.basename(os.path.abspath(root_dir))
    readme_content: str | None = None
    for fname in ("README.md", "readme.md", "README.txt", "README"):
        rpath = os.path.join(root_dir, fname)
        if os.path.isfile(rpath):
            readme_content = read_file_content(rpath, 500 * 1024)
            break

    lines: list[str] = []
    lines.append(f"# Progetto: {project_name}\n")
    lines.append(
        f"**Data generazione contesto:** {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S %Z')}\n"
    )

    if readme_content:
        lines.append("## README originale\n")
        lines.append(readme_content.strip())
        lines.append("")

    lines.append("## Struttura del progetto\n")
    lines.append("```")
    lines.extend(tree_lines)
    lines.append("```\n")

    return "\n".join(lines)


def generate_project_xml(root_dir: str, config: Config) -> str:
    """Genera l'XML completo del progetto."""
    gitignore_patterns = load_gitignore_patterns(root_dir)
    scanner_cfg = config.scanner

    # 1. Costruisci albero per abstract
    snapshot_path = config.snapshot.output_path or None
    tree_lines = build_tree_lines(
        root_dir, gitignore_patterns, scanner_cfg, snapshot_path=snapshot_path
    )

    # 2. Genera abstract markdown
    abstract = generate_abstract(root_dir, tree_lines)

    # 3. Genera struttura XML
    xml_body = folder_to_xml(
        root_dir, gitignore_patterns, scanner_cfg, snapshot_path=snapshot_path
    )

    # 4. Assembla il documento
    safe_abstract = abstract.replace("]]>", "]]]]><![CDATA[>")
    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        "<progetto>",
        f'  <contesto><![CDATA[{safe_abstract}]]></contesto>',
        "  <struttura>",
    ]
    xml_lines.extend(xml_body)
    xml_lines.append("  </struttura>")
    xml_lines.append("</progetto>")

    return "\n".join(xml_lines)
