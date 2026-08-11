local arc = require("util.arc")
local ARC_ROOT = arc.root()

local opts = {
  windows = { preview = true, width_preview = 30 },
  options = { use_as_default_explorer = true },
}

local keys = {
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

local dependencies = {
  {
    "nvim-mini/mini.icons",
    opts = {},
  },
}

return {
  {
    "nvim-mini/mini.files",
    cond = function()
      return not arc.is_repo()
    end,
    dependencies = dependencies,
    opts = opts,
    keys = keys,
  },
  {
    dir = vim.fs.joinpath(ARC_ROOT, "junk/ermnvldmr/mini-arc-files"),
    main = "mini.files",
    cond = function()
      return arc.is_repo()
    end,
    dependencies = dependencies,
    opts = opts,
    keys = keys,
  },
  {
    "nvim-neo-tree/neo-tree.nvim",
    enabled = false,
  },
}

