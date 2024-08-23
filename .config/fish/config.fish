set fish_greeting ""

set -gx LC_ALL en_US.UTF-8
set -gx FZF_DEFAULT_COMMAND 'fd --type f --hidden --follow --exclude .git --exclude .arc'

export GPG_TTY=$(tty)

if type -q nvim
    alias vim nvim
    set -gx EDITOR nvim
end

if status is-interactive
    # Commands to run in interactive sessions can go here
    if type -q eza
        alias l "eza -l -g -a --icons --group-directories-first"
    else
        alias l "ls -la"
    end
end
