# Repository Instructions

## Commit Message Convention

- Prefer commit subjects in the form `<scope>: <summary>` (e.g. `zshrc: add alias`).
- Do not add `Co-authored-by`, AI attribution, or similar trailers unless the user explicitly requests them.

## Chezmoi Workflow

- Before starting work, run `chezmoi status` and `chezmoi diff` to check for changes made directly on this system.
- If only the system copy changed, run `chezmoi re-add <target>` to bring that change into the source files.
- If a conflict occurs, cancel the current action and undo any partial changes from that action to restore the pre-action state.
    - Do not merge or continue through the conflict.
    - Report the conflict and the rollback result to the user.
- Make configuration changes in chezmoi source files; treat them as the source of truth.
- After completing and committing the changes, run `chezmoi apply` to synchronize managed files to this system.
