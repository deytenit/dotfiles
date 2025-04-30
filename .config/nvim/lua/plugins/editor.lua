return {
  {
    "telescope.nvim",
    keys = {
      {
        "<leader>sg",
        LazyVim.pick("live_grep", { root = false }),
        desc = "Grep (cwd)"
      },
      {
        "<leader>sG",
        LazyVim.pick("live_grep", { cwd = vim.fn.expand("%:p:h") }),
        desc = "Grep (cwd)"
      },
      {
        "<leader>ff",
        LazyVim.pick("files", { root = false }),
        desc = "Find Files (cwd)"
      },
      {
        "<leader>fF",
        LazyVim.pick("files", { cwd = vim.fn.expand("%:p:h") }),
        desc = "Find Files (Directory of Current File)"
      },
      {
        "<leader><space>",
        LazyVim.pick("files", { root = false }),
        desc = "Find Files (cwd)"
      },
    },
  },
  {
    "deytenit/sixty.nvim",
    config = function()
      require("sixty").setup()
    end,
  },
  {
    "echasnovski/mini.files",
    options = {
      use_as_default_explorer = true,
    },
    keys = {
      {
        "<leader>fE",
        function()
          require("mini.files").open(vim.api.nvim_buf_get_name(0), true)
        end,
        desc = "Open mini.files (Directory of Current File)",
      },
      {
        "<leader>fe",
        function()
          require("mini.files").open(vim.uv.cwd(), true)
        end,
        desc = "Open mini.files (cwd)",
      },
    }
  },
  {
    "nvim-neo-tree/neo-tree.nvim",
    enabled = false,
  },
}
