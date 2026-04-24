if status is-interactive
  # Commands to run in interactive sessions can go here
  if type -q eza
    alias l "eza -l -g -a --icons --group-directories-first"
  else
    alias l "ls -la"
  end

  if type -q arc
    alias amount "arc mount -m ~/Source/arcadia/a -S ~/Source/arcadia/.store_a && arc mount -m ~/Source/arcadia/b -S ~/Source/arcadia/.store_b"
    alias arebase "arc fetch trunk && arc pull trunk && arc rebase trunk"
    alias aupdate "arc commit --amend --no-edit"
    alias apush "arc push -f"
  end
end

if type -q nvim
  alias vim nvim
end

if type -q bat
  alias cat bat
end

function __opencode_inline_config --description "Запуск opencode с инлайн-конфигом"
  set -l config_path "$HOME/.config/opencode/opencode.jsonc"

  if not test -f $config_path
    command opencode $argv
    return $status
  end

  set -l inline_config (string collect < $config_path)
  env OPENCODE_CONFIG_CONTENT="$inline_config" command opencode $argv
end

alias opencode __opencode_inline_config
