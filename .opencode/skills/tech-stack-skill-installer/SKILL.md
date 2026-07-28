---
name: tech-stack-skill-installer
description: Automates discovering, fetching, and installing specialized skills, agent personas, and tech-stack rules from curated external catalogs (anthropics/skills, spencerpauly/awesome-cursor-skills, mskadu/opencode-agent-skills, cursor.directory) into .opencode/.
---

# Tech-Stack & Skill Installer

## Overview

Dynamically expand your AI development environment by discovering, fetching, and installing new skills, agent personas, and stack-specific guidelines. It pulls from trusted open-source catalogs, validates their Markdown format, and places them inside `.opencode/` while maintaining symlink compatibility with `.claude` and `.github`.

## When to Use

- Onboarding a new project with a specific framework or tech stack (e.g., Spring Boot, FastAPI, Next.js, Go).
- Needing advanced execution patterns like continuous test grinding (`grinding-until-pass`) or parallel exploration (`parallel-exploring`).
- Adding automated workflow tools (e.g., `smart-git-automation`, `anti-sycophancy`).
- Expanding agent roles beyond the default AI-SDLC set.

---

## 📚 Curated External Catalogs

When searching for new skills or agents, query these official and community sources:

| Catalog Source | URL / Repository | Best Used For | Target Installation Path |
| :--- | :--- | :--- | :--- |
| **Anthropic Official Skills** | `anthropics/skills` | Standard workflows, MCP servers, testing, documentation | `.opencode/skills/<skill-name>/SKILL.md` |
| **Awesome Cursor Skills** | `spencerpauly/awesome-cursor-skills` | Execution patterns (`grinding-until-pass`, `parallel-exploring`, visual QA) | `.opencode/skills/<skill-name>/SKILL.md` |
| **OpenCode Agent Skills** | `mskadu/opencode-agent-skills` | OpenCode-native utilities (`smart-git-automation`, `anti-sycophancy`, `skill-suggester`) | `.opencode/skills/<skill-name>/SKILL.md` |
| **Cursor Directory** | `cursor.directory` / `awesome-cursorrules` | Framework-specific coding standards (FastAPI, React, Spring, etc.) | `.opencode/skills/stack-<name>/SKILL.md` or `AGENTS.md` |

---

## 🛠️ Installation & Integration Process

Follow this 5-step process when installing new skills or agent personas:

### Step 1: Identify Stack or Capability Gap
Determine the missing capability by inspecting project dependencies (`pom.xml`, `package.json`, `requirements.txt`) or user requests.
- *Example Ask:* "I need a skill to auto-generate conventional git commits and PRs for OpenCode."

### Step 2: Fetch from Target Catalog
Download the target `.md` file directly using `curl`, `gh` CLI, or WebFetch.

```bash
# Example: Fetching smart-git-automation from opencode-agent-skills
mkdir -p .opencode/skills/smart-git-automation
curl -sSL "[https://raw.githubusercontent.com/mskadu/opencode-agent-skills/main/skills/smart-git-automation/SKILL.md](https://raw.githubusercontent.com/mskadu/opencode-agent-skills/main/skills/smart-git-automation/SKILL.md)" \
  -o .opencode/skills/smart-git-automation/SKILL.md
```

### Step 3: Format & Structure Validation
Ensure the fetched file complies with Addy Osmani's standard:
1. **Valid YAML Frontmatter:** Must contain `name` and `description`.
2. **No Nested Agent Spawning:** Agent personas must not call other agent personas.
3. **Skill Target Path:** `.opencode/skills/<skill-name>/SKILL.md`.
4. **Agent Target Path:** `.opencode/agents/<agent-name>.md`.

### Step 4: Register in `AGENTS.md` (Intent Routing)
If the new skill or agent provides a core workflow capability, update the **Intent Routing Table** in `AGENTS.md` so OpenCode and Copilot can trigger it automatically:

```markdown
| Intento Utente | Agente Principale | Skill Obbligatorie | Output Atteso |
| :--- | :--- | :--- | :--- |
| **Git Commit/PR Automativo** | `fullstack-developer` | `smart-git-automation` | Commit atomici e descrittivi |
```

### Step 5: Verify Symlinks
Ensure that files written to `.opencode/` are instantly visible to `.claude/` and `.github/`:

```bash
# Verify symlink integrity
ls -la .claude .github
```
*Expected output: `.claude -> .opencode` and `.github -> .opencode`.*

---

## ⚠️ Anti-Patterns & Boundaries

- **NEVER** edit files directly inside `.claude/` or `.github/` when installing skills; always write to `.opencode/` (the Single Source of Truth).
- **NEVER** install executable binary scripts or unverified dependencies without user confirmation.
- **NEVER** overwrite existing core AI-SDLC skills (`spec-driven-development`, `test-driven-development`, etc.) unless explicitly instructed.

---

## ✅ Verification Checklist

After running `tech-stack-skill-installer`:

- [ ] New skill/agent file exists in `.opencode/skills/` or `.opencode/agents/`.
- [ ] YAML frontmatter contains valid `name` and `description`.
- [ ] The skill is accessible via `.claude/` and `.github/` through symlinks.
- [ ] `AGENTS.md` has been updated with the new intent-routing entry.
- [ ] OpenCode/Copilot can successfully discover and execute the newly installed skill.