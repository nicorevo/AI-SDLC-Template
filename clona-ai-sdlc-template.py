#!/usr/bin/env python3
import argparse
import os
import shutil
import subprocess
import sys


SOURCE_BRANCH = "opcl"
TARGET_BRANCH = "main"

# Materiale utile per mantenere il template, ma non necessario nei progetti
# applicativi generati dal cloner.
TEMPLATE_ONLY_PATHS = (
    ".opencode/evals",
    ".opencode/guide",
    ".opencode/hooks",
    ".opencode/plans",
    "codesync",
    "prj-context-extract.py",
    "clona-ai-sdlc-template.py",
)

# ai-generated: Codex | human-reviewed: no | date: 2026-08-09


def ottieni_remote_origin(cwd="."):
    """Tenta di leggere l'URL del remote origin del repository corrente."""
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except Exception:
        return None


def chiedi_input(messaggio, default=None):
    """Richiede un input all'utente con un valore di default opzionale."""
    if default:
        prompt = f"{messaggio} [{default}]: "
    else:
        prompt = f"{messaggio}: "

    risposta = input(prompt).strip()
    return risposta if risposta else default


def rimuovi_file_template(path_progetto):
    """Rimuove dal progetto clonato il materiale interno al template."""
    for relative_path in TEMPLATE_ONLY_PATHS:
        target = os.path.join(path_progetto, relative_path)
        if os.path.islink(target) or os.path.isfile(target):
            os.unlink(target)
        elif os.path.isdir(target):
            shutil.rmtree(target)


def crea_progetto_da_template(repo_url, nome_progetto, destinazione):
    # 1. Clone shallow (solo l'ultimo commit per essere veloci)
    print(f"\n📦 Clonazione del template in corso...")
    print(f"   URL:   {repo_url}")
    print(f"   Dest:  {os.path.join(destinazione, nome_progetto)}\n")

    path_progetto = os.path.abspath(os.path.join(destinazione, nome_progetto))

    try:
        subprocess.run(
            [
                "git",
                "clone",
                "--depth",
                "1",
                "--branch",
                SOURCE_BRANCH,
                "--single-branch",
                repo_url,
                nome_progetto,
            ],
            cwd=destinazione,
            check=True,
        )
    except subprocess.CalledProcessError:
        print("❌ Errore durante il git clone. Verifica l'URL.")
        return

    print("🧹 Rimozione del materiale interno al template...")
    rimuovi_file_template(path_progetto)

    # 2. Rimozione della cartella .git originale
    git_dir = os.path.join(path_progetto, ".git")
    if os.path.exists(git_dir):
        print("🧹 Rimozione della vecchia cronologia Git...")
        shutil.rmtree(git_dir)

    # 3. Inizializzazione del nuovo repository Git
    print("🚀 Inizializzazione del nuovo repository...")
    try:
        subprocess.run(
            ["git", "init", "-b", TARGET_BRANCH], cwd=path_progetto, check=True
        )
        subprocess.run(["git", "add", "."], cwd=path_progetto, check=True)

        # Configura user per il commit se non presente
        subprocess.run(
            ["git", "config", "user.name", "Developer"],
            cwd=path_progetto,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.email", "dev@example.com"],
            cwd=path_progetto,
            check=True,
            capture_output=True,
        )

        subprocess.run(
            ["git", "commit", "-m", "Initial commit dal template"],
            cwd=path_progetto,
            check=True,
        )

        print(f"\n{'='*50}")
        print(f"🎉 Fatto! Il tuo nuovo progetto è pronto.")
        print(f"{'='*50}")
        print(f"📂 Percorso: {path_progetto}")
        print(f"👉 cd {path_progetto}")

    except subprocess.CalledProcessError:
        print(
            "⚠️ Qualcosa è andato storto con l'inizializzazione di Git, ma il codice è stato copiato."
        )


def main(argv=None):
    parser = argparse.ArgumentParser(description="Clona il template AI-SDLC")
    parser.add_argument("url", nargs="?", help="URL del repository template")
    parser.add_argument("nome", nargs="?", help="Nome del nuovo progetto")
    parser.add_argument(
        "destinazione",
        nargs="?",
        help="Cartella che conterrà il nuovo progetto",
    )
    args = parser.parse_args(argv)

    print("=" * 50)
    print("  AI-SDLC Template Cloner")
    print("=" * 50)

    # Rileva automaticamente l'URL del template dal repo dove si trova lo script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    url_template = ottieni_remote_origin(script_dir)

    # Input interattivo
    url = args.url or chiedi_input("📡 URL del template Git", url_template)
    if not url:
        print("❌ L'URL del template è obbligatorio. Exiting.")
        sys.exit(1)

    # Suggerisci nome dal nome della cartella del repo
    repo_name = url.rstrip("/").split("/")[-1].replace(".git", "")
    nome = args.nome or chiedi_input("✨ Nome del nuovo progetto", repo_name)
    nome = nome if nome else repo_name

    dest = args.destinazione or chiedi_input("📁 Cartella di destinazione", ".")

    print()
    crea_progetto_da_template(url, nome, dest)


if __name__ == "__main__":
    main()
