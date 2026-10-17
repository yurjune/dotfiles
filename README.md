# dotfiles

## Shared LLM skills

The personal Codex and Claude Code skills in `~/.agents/skills` and
`~/.claude/skills` link to `~/github/my-skills/skills`. Clone `my-skills`
to that location before running `chezmoi apply`.

### add a chezmoi file

```bash
chezmoi add ~/.dotfile
```
 
### edit chezmoi file and apply to source

```bash
chezmoi edit ~/.dotfile
chezmoi apply
```

### pull source changes to chezmoi file

```bash
# specific file
chezmoi re-add ~/.dotfile

# all files
chezmoi re-add
```
