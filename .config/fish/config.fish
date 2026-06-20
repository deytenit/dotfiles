set fish_greeting ""

set -gx FZF_DEFAULT_COMMAND 'fd --type f --hidden --follow --exclude .git --exclude .arc'
set -gx GPG_TTY $(tty)
if type -q nvim
  set -gx EDITOR nvim
end

source $HOME/.config/fish/aliases.fish
source $HOME/.config/fish/functions.fish

# pnpm
set -gx PNPM_HOME "$HOME/.local/share/pnpm"
if test -d $PNPM_HOME
  set -gx PATH "$PNPM_HOME" $PATH
end
# pnpm end

# fnm
set -gx FNM_HOME "$HOME/.local/share/fnm"
if test -d $FNM_HOME
  set -gx PATH "$FNM_HOME" $PATH
  fnm env --shell fish | source
end
# fnm end

# local
if not contains $HOME/.local/bin $PATH
    set -gx PATH $HOME/.local/bin $PATH
end
# local end

if test -f $HOME/.config/fish/.config.local.fish
  source $HOME/.config/fish/.config.local.fish
end
