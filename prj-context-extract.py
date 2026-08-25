#!/usr/bin/env python3
"""
project_to_xml.py
Genera un file XML che descrive l'intero contenuto di un progetto.

Uso:
    python project_to_xml.py <cartella_progetto> [-o output.xml]

Struttura XML prodotta:
    <progetto>
        <contesto><![CDATA[ ... abstract in markdown ... ]]></contesto>
        <struttura>
            <fld name="nomecartella">
                <file ext="py"><![CDATA[ contenuto ]]></file>
                ...
            </fld>
        </struttura>
    </progetto>
"""

import os
import sys
import argparse
import fnmatch
import pathlib
from xml.sax.saxutils import escape


# ---------------------------------------------------------------------------
# Configurazione
# ---------------------------------------------------------------------------

# Cartelle da ignorare sempre
ALWAYS_SKIP_DIRS = {
    '.git', '__pycache__', 'node_modules', '.idea', '.vscode',
    '.metadata', 'target', 'dist', 'env', '.environment',
    'LOGS', '.settings', 'temp',
}

# Estensioni considerate binarie (non leggibili come testo)
BINARY_EXTENSIONS = {
    '.class', '.jar', '.war', '.exe', '.app', '.pyc', '.pyo', '.pyd',
    '.so', '.dll', '.dylib', '.o', '.a',
    '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.svg', '.webp',
    '.mp4', '.avi', '.mov', '.wmv', '.flv', '.tiff',
    '.zip', '.tar', '.gz', '.bz2', '.7z', '.rar',
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    '.woff', '.woff2', '.ttf', '.eot',
    '.db', '.sqlite', '.sqlite3',
    '.iml',
}

