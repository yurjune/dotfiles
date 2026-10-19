# Repository Instructions

## Commit Message Convention

- Prefer commit subjects in the form `<scope>: <summary>` (e.g. `zshrc: add alias`).
- Do not add `Co-authored-by`, AI attribution, or similar trailers unless the user explicitly requests them.

## Chezmoi Workflow

- Before starting work, run `chezmoi status` and `chezmoi diff` to check for changes made directly on this system.
- If only the system copy changed, run `chezmoi re-add <target>` to bring that change into the source files.
- If `chezmoi apply` encounters a conflict or asks whether to overwrite a changed target, leave the source changes and system files as they are.
  Do not force, merge, or roll back the changes. Report the situation and wait for the user to review it before proceeding.
- If `chezmoi re-add` encounters a conflict, report it to the user. Do not take further action in chezmoi to resolve it.
- Make configuration changes in chezmoi source files; treat them as the source of truth.
- Do not modify README.md.
- After completing and committing the changes, run `chezmoi apply` to synchronize managed files to this system.

## Personal Skills

- When a skill is added to or removed from `~/github/my-skills/skills`, sync its symlinks in `dot_agents/skills` and `dot_claude/skills`.
