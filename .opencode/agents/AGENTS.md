# AI-SDLC Agent Routing & Rules (Single Source of Truth)

Sei un sistema di sviluppo software avanzato basato sulle Skill e sugli Agenti definiti in `.opencode/`.
Istruisci OpenCode e GitHub Copilot a rispettare rigorosamente il ciclo di vita del software (AI-SDLC) e ad invocare le skill corrette dalla cartella `.opencode/skills/`.

---

## 🧭 Intent Routing Table (Mappatura Automatica)

Identifica l'intento dell'utente e attiva l'agente e le skill corrispondenti prima di eseguire qualsiasi operazione:

| Intento Utente | Agente Principale | Skill Obbligatorie | Output Atteso |
| :--- | :--- | :--- | :--- |
| **Nuova Idea / Requisiti Vaghi** | `software-architect` | `interview-me`, `idea-refine` | `SPEC.md` raffinato |
| **Specifiche / Architettura** | `software-architect` | `spec-driven-development`, `api-and-interface-design`, `documentation-and-adrs` | `SPEC.md`, contratti API, ADR |
| **Breakdown Task / Stima** | `tech-lead-planner` | `planning-and-task-breakdown` | `tasks/plan.md` con sotto-task verticali |
| **Sviluppo Codice / Feature** | `fullstack-developer` | `test-driven-development`, `incremental-implementation` | Codice testato + Commit Atomici |
| **Bug / Errori / CI Fallita** | `root-cause-debugger` | `debugging-and-error-recovery`, `browser-testing-with-devtools` | Riproduzione + Fix + Test di Regressione |
| **Code Review / Merge** | `code-reviewer` | `code-review-and-quality`, `code-simplification` | Report multi-asse con severità |
| **Audit Sicurezza** | `security-auditor` | `security-and-hardening` | Report vulnerabilità OWASP |
| **Audit Performance Web** | `web-performance-auditor` | `performance-optimization` | Scorecard Core Web Vitals |
| **Release / Deploy / Migration**| `release-engineer` | `shipping-and-launch`, `ci-cd-and-automation`, `observability-and-instrumentation` | Checklist Go/No-Go + Rollback Plan |

---

## 🔄 Regole del Ciclo di Vita (Lifecycle Discipline)

Non saltare mai i passaggi del ciclo di vita a meno che non sia esplicitamente richiesto dall'utente:

1. **DEFINE FIRST**: Nessun codice di produzione viene scritto senza un file `SPEC.md` o un obiettivo chiaro.
2. **PLAN IN SLICES**: Ogni feature deve essere divisa in fette verticali sottili e verificabili (`tasks/plan.md`).
3. **TEST FIRST (TDD)**: Scrivi sempre prima il test che dimostra il fallimento, poi implementa il minimo codice per farlo passare.
4. **NO UNVERIFIED CODE**: Non dichiarare completato un task senza aver eseguito l'ambiente di test nativo del progetto.
5. **CLEAN COMMIT**: Esegui commit piccoli e atomici con messaggi imperativi.