#!/usr/bin/env python3
import os
import shutil
import subprocess
import sys


def crea_progetto_da_template(repo_url, nome_progetto):
    path_progetto = os.path.abspath(nome_progetto)

    # 1. Clone shallow (solo l'ultimo commit per essere veloci)
    print(f"📦 Clonazione del template in corso in: {nome_progetto}...")
    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", repo_url, nome_progetto], check=True
        )
    except subprocess.CalledProcessError:
        print("❌ Errore durante il git clone. Verifica l'URL.")
        return

    # 2. Rimozione della cartella .git originale
    git_dir = os.path.join(path_progetto, ".git")
    if os.path.exists(git_dir):
        print("🧹 Rimozione della vecchia cronologia Git...")
        shutil.rmtree(git_dir)

    # 3. Inizializzazione del nuovo repository Git
    print("🚀 Inizializzazione del nuovo repository...")
    try:
        subprocess.run(["git", "init"], cwd=path_progetto, check=True)
        subprocess.run(["git", "add", "."], cwd=path_progetto, check=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial commit dal template"],
            cwd=path_progetto,
            check=True,
        )
        print(f"🎉 Fatto! Il tuo nuovo progetto '{nome_progetto}' è pronto.")
        print(f"📂 Dai un'occhiata: cd {nome_progetto}")
    except subprocess.CalledProcessError:
        print(
            "⚠️ Qualcosa è andato storto con l'inizializzazione di Git, ma il codice è stato copiato."
        )


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python3 clona_template.py <URL_TEMPLATE> <NOME_NUOVO_PROGETTO>")
        sys.exit(1)

    url = sys.argv[1]
    nuovo_nome = sys.argv[2]
    crea_progetto_da_template(url, nuovo_nome)

