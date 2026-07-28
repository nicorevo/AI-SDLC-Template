# AI-SDLC Template

AI-driven software development lifecycle. Skills, agent personas, checklists, and evals for Claude Code, OpenCode, GitHub Copilot, and Cursor.

## TL;DR

- Load skills from `.opencode/skills/` to enforce TDD, review gates, security audits, and structured specification
- Agent personas in `.opencode/agents/` provide specialized perspectives (code review, security, testing, performance, architecture)
- GitHub symlink trick: `ln -sf .opencode .claude && ln -sf .opencode .github` makes everything available to Claude Code and Copilot from one place
- Coding standards across 4 stacks: Java/Spring, C#/ASP.NET, Node/TypeScript, Python/FastAPI → see `CODING-STANDARDS.md`

## Structure

```
├── .opencode/              # Core: skills, agents, guides, hooks, evals
│   ├── skills/             # 25 skills (spec-driven-development, test-driven-development, etc.)
│   ├── agents/             # 9 agent personas + AGENTS.md routing table
│   ├── guide/              # Setup guides (OpenCode, Copilot, adoption paths, onboarding)
│   ├── references/         # Checklists (security, testing, performance, accessibility, observability)
│   ├── evals/              # Tier 1-3 evaluation framework for skills
│   ├── hooks/              # Session-start and WebFetch caching hooks
│   └── copilot-instruction.md
├── AGENTS.md               # Agent intent routing + lifecycle rules (this repo)
├── CLAUDE.md               # Verification commands for Claude Code
├── CODING-STANDARDS.md     # Language-specific conventions (Java, C#, Node, Python)
├── SECURITY.md             # Vulnerability reporting, data classification, OWASP rules
├── clona-ai-sdlc-template.py  # Clone-and-adapt this template for new projects
└── scripts/                # Validation scripts (validate-skills, run-evals, validate-commands)
```

## Quick Start

### Use in a new project

```bash
# Clone this template
python3 clona-ai-sdlc-template.py https://github.com/your-org/AI-SDLC-Template my-project

# Make skills visible to AI tools
cd my-project
ln -sf .opencode .claude
ln -sf .opencode .github
```

### Use in an existing project

```bash
# Create symlinks pointing to this template
ln -sf /path/to/AI-SDLC-Template/.opencode .claude
ln -sf /path/to/AI-SDLC-Template/.opencode .github
```

### Development workflow (guided by intent)

The agent auto-routes to the right skill based on your request. Full routing table from [AGENTS.md](AGENTS.md):

| Intent                              | Agent              | Skills                              | Output                                  |
| :---                                | :---               | :---                                | :---                                    |
| New idea / vague requirements       | `software-architect` | `interview-me`, `idea-refine`        | Refined `SPEC.md`                       |
| Specs / architecture                | `software-architect` | `spec-driven-development`, `api-and-interface-design`, `documentation-and-adrs` | `SPEC.md`, API contracts, ADR |
| Task breakdown / estimation         | `tech-lead-planner` | `planning-and-task-breakdown`         | `tasks/plan.md` with vertical subtasks  |
| Code development / features         | `fullstack-developer` | `test-driven-development`, `incremental-implementation` | Tested code + atomic commits |
| Bug / errors / CI failure           | `root-cause-debugger` | `debugging-and-error-recovery`, `browser-testing-with-devtools` | Reproduction + fix + regression tests |
| Code review / merge                 | `code-reviewer`     | `code-review-and-quality`, `code-simplification` | Multi-axis review report |
| Security audit                      | `security-auditor`  | `security-and-hardening`              | OWASP vulnerability report              |
| Web performance audit               | `web-performance-auditor` | `performance-optimization`         | Core Web Vitals scorecard               |
| Release / deploy / migration        | `release-engineer`  | `shipping-and-launch`, `ci-cd-and-automation`, `observability-and-instrumentation` | Go/No-Go checklist + rollback plan |

No slash commands needed in OpenCode — intent mapping handles routing automatically.

## Lifecycle

