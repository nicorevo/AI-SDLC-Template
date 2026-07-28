# AI-SDLC Agent Routing & Rules (Single Source of Truth)

Sei un sistema di sviluppo software avanzato basato sulle Skill e gli Agenti definiti in `.opencode/`.
Istruisci OpenCode e GitHub Copilot a rispettare rigorosamente il ciclo di vita del software (AI-SDLC) e ad invocare le skill corrette dalla cartella `.opencode/skills/`.

---

## Intent Routing Table

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

## Lifecycle Discipline

Non saltare mai i passaggi del ciclo di vita a meno che non sia esplicitamente richiesto dall'utente:

1. **DEFINE FIRST**: Nessun codice di produzione senza un file `SPEC.md` o obiettivo chiaro.
2. **PLAN IN SLICES**: Ogni feature divisa in fette verticali verificabili (`tasks/plan.md`).
3. **TEST FIRST (TDD)**: Scrivi prima il test che dimostra il fallimento, poi implementa il minimo per farlo passare.
4. **NO UNVERIFIED CODE**: Non dichiarare completato un task senza aver eseguito i test nativi del progetto.
5. **CLEAN COMMIT**: Commit piccoli e atomici con messaggi imperativi.

---

## Skills e Agenti

Le skill sono nella cartella `.opencode/skills/` (25 directory). L'agente le attiva automaticamente via intent routing.

Agenti persona in `.opencode/agents/`:
- `code-reviewer` — five-axis review
- `fullstack-developer` — code implementation via TDD
- `release-engineer` — CI/CD, pre-launch, migrations
- `root-cause-debugger` — systematic bug triage
- `security-auditor` — OWASP-style vulnerability audit
- `software-architect` — specs, domain modeling, API contracts, ADRs
- `tech-lead-planner` — task breakdown and plan.md generation
- `test-engineer` — QA test strategy and coverage analysis
- `web-performance-auditor` — Core Web Vitals audit

**Regole:**
- Gli agenti non invocano altri agenti. La composizione è compito dei comandi slash o dell'utente.
- Gli agenti invocano skill come step obbligati del loro workflow.
- Massimo 100 righe di codice significativo per PR, commit atomici compilabili.
- Test pyramid: 80% unit / 15% integration / 5% e2e.

---

## Coding Standards

Riferimento: `CODING-STANDARDS.md`. Ogni lingua: max 500 righe/file, commenta il PERCHÉ non il COSA, commit atomici, zero secret nel codice, OpenAPI-first per API REST.

| Lingua | Versione | Build | Framework | Test |
| :--- | :--- | :--- | :--- | :--- |
| Java | 21+ | Maven | Spring Boot 3.x | JUnit 5 + AssertJ + Mockito |
| C# | .NET 8+ | `dotnet` CLI | ASP.NET Core 8.x | xUnit + FluentAssertions + Moq |
| Node.js | 22 LTS + TS 5.x | npm | Express 5.x / Fastify 4.x | Vitest + Supertest |
| Python | 3.12+ | uv | FastAPI 0.11x + Typer | pytest + httpx |

---

## Tracciabilità AI

Ogni blocco di codice generato dall'agente deve includere:

```
// ai-generated: [tool] | human-reviewed: [yes/no] | date: YYYY-MM-DD
```

---

## Setup rapido per nuovi progetti

```bash
python3 clona-ai-sdlc-template.py <URL_TEMPLATE> <NOME_PROGETTO>
```

Dopo la clonazione, crea i symlink per Copilot/Claude:

```bash
ln -sf .opencode .claude
ln -sf .opencode .github
```

---

## Risorse

- **Guide**: `.opencode/guide/` (getting-started, adoption, opencode-setup, copilot-setup, developer-onboarding)
- **Referenze**: `.opencode/references/` (checklists sicurezza, testing, performance, accessibility, observability, definition-of-done)
- **Evals**: `.opencode/evals/` (framework di valutazione tier 1-3)
- **Hooks**: `.opencode/hooks/` (session-start, WebFetch caching)
- **Security**: `SECURITY.md` (data classification, OWASP Top 10, dependency audit)
