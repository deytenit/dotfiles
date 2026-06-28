return {
  {
    "folke/tokyonight.nvim",
    lazy = true,
    name = "tokyonight",
    opts = {
      style = "moon",
      light_style = "day",
      transparent = true,
      dim_inactive = true,
      styles = {
        sidebars = "transparent",
        floats = "transparent",
        comments = { italic = true },
      },
      on_highlights = function(hl, c)
        hl.CursorLineNr = { fg = c.blue, bold = true }
      end,
    },
  },
}
