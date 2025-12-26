if status is-interactive
  if type -q arc
    function ainit
      # Call amount
      amount

      # Change to the first directory and call nvm use
      cd ~/Source/arcadia/a/adv/frontend/packages/direct-modules
      nvm use

      # Open zellij with the yandex layout
      zellij --layout yandex
    end
  end
end
