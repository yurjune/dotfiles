# Repository Instructions

## General

Do not modify README.md.

## Commit Message Convention

- Prefer commit subjects in the form `<scope>: <summary>` (e.g. `zshrc: add alias`).
- Do not add `Co-authored-by`, AI attribution, or similar trailers unless the user explicitly requests them.

## Chezmoi Workflow

1. Before starting work, run `chezmoi status` and `chezmoi diff` to check for changes made directly on this system.
2. If only the system copy of a relevant target changed, run `chezmoi re-add <target>` to bring that change into the source files.
3. Make configuration changes in chezmoi source files; treat them as the source of truth.
4. After changing managed source files, run `chezmoi apply` to synchronize them to this system.
5. Report the changes and apply result. The user tests the applied configuration; commit when the user accepts it.

If `chezmoi re-add` encounters a conflict, report it to the user and do not take further action in chezmoi to resolve it.
If `chezmoi apply` encounters a conflict or asks whether to overwrite a changed target, leave the source changes and system files as they are.
Do not force, merge, or roll back the changes. Report the situation and wait for the user to review it before proceeding.

## Skill Management

- When a skill is added to or removed from `~/github/my-skills/skills`, sync its symlinks in `dot_agents/skills` and `dot_claude/skills`.
- Third-party skills are installed per machine with `npx skills` and are not tracked in this repository.
  Use the `syncing-skills` skill to add or remove them.
