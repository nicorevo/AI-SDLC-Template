---
name: tech-stack-skill-installer
description: Analizza il repository, individua lo stack tecnologico (linguaggi, framework, DB, tool di test) e importa o genera le skill più utili in .agents/skills/
---

# Tech Stack Skill Installer & Analyzer

Quando l'utente invoca questa skill (es. "Analizza lo stack e importa le skill utili" o "Configura le skill per questo progetto"):

## Fase 1: Analisi dello Stack Tecnologico
Ispeziona la radice del progetto e le sottocartelle per identificare i file di configurazione e dipendenza:
- **Node.js / JS / TS**: `package.json`, `tsconfig.json`
- **Python**: `pyproject.toml`, `requirements.txt`, `Pipfile`, `Pipfile.lock`
- **Go**: `go.mod`
- **Rust**: `Cargo.toml`
- **PHP**: `composer.json`
- **Java/Kotlin**: `pom.xml`, `build.gradle`
- **Database & Infra**: `docker-compose.yml`, `Dockerfile`, file `.env.example`, schemi Prisma/Drizzle/SQLAlchemy
- **Testing**: Configs di `jest`, `vitest`, `pytest`, `playwright`, ecc.

Compila un elenco dello stack rilevato:
1. **Linguaggio e Runtime** (es. TypeScript Node v20, Python 3.11)
2. **Framework Principale** (es. Next.js App Router, FastAPI, Spring Boot)
3. **Database e ORM** (es. PostgreSQL con Prisma)
4. **Tool di Testing & QA** (es. Vitest, PyTest, ESLint)

## Fase 2: Verifica Skill Esistenti
Controlla quali skill sono già presenti nella cartella `.agents/skills/` per evitare duplicati.

## Fase 3: Ricerca e Importazione Skill
Per ogni tecnologia chiave identificata che non ha ancora una skill associata:

1. **Importazione da fonti note**:
   Se disponibile tramite CLI o repository noti (es. `addyosmani/agent-skills` o `agentskills/agentskills`), esegui il comando via terminale per scaricarla:
   ```bash
   npx skills add <nome-repo/skill>