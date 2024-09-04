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
          col_offset = 3,
          winhighlight = "Normal:Normal,FloatBorder:NoiceCmdlinePopupBorder,Search:None",
        },
      }
      opts.formatting = {
        fields = { "kind", "abbr", "menu" },
        format = function(entry, item)
          item.menu = "    (" .. (item.kind or "unknown") .. ")"

          if item.kind == "Color" and entry.completion_item.documentation then
            local _, _, r, g, b = string.find(entry.completion_item.documentation, "^rgb%((%d+), (%d+), (%d+)")
            if r and g and b then
              local color = string.format("%02x", r) .. string.format("%02x", g) .. string.format("%02x", b)
              local group = "Tw_" .. color
              if vim.fn.hlID(group) < 1 then
                vim.api.nvim_set_hl(0, group, { bg = "#" .. color })
              end
              item.kind_hl_group = group
            end
          end

          local icons = require("lazyvim.config").icons.kinds
          item.kind = " " .. (icons[item.kind] or " ")

          return item
        end,
      }
      return opts
    end,
  },
  {
    "L3MON4D3/LuaSnip",
    -- stylua: ignore
    init = function ()
      local luasnip = require('luasnip')

      local unlinkgrp = vim.api.nvim_create_augroup(
        'UnlinkSnippetOnModeChange',
        { clear = true }
      )

      vim.api.nvim_create_autocmd('ModeChanged', {
        group = unlinkgrp,
        pattern = {'s:n', 'i:*'},
        desc = 'Forget the current snippet when leaving the insert mode',
        callback = function(evt)
          if
            luasnip.session
            and luasnip.session.current_nodes[evt.buf]
            and not luasnip.session.jump_active
          then
            luasnip.unlink_current()
          end
        end,
      })
    end
,
  },
}
