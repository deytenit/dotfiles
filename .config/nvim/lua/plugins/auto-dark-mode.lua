return {
  {
    "f-person/auto-dark-mode.nvim",
    commit = "c31de126963ffe9403901b4b0990dde0e6999cc6",
    opts = {
      update_interval = 1000,
      set_dark_mode = function()
        vim.api.nvim_set_option_value("background", "dark", {})
      end,
      set_light_mode = function()
        vim.api.nvim_set_option_value("background", "light", {})
      end,
      fallback = "dark",
    },
  },
}
