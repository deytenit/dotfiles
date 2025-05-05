if status is-interactive
  # Commands to run in interactive sessions can go here
  if type -q eza
    alias l "eza -l -g -a --icons --group-directories-first"
  else
    alias l "ls -la"
  end
end

if type -q nvim
  alias vim nvim
end
