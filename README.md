# ai-sdlc-template

> Archetipo di progetto per Cursor — SDLC AI-augmented con skills Osmani
## Quick Start

1. Copia questa repo come base del tuo progetto
2. Rinomina la cartella e aggiorna `README.md`
3. Apri con Cursor: le skills in `.cursor/skills/` vengono auto-scoperte dall'agente
4. Avvia una sessione con `/spec` per definire cosa costruire

## Comandi SDLC (Osmani)

| Fase       | Comando          | Principio chiave         |
|------------|------------------|--------------------------|
| Define     | `/spec`          | Spec before code         |
| Plan       | `/plan`          | Small, atomic tasks      |
| Build      | `/build`         | One slice at a time      |
| Verify     | `/test`          | Tests are proof          |
| Review     | `/review`        | Improve code health      |
| Simplify   | `/code-simplify` | Clarity over cleverness  |
| Ship       | `/ship`          | Faster is safer          |

Pre:
Osmani Skills
Installa tutte le skills da riga di comando (opzionale)
npx skills add addyosmani/agent-skills --all --agent cursor

Java Skills
npx skills add jabrena/cursor-rules-java --all --agent cursor 

Github Tools
pip install pre-commit && pre-commit install

Vedi `docs/agent-skills/using-agent-skills.md` per come usare le skills.
