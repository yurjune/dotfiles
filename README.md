# dotfiles

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
