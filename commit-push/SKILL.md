---
name: commit-push
description: "Commit and push changes with gitmoji-style messages. Triggers on '/commit-push' or phrases like 'commit and push', 'save my changes', 'push this'."
model: claude-haiku-4-5-20241022
---

# Commit and Push

When the user wants to commit and push changes (detected via `/commit-push` command or phrases like "commit and push", "save my changes", "push this", "commit this"), follow this workflow:

## 1. Gather Context

Run these commands in parallel:
```bash
git status
git diff --staged
git diff
git log --oneline -5
```

## 2. Stage Changes

If there are unstaged changes the user likely wants committed:
```bash
git add -A
```

If unsure which files to include, ask the user.

## 3. Write Commit Message

Use **gitmoji** style with this format:
```
<emoji> <type>: <short description>

<optional body explaining what and why>
```

### Gitmoji Reference

| Emoji | Code | Use for |
|-------|------|---------|
| ✨ | `:sparkles:` | New feature |
| 🐛 | `:bug:` | Bug fix |
| 🔧 | `:wrench:` | Configuration |
| 📝 | `:memo:` | Documentation |
| ♻️ | `:recycle:` | Refactor |
| 🎨 | `:art:` | Style/format |
| ⚡ | `:zap:` | Performance |
| 🔒 | `:lock:` | Security |
| 🧪 | `:test_tube:` | Tests |
| 🚀 | `:rocket:` | Deploy |
| 🗑️ | `:wastebasket:` | Remove code/files |
| 📦 | `:package:` | Dependencies |
| 🏗️ | `:building_construction:` | Architecture |
| 💄 | `:lipstick:` | UI/cosmetic |

### Examples

```
✨ feat: add user authentication flow

Implements JWT-based auth with refresh tokens.
Adds login, logout, and session management.
```

```
🐛 fix: resolve race condition in data fetching

The useEffect cleanup wasn't cancelling pending requests,
causing state updates on unmounted components.
```

```
🔧 config: update ESLint rules for stricter typing
```

## 4. Commit and Push

```bash
git commit -m "<message>"
git push
```

If push fails due to remote changes:
```bash
git pull --rebase
git push
```

## 5. Report Result

After successful push, show:
- Commit hash (short)
- Branch name
- Files changed summary
- Remote URL for easy access

## Important

- Never use `--force` unless explicitly requested
- Never skip hooks (`--no-verify`) unless explicitly requested
- If there are merge conflicts, stop and explain the situation
- Keep commit messages concise but informative
