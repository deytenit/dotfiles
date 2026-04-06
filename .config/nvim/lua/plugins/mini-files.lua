return {
  {
    "nvim-mini/mini.files",
    cond = function()
      vim.fn.system("arc root 2>/dev/null")
      return vim.v.shell_error ~= 0
    end,
    options = {
      preview = true,
      width_preview = 30,
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
    dir = "~/Source/arcadia/a/junk/ermnvldmr/mini-arc-files",
    cond = function()
      vim.fn.system("arc root 2>/dev/null")
      return vim.v.shell_error == 0
    end,
    options = {
      preview = true,
      width_preview = 30,
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
