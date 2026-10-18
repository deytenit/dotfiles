if status is-interactive
end

function codex --wraps codex
    if set -q ZELLIJ_PANE_ID; and set -q ZELLIJ_SESSION_NAME; and not contains -- --no-daemon $argv
        command codex --no-daemon $argv
    else
        command codex $argv
    end
end
