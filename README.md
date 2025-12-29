# Claude Code Skills

Personal skills for [Claude Code](https://claude.ai/code).

## Skills

### explaining-code

Explains code with visual diagrams and analogies. When active, Claude will:

1. Start with an everyday analogy
2. Draw ASCII or mermaid diagrams
3. Walk through the code step-by-step
4. Highlight common gotchas

## Usage

To use these skills, clone this repo to `~/.claude/skills/`:

```bash
git clone https://github.com/nunomen/claude-skills.git ~/.claude/skills
```

## Creating Skills

Each skill is a directory containing a `SKILL.md` file with YAML frontmatter:

```yaml
---
name: skill-name
description: When to use this skill
---

Instructions for Claude...
```

See [Claude Code documentation](https://docs.anthropic.com/en/docs/claude-code) for more details.
