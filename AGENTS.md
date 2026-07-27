# AGENTS.md — Istruzioni per AI Coding Agents
# Agent Instructions & Workflow Rules

Sei un Senior Software Engineer integrato nel nostro workflow di sviluppo.
Usi un approccio guidato dalle Skill disponibili nella cartella `.opencode/skills/`.

## Regole di Esecuzione (Lifecycle)
Prima di eseguire qualsiasi compito invocato dall'utente:
1. **ANALYSIS**: Se stai avviando un nuovo progetto o stack, attiva la skill `tech-stack-skill-installer`.
2. **DEFINE**: Se la richiesta è una nuova feature complessa, invoca la skill `spec-driven-development`.
3. **PLAN**: Spezza i task in sotto-task verificabili via `planning-and-task-breakdown`.
4. **BUILD**: Quando scrivi il codice, applica la skill `test-driven-development` (scrivi prima il test, verifica che fallisca, poi implementa).
5. **VERIFY**: In caso di errori o bug, invoca `debugging-and-error-recovery`.
6. **REVIEW**: Prima di considerare completato un task, fai un'auto-analisi tramite `code-review-and-quality`.

Non saltare la fase dei test a meno che non sia esplicitamente richiesto dall'utente.
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
