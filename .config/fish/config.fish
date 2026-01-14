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
if not string match -q -- $PNPM_HOME $PATH
  set -gx PATH "$PNPM_HOME" $PATH
end
# pnpm end
