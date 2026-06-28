-- ~/.config/nvim/lua/plugins/auto-dark-mode.lua
-- Replacing OS-polling auto-dark-mode with terminal-driven OSC 11 checks

local TerminalThemeSync = {}

function TerminalThemeSync.query_terminal()
  -- Write raw OSC 11 query to stdout to bypass Neovim buffer
  io.stdout:write("\27]11;?\27\\")
  io.stdout:flush()
end

function TerminalThemeSync.setup()
  -- 1. Create autocommand to parse TermResponse
  vim.api.nvim_create_autocmd("TermResponse", {
    pattern = "*",
    callback = function(args)
      local sequence = args.data.sequence
      -- Parse OSC 11 response (e.g. \027]11;rgb:xxxx/xxxx/xxxx\027\\)
      local r, g, b = sequence:match("\27%]11;rgb:(%x+)/(%x+)/(%x+)")
      if r and g and b then
        local rr = tonumber(r, 16) / 65535
        local gg = tonumber(g, 16) / 65535
        local bb = tonumber(b, 16) / 65535

        -- Compute luminance
        local luminance = (0.299 * rr) + (0.587 * gg) + (0.114 * bb)
        local bg_mode = luminance < 0.5 and "dark" or "light"

        if vim.o.background ~= bg_mode then
          vim.o.background = bg_mode
          vim.cmd("redraw!")
        end
      end
    end,
  })

  -- 2. Query theme at startup and when window gains focus
  vim.api.nvim_create_autocmd({ "VimEnter", "FocusGained" }, {
    callback = TerminalThemeSync.query_terminal,
  })

  -- 3. Set up a periodic background timer (every 3 seconds) for runtime shifts
  local timer = vim.uv.new_timer()
  timer:start(1000, 3000, vim.schedule_wrap(TerminalThemeSync.query_terminal))

  -- Clean up timer on exit
  vim.api.nvim_create_autocmd("VimLeavePre", {
    callback = function()
      if timer and not timer:is_closing() then
        timer:close()
      end
    end,
  })
end

-- Initialize the sync module
vim.schedule(TerminalThemeSync.setup)

-- Return empty table to signal lazy.nvim to disable the old f-person plugin
return {}
