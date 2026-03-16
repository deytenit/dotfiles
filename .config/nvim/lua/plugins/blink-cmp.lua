return {
  {
    "saghen/blink.cmp",
    dependencies = {
      "saghen/blink.compat",  -- required for blink.compat.source module
    },
    opts = {
      sources = {
        default = {
          "lsp", "path", "snippets", "buffer",
          -- avante sources (replaces codecompanion source)
          "avante_commands",
          "avante_mentions",
          "avante_shortcuts",
          "avante_files",
        },
        providers = {
          -- remove any existing codecompanion entry, add these:
          avante_commands = {
            name = "avante_commands",
            module = "blink.compat.source",
            score_offset = 90,
            opts = {},
          },
          avante_files = {
            name = "avante_files",
            module = "blink.compat.source",
            score_offset = 100,
            opts = {},
          },
          avante_mentions = {
            name = "avante_mentions",
            module = "blink.compat.source",
            score_offset = 1000,
            opts = {},
          },
          avante_shortcuts = {
            name = "avante_shortcuts",
            module = "blink.compat.source",
            score_offset = 1000,
            opts = {},
          },
        },
      },
    },
  },
}
