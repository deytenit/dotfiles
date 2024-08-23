return {
  {
    "hrsh7th/nvim-cmp",
    opts = function(_, opts)
      opts.window = {
        completion = {
          winhighlight = "Normal:Pmenu,FloatBorder:PmenuThumb,Search:None",
          col_offset = -3,
          side_padding = 0,
        },
        documentation = {
          border = "rounded",
          winhighlight = "Normal:Pmenu,FloatBorder:Pmenu,Search:None",
        },
      }
      opts.formatting = {
        fields = { "kind", "abbr", "menu" },
        format = function(_, item)
          local icons = require("lazyvim.config").icons.kinds
          item.menu = "    (" .. (item.kind or "unknown") .. ")"
          item.kind = " " .. (icons[item.kind] or " ")
          return item
        end,
      }
      return opts
    end,
  },
  {
    "L3MON4D3/LuaSnip",
    opts = {
      history = true,
      region_check_events = "CursorHold,InsertLeave",
      -- those are for removing deleted snippets, also a common problem
      delete_check_events = "TextChanged,InsertEnter",
    }
  }
}
