return {
  {
    "neovim/nvim-lspconfig",
    opts = function(_, opts)
      table.insert(opts.servers.clangd.cmd, 3, "--background-index-priority=low")
    end,
  },
}
