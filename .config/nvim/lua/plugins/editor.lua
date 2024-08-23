return {
  {
    "telescope.nvim",
    dependencies = {
      "nvim-telescope/telescope-file-browser.nvim",
    },
    keys = {
      {
        "<leader>fE",
        function()
          local telescope = require("telescope")

          telescope.extensions.file_browser.file_browser({
            path = "%:p:h",
            cwd = vim.fn.expand("%:p:h"),
            respect_gitignore = false,
            hidden = true,
            grouped = true,
          })
        end,
        desc = "Explorer (cwd)",
      },
      {
        "<leader>fe",
        function()
          local telescope = require("telescope")
          telescope.extensions.file_browser.file_browser({
            respect_gitignore = false,
            hidden = true,
            grouped = true,
          })
        end,
        desc = "Explorer (Root Dir)",
      },
      {
        "<leader>sg",
        LazyVim.pick("live_grep", { root = false }),
        desc = "Grep (Root Dir)"
      },
      {
        "<leader>sG",
        LazyVim.pick("live_grep", { cwd = vim.fn.expand("%:p:h") }),
        desc = "Grep (cwd)"
      },
      {
        "<leader>ff",
        LazyVim.pick("files", { root = false }),
        desc = "Find Files (Root Dir)"
      },
      {
        "<leader>fF",
        LazyVim.pick("files", { cwd = vim.fn.expand("%:p:h") }),
        desc = "Find Files (cwd)"
      },
      {
        "<leader><space>",
        LazyVim.pick("files", { root = false }),
        desc = "Find Files (Root Dir)"
      },
    },
  },
  {
    "nvim-neo-tree/neo-tree.nvim",
    enabled = false,
  },
}
