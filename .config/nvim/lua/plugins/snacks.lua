return {
  {
    "folke/snacks.nvim",
    event = "VimEnter",
    opts = function(_, opts)
      local header = [[
 __ __  ____  __ __  ____   ____  __    __  __    __ 
|  |  ||    ||  |  ||    | /    ||  |__|  ||  |__|  |
|  ~  | |  | |  ~  | |  | |  o  ||  |  |  ||  |  |  |
|___, | |  | |___, | |  | |  _  |\  `  '  /\  `  '  /
|____/ |____||____/ |____||__|__|  \_/\_/    \_/\_/  
      ]]

      opts.dashboard.preset.header = header
      opts.dashboard.sections = {
        { section = "header" },
        { section = "keys", gap = 1, padding = 1 },
        { pane = 2, icon = " ", title = "Recent Files", section = "recent_files", indent = 2, padding = 1 },
        { pane = 2, icon = " ", title = "Projects", section = "projects", indent = 2, padding = 1 },
        {
          pane = 2,
          icon = " ",
          title = "Git Status",
          section = "terminal",
          enabled = function()
            return Snacks.git.get_root() ~= nil
          end,
          cmd = "hub status --short --branch --renames",
          height = 5,
          padding = 1,
          ttl = 5 * 60,
          indent = 3,
        },
        { section = "startup" }
      }
    end,
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
}

