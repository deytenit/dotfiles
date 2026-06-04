# Commands to run in interactive sessions can go here
if status is-interactive
  if type -q eza
    alias l "eza -l -g -a --icons --group-directories-first"
  else
    alias l "ls -la"
  end

  if type -q nvim
    alias vim nvim
  end

  if type -q bat
    alias cat bat
  end
end

function __opencode_inline_config --description "Запуск opencode с инлайн-конфигом"
  set -l config_path "$HOME/.config/opencode/opencode.jsonc"

  if not test -f $config_path
    command opencode $argv
    return $status
  end

  set -l inline_config (string collect < $config_path)
  set -lx OPENCODE_CONFIG_CONTENT $inline_config
  command opencode $argv
end


alias opencode __opencode_inline_config
