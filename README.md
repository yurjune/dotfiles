# dotfiles

Below, "source" means this repository and "target" means the file chezmoi writes under the home directory.

### source file naming

A prefix on a source filename sets an attribute on the target. chezmoi strips the prefix when it renders the target name.

- `dot_` becomes a leading `.`, so `dot_zshrc` is applied as `~/.zshrc`.
- `private_` removes all group and world permissions from the target file or directory.
- `executable_` sets the executable bit. `chezmoi add` applies this prefix on its own when the file already has the bit, so it
  only has to be written by hand when a source file is created or renamed directly.
- `symlink_` creates a symlink whose target is the rendered file contents. A relative target can be written as plain text,
  while an absolute one needs the `.tmpl` suffix so that the target can be rendered from `{{ .chezmoi.homeDir }}`.

### repository-only files

Any file placed in the source directory becomes a target in the home directory. A file that belongs to the repository alone,
such as this README, has to be listed in `.chezmoiignore` to keep `chezmoi apply` from creating it in `~`.

### add a file to chezmoi

```bash
chezmoi add ~/.dotfile
```

### edit a source file and apply it to the target

```bash
chezmoi edit ~/.dotfile
chezmoi apply
```

### pull target changes into the source

```bash
# specific file
chezmoi re-add ~/.dotfile

# all files
chezmoi re-add
```
