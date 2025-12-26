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