# Dimensione massima di un file da includere (500 KB)
MAX_FILE_SIZE = 500 * 1024


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def load_gitignore_patterns(root_dir: str) -> list[str]:
    """Carica i pattern dal .gitignore nella root del progetto."""
    gitignore_path = os.path.join(root_dir, '.gitignore')
    patterns = []
    if os.path.isfile(gitignore_path):
        with open(gitignore_path, encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    patterns.append(line)
    return patterns


def is_ignored_by_gitignore(rel_path: str, patterns: list[str], is_dir: bool) -> bool:
    """Controlla se un path relativo corrisponde a uno dei pattern .gitignore."""
    name = os.path.basename(rel_path)
    # Normalizza il path con /
    rel_posix = rel_path.replace('\\', '/')
    if is_dir:
        rel_posix_slash = rel_posix + '/'
    else:
        rel_posix_slash = rel_posix

    for pat in patterns:
        pat_clean = pat.rstrip('/')
        # Pattern che matchano il nome del file / cartella
        if fnmatch.fnmatch(name, pat_clean):
            return True
        # Pattern che matchano il path completo
        if fnmatch.fnmatch(rel_posix, pat_clean):
            return True
        if fnmatch.fnmatch(rel_posix_slash, pat):
            return True
        # Pattern con ** (glob ricorsivo semplificato)
        if pat.startswith('**/'):
            sub = pat[3:]
            if fnmatch.fnmatch(name, sub.rstrip('/')):
                return True
    return False


def is_binary_file(filepath: str) -> bool:
    """Euristica per stabilire se un file è binario."""
    ext = pathlib.Path(filepath).suffix.lower()
    if ext in BINARY_EXTENSIONS:
        return True
    # Prova a leggere i primi byte
    try:
        with open(filepath, 'rb') as f:
            chunk = f.read(1024)
            if b'\x00' in chunk:
                return True
    except (OSError, PermissionError):
        return True
    return False


def read_file_content(filepath: str) -> str | None:
    """Legge il contenuto di un file testuale. Ritorna None se non leggibile."""
    if os.path.getsize(filepath) > MAX_FILE_SIZE:
        return f"[FILE TROPPO GRANDE - {os.path.getsize(filepath)} bytes]"
    try:
        with open(filepath, encoding='utf-8', errors='replace') as f:
            return f.read()
    except (OSError, PermissionError):
        return None


# ---------------------------------------------------------------------------
# Generazione abstract / contesto
# ---------------------------------------------------------------------------

def generate_abstract(root_dir: str, tree_lines: list[str]) -> str:
    """Genera un abstract in Markdown che descrive il progetto."""
    project_name = os.path.basename(os.path.abspath(root_dir))
    readme_content = None
    for fname in ('README.md', 'readme.md', 'README.txt', 'README'):
        rpath = os.path.join(root_dir, fname)
        if os.path.isfile(rpath):
            readme_content = read_file_content(rpath)
            break

    lines = []
    lines.append(f"# Progetto: {project_name}\n")
    lines.append(f"**Data generazione contesto:** {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    if readme_content:
        lines.append("## README originale\n")
        lines.append(readme_content.strip())
        lines.append("")

    lines.append("## Struttura del progetto\n")
    lines.append("```")
    lines.extend(tree_lines)
    lines.append("```\n")

    return '\n'.join(lines)


# ---------------------------------------------------------------------------
# Generazione XML
# ---------------------------------------------------------------------------

def build_tree_lines(root_dir: str, gitignore_patterns: list[str],
                     prefix: str = '', rel_base: str = '') -> list[str]:
    """Costruisce le linee dell'albero tipo 'tree' per l'abstract."""
    tree = []
    try:
        entries = sorted(os.listdir(root_dir))
    except PermissionError:
        return tree

    dirs = []
    files = []
    for e in entries:
        full = os.path.join(root_dir, e)
        rel = os.path.join(rel_base, e) if rel_base else e
        is_d = os.path.isdir(full)
        if e in ALWAYS_SKIP_DIRS:
            continue
        if is_ignored_by_gitignore(rel, gitignore_patterns, is_d):
            continue
        if is_d:
            dirs.append((e, full, rel))
        else:
            if not is_binary_file(full):
                files.append(e)

    all_items = [(d[0], True, d[1], d[2]) for d in dirs] + [(f, False, None, None) for f in files]
    for i, (name, is_d, full_path, rel_path) in enumerate(all_items):
        connector = '├── ' if i < len(all_items) - 1 else '└── '
        if is_d:
            tree.append(f"{prefix}{connector}{name}/")
            extension = '│   ' if i < len(all_items) - 1 else '    '
            tree.extend(build_tree_lines(full_path, gitignore_patterns,
                                         prefix + extension, rel_path))
        else:
            tree.append(f"{prefix}{connector}{name}")
    return tree


def folder_to_xml(root_dir: str, gitignore_patterns: list[str],
                  indent: int = 2, rel_base: str = '') -> list[str]:
    """Converte ricorsivamente una cartella in nodi XML."""
    xml_lines = []
    pad = ' ' * indent

    try:
        entries = sorted(os.listdir(root_dir))
    except PermissionError:
        return xml_lines

    for entry in entries:
        full_path = os.path.join(root_dir, entry)
        rel_path = os.path.join(rel_base, entry) if rel_base else entry
        is_d = os.path.isdir(full_path)

        # Salta cartelle note
        if entry in ALWAYS_SKIP_DIRS:
            continue
        if is_ignored_by_gitignore(rel_path, gitignore_patterns, is_d):
            continue

        if is_d:
            xml_lines.append(f'{pad}<fld name="{escape(entry)}">')
            xml_lines.extend(folder_to_xml(full_path, gitignore_patterns,
                                           indent + 2, rel_path))
            xml_lines.append(f'{pad}</fld>')
        else:
            if is_binary_file(full_path):
                continue
            ext = pathlib.Path(entry).suffix.lstrip('.')
            if not ext:
                ext = 'txt'
            content = read_file_content(full_path)
            if content is None:
                continue
            # Escape ]]> dentro CDATA (split trick)
            safe_content = content.replace(']]>', ']]]]><![CDATA[>')
            xml_lines.append(f'{pad}<file name="{escape(entry)}" ext="{escape(ext)}"><![CDATA[{safe_content}]]></file>')

    return xml_lines


def generate_project_xml(root_dir: str, output_file: str) -> None:
    """Funzione principale: genera l'XML completo del progetto."""
    root_dir = os.path.abspath(root_dir)
    if not os.path.isdir(root_dir):
        print(f"Errore: '{root_dir}' non è una cartella valida.", file=sys.stderr)
        sys.exit(1)

    print(f"📂 Scansione progetto: {root_dir}")
    gitignore_patterns = load_gitignore_patterns(root_dir)
    print(f"📋 Pattern .gitignore caricati: {len(gitignore_patterns)}")

    # 1. Costruisci albero per abstract
    print("🌳 Generazione albero progetto...")
    tree_lines = build_tree_lines(root_dir, gitignore_patterns)

    # 2. Genera abstract markdown
    print("📝 Generazione abstract / contesto...")
    abstract = generate_abstract(root_dir, tree_lines)

    # 3. Genera struttura XML
    print("🔧 Generazione struttura XML...")
    xml_body = folder_to_xml(root_dir, gitignore_patterns)

    # 4. Assembla il documento
    safe_abstract = abstract.replace(']]>', ']]]]><![CDATA[>')
    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<progetto>',
        f'  <contesto><![CDATA[{safe_abstract}]]></contesto>',
        '  <struttura>',
    ]
    xml_lines.extend(xml_body)
    xml_lines.append('  </struttura>')
    xml_lines.append('</progetto>')

    xml_content = '\n'.join(xml_lines)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(xml_content)

    size_kb = os.path.getsize(output_file) / 1024
    print(f"✅ File XML generato: {output_file} ({size_kb:.1f} KB)")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Genera un file XML che descrive l\'intero contenuto di un progetto.'
    )
    parser.add_argument('cartella', help='Percorso della cartella del progetto')
    parser.add_argument('-o', '--output', default=None,
                        help='Nome del file XML di output (default: <nome_progetto>_context.xml)')

    args = parser.parse_args()

    if args.output is None:
        project_name = os.path.basename(os.path.abspath(args.cartella))
        args.output = f'{project_name}_context.xml'

    generate_project_xml(args.cartella, args.output)
