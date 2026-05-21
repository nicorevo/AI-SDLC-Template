# AGENTS.md — Istruzioni per AI Coding Agents

Questo file guida agenti come Cursor, Claude Code, Copilot nel rispetto del workflow SDLC.

## Workflow obbligatorio

1. **SEMPRE** inizia con `/spec` per nuove feature
2. **SEMPRE** scrivi test prima del codice (TDD)
3. **SEMPRE** esegui `/review` prima di proporre un merge
4. **MAI** committare codice senza tag `ai-generated` + review umana

## Skills attive

Le skills si trovano in `.cursor/skills/`. L'agente le usa automaticamente:
- `spec-driven-development` → attivata all'inizio di ogni feature
- `test-driven-development` → attivata su ogni modifica di logica
- `code-review-and-quality` → attivata prima di ogni merge
- `security-and-hardening` → attivata su input utente, auth, storage
- `git-workflow-and-versioning` → attivata su ogni commit
- `java-development` → attivata su codice Java/Maven/Spring

## Regole di comportamento

- Dimensione massima PR: ~100 righe di codice significativo
- Ogni commit deve essere atomico e compilabile
- Test pyramid: 80% unit / 15% integration / 5% e2e
- Documentare il PERCHÉ nelle ADR, non solo il COSA

## Tracciabilità AI

Ogni blocco di codice generato dall'AI deve includere:
```
// ai-generated: [tool] | human-reviewed: [yes/no] | date: YYYY-MM-DD
```
