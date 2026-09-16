return {
  {
    "https://github.com/DrKJeff16/project.nvim",
    main = "project",
    lazy = false,
    dependencies = {
      "ibhagwan/fzf-lua",
      "folke/snacks.nvim",
    },
    opts = {
      manual_mode = true,
      fzf_lua = { enabled = true },
      snacks = { enabled = true },
    },
    keys = {
      { "<leader>fp", "<cmd>Project fzf-lua<cr>", desc = "Projects" },
    },
  },
  {
    "nvim-lualine/lualine.nvim",
    opts = function(_, opts)
      table.insert(opts.sections.lualine_b, { "project" })
    end,
  },
}
