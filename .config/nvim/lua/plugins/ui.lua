return {
  {
    "akinsho/bufferline.nvim",
    keys = {
      { "<tab>", "<cmd>BufferLineCycleNext<cr>", desc = "Next Buffer" },
      { "<s-tab>", "<cmd>BufferLineCyclePrev<cr>", desc = "Prev Buffer" },
    },
    opts = {
      options = {
        show_buffer_close_icons = false,
        show_close_icon = false,
      },
    },
  },
  {
    "nvimdev/dashboard-nvim",
    event = "VimEnter",
    opts = function(_, opts)
      local logo = [[
__ __  ____  __ __  ____  __ __  ____   ____  __    __  __    __ 
|  |  ||    ||  |  ||    ||  |  ||    | /    ||  |__|  ||  |__|  |
|  |  | |  | |  |  | |  | |  |  | |  | |  o  ||  |  |  ||  |  |  |
|  ~  | |  | |  ~  | |  | |  ~  | |  | |     ||  |  |  ||  |  |  |
|___, | |  | |___, | |  | |___, | |  | |  _  ||  `  '  ||  `  '  |
|     | |  | |     | |  | |     | |  | |  |  | \      /  \      / 
|____/ |____||____/ |____||____/ |____||__|__|  \_/\_/    \_/\_/  
      ]]

      logo = string.rep("\n", 8) .. logo .. "\n\n"
      opts.config.header = vim.split(logo, "\n")
    end,
  },
  {
    "catppuccin/nvim",
    lazy = true,
    name = "catppuccin",
    opts = {
      flavour = "latte",
      transparent_background = true,
      integrations = {
        aerial = true,
        alpha = true,
        cmp = true,
        dashboard = true,
        flash = true,
        gitsigns = true,
        headlines = true,
        illuminate = true,
        indent_blankline = { enabled = true },
        leap = true,
        lsp_trouble = true,
        mason = true,
        markdown = true,
        mini = true,
        native_lsp = {
          enabled = true,
          underlines = {
            errors = { "undercurl" },
            hints = { "undercurl" },
            warnings = { "undercurl" },
            information = { "undercurl" },
          },
        },
        navic = { enabled = true, custom_bg = "lualine" },
        neotest = true,
        neotree = true,
        noice = true,
        notify = true,
        semantic_tokens = true,
        telescope = true,
        treesitter = true,
        treesitter_context = true,
        which_key = true,
      },
    },
  },
  {
    "LazyVim/LazyVim",
    opts = {
      colorscheme = "catppuccin",
    },
  },
}