Every task flows through these phases (agent enforces, never skips). Full rules from [AGENTS.md](AGENTS.md):

```
DEFINE → PLAN → BUILD → VERIFY → REVIEW → SHIP
```

### 5 Non-Negotiable Rules

| #   | Rule             | What it means                                                  |
| :--- | :---           | :---                                                           |
| 1   | **DEFINE FIRST**  | No production code without a `SPEC.md` or clear objective      |
| 2   | **PLAN IN SLICES**| Every feature split into thin, verifiable vertical slices (`tasks/plan.md`) |
| 3   | **TEST FIRST**    | Write the failing test first, then the minimal code to make it pass |
| 4   | **NO UNVERIFIED** | Task not "done" until native test suite runs clean             |
| 5   | **CLEAN COMMIT**  | Small, atomic commits with imperative messages                 |

- **DEFINE**: `SPEC.md` before production code
- **PLAN**: Vertical slices in `tasks/plan.md`
- **BUILD**: TDD — failing test first, minimal implementation, commit atomic
- **VERIFY**: Run native test suite; no unverified code
- **REVIEW**: Five-axis review (correctness, design, readability, security, performance)
- **SHIP**: Go/No-Go checklist + rollback plan

## Language Stacks

| Stack | Key Versions | Lint/Format | Test |
| :--- | :--- | :--- | :--- |
| **Java** | JDK 21, Spring Boot 3.x, Maven | — | JUnit 5 + AssertJ + Mockito |
| **C#** | .NET 8, ASP.NET Core 8.x | — | xUnit + FluentAssertions + Moq |
| **Node.js** | Node 22 LTS, TS 5.x strict | ESLint flat + Prettier | Vitest + Supertest |
| **Python** | 3.12+, FastAPI 0.11x | Ruff (no type: ignore sans comment) | pytest + httpx |

Common rules: 500 lines/file max, atomic commits, no secrets in code, OpenAPI-first REST. → `CODING-STANDARDS.md`

## Skills Reference (25)

`spec-driven-development`, `test-driven-development`, `planning-and-task-breakdown`, `incremental-implementation`, `code-review-and-quality`, `debugging-and-error-recovery`, `security-and-hardening`, `code-simplification`, `frontend-ui-engineering`, `api-and-interface-design`, `documentation-and-adrs`, `git-workflow-and-versioning`, `shipping-and-launch`, `ci-cd-and-automation`, `observability-and-instrumentation`, `performance-optimization`, `deprecation-and-migration`, `context-engineering`, `doubt-driven-development`, `tech-stack-skill-installer`, `browser-testing-with-devtools`, `interview-me`, `idea-refine`, `using-agent-skills`, `software-architect` (agent).

Load selectively per phase — all 25 in one session wastes context. → `.opencode/skills/` and `guide/`

## Contributing to this Template

See `guide/developer-onboarding.md` for the full contribution workflow.

```bash
# Structural validation (frontmatter, naming, required sections)
node scripts/validate-skills.js

# Command parity across Claude/Gemini/Antigravity directories
node scripts/validate-commands.js

# Trigger & routing evals (Tier 2 — lexical TF-IDF)
node scripts/run-evals.js

# Hook regression test (required if touching hooks/ or using-agent-skills)
bash hooks/session-start-test.sh
```

- Skills live in `skills/<name>/SKILL.md` with YAML frontmatter, step-by-step workflow, and verification gates
- Personals live in `agents/<role>.md` with a single perspective and output format
- Personas never call other personas; slash commands compose them
- English only — translations drift

## Resources

| Location | Contents |
| :--- | :--- |
| `guide/getting-started.md` | Universal setup and skill anatomy |
| `guide/adoption-guide.md` | Greenfield vs. brownfield rollout paths |
| `guide/opencode-setup.md` | OpenCode-specific configuration |
| `guide/copilot-setup.md` | GitHub Copilot integration |
| `guide/developer-onboarding.md` | Contributing to this repo |
| `references/` | Security, testing, performance, accessibility, observability checklists |
| `SECURITY.md` | Data classification, vulnerability reporting, OWASP rules |
