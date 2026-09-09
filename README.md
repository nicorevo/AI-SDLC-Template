# AI-SDLC Template

Template for bootstrapping new projects with skills, agents and conventions
for AI-assisted development. The main operational material lives in
`.opencode/`.

## Abstract

AI-SDLC Template imposes a structured, quality-gated software development
lifecycle on AI coding agents. Every user intent is routed through a mapping
table (`AGENTS.md`) to a specialized agent persona, a set of mandatory skills
and an expected deliverable: specification and ADRs, vertical task plans,
tested code with atomic commits, multi-axis review reports, security and
performance audits, release checklists. The lifecycle rules are binding —
the agent must never skip them unless explicitly told to: define first (no
production code without `docs/SPEC.md`), plan in verifiable vertical slices,
test first (TDD), never claim a task done without running the native tests
and linters, commit small and atomically. Skills are loaded on demand per
intent, never all at once, and the key phases of the workflow are gated by
human review (SPECIFY → PLAN → TASKS → IMPLEMENT).

The template is OpenCode-native — the operational material (skills, agents,
commands, references) lives in `.opencode/` and is loaded automatically by
opencode — but it is designed to work with any agent. `linkToOthers.txt`
provides the symlink recipes to expose the same material as `.claude`,
`.agents`, `.cursor` and `.github`; `.vscode/settings.json` binds GitHub
Copilot to the workflow defined in `AGENTS.md`; `.serena/project.yml` adds
Serena support; and the root `AGENTS.md` follows the vendor-neutral AGENTS.md
convention as the single source of truth for intent routing, so other
agentic tools pick up the same rules without modification.

## What is used in new projects

- `.opencode/skills/`: workflows loaded on demand, e.g. specifications,
  TDD, debugging, security and code review;
- `.opencode/agents/`: specialized personas and intent routing;
- `.opencode/references/`: checklists consulted by the skills;
- `AGENTS.md`: project-specific rules, to be completed with commands and
  conventions of the stack.

Skills must not all be loaded in a single session: the agent picks the ones
relevant to the task.

## Creating a new project

Non-interactive mode:

```bash
python3 clona-ai-sdlc-template.py TEMPLATE_URL PROJECT_NAME DESTINATION
```

Interactive mode:

```bash
python3 clona-ai-sdlc-template.py
```

The cloner uses the `opcl` branch, removes the template's Git history,
initializes a new repository on the `main` branch and deletes the
template-internal artifacts that the application project does not need.

## Recommended workflow

1. Define the goal and the constraints.
2. Plan the work in verifiable slices.
3. Implement with relevant tests and incremental changes.
4. Verify tests, lint and runtime behavior.
5. Run review and security checks before merging.

For detailed routing see `AGENTS.md`.

## Conventions

- `CODING-STANDARDS.md` collects the shared per-language conventions; keep
  only the useful ones
- `SECURITY.md` collects the security requirements.
- Project-specific verification commands go into `AGENTS.md` in the new
  project.
- This file can be rewritten with the new project's scope.

## Template repository tooling

The template repository also contains maintenance tools and the optional
`codesync/` service. These components serve template development and are not
copied into new projects by the cloner. codesync provides an XML snapshot of
the entire project.

## Credits

The skills in `.opencode/skills/` are derived from
[agent-skills](https://github.com/addyosmani/agent-skills) by
[Addy Osmani](https://github.com/addyosmani), MIT License, © 2025.
See `.opencode/skills/NOTICE.md` for the full notice and license text.

A heartfelt thank you to Addy for the work he has done for the community:
his skills proved useful to this project from day one, and he is probably
the strongest contributor to public knowledge in this field.
