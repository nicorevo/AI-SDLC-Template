# Istruzioni per gli agenti

Questo progetto usa le skill e le persone definite in `.opencode/`.
Mantieni questo file specifico del progetto: descrive convenzioni, comandi e
vincoli che l'agente deve conoscere sempre. Le skill dettagliate stanno in
`.opencode/skills/` e vanno caricate on demand, non tutte insieme.

## Routing degli intenti

Identifica l'intento dell'utente e attiva l'agente e le skill corrispondenti
prima di eseguire qualsiasi operazione:

| Intento Utente | Agente Principale | Skill Obbligatorie | Output Atteso |
| :--- | :--- | :--- | :--- |
| Nuova Idea / Requisiti Vaghi | `software-architect` | `interview-me`, `idea-refine` | `docs/SPEC.md` raffinato |
| Specifiche / Architettura | `software-architect` | `spec-driven-development`, `api-and-interface-design`, `documentation-and-adrs` | `docs/SPEC.md`, contratti API, ADR |
| Breakdown Task / Stima | `tech-lead-planner` | `planning-and-task-breakdown` | `tasks/plan.md` con sotto-task verticali |
| Sviluppo Codice / Feature | `fullstack-developer` | `test-driven-development`, `incremental-implementation` | Codice testato + Commit Atomici |
| Test / QA / Coverage | `test-engineer` | `test-driven-development` | Test suite + analisi copertura |
| Bug / Errori / CI Fallita | `root-cause-debugger` | `debugging-and-error-recovery`, `browser-testing-with-devtools` | Riproduzione + Fix + Test di Regressione |
| Code Review / Merge | `code-reviewer` | `code-review-and-quality`, `code-simplification` | Report multi-asse con severità |
| Audit Sicurezza | `security-auditor` | `security-and-hardening` | Report vulnerabilità OWASP |
| Audit Performance Web | `web-performance-auditor` | `performance-optimization` | Scorecard Core Web Vitals |
| Release / Deploy / Migration | `release-engineer` | `shipping-and-launch`, `ci-cd-and-automation`, `observability-and-instrumentation` | Checklist Go/No-Go + Rollback Plan |

## Regole del ciclo di vita

Non saltare mai i passaggi del ciclo di vita a meno che non sia esplicitamente
richiesto dall'utente:

1. DEFINE FIRST: nessun codice di produzione senza `docs/SPEC.md` o un obiettivo chiaro.
2. PLAN IN SLICES: ogni feature divisa in fette verticali verificabili (`tasks/plan.md`).
3. TEST FIRST (TDD): prima il test che fallisce, poi il minimo codice per farlo passare.
4. NO UNVERIFIED CODE: non dichiarare completato un task senza aver eseguito test e lint nativi.
5. CLEAN COMMIT: commit piccoli e atomici con messaggi imperativi.

## Regole operative

- Leggi le istruzioni pertinenti prima di modificare il codice.
- Attiva solo le skill necessarie all'intento e alla superficie modificata.
- Mantieni le modifiche focalizzate e non introdurre dipendenze o architetture
  non richieste.
- Non inserire segreti nel repository e tratta i dati provenienti da utenti,
  file, API e agenti come non attendibili ai confini del sistema.

## Convenzioni del progetto

- Comandi di test, lint, build e avvio: documentali qui quando il progetto li
  stabilisce.
- Convenzioni generali: `CODING-STANDARDS.md`.
- Requisiti di sicurezza: `SECURITY.md`.

## Criteri di verifica

- Esegui la suite pertinente alle modifiche.
- Esegui lint e type-check quando previsti dallo stack.
- Controlla `git diff` e `git status --short`.
- Non includere cache, snapshot, credenziali o altri artefatti runtime.
