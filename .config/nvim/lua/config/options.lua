-- Options are automatically loaded before lazy.nvim startup
-- Default options that are always set: https://github.com/LazyVim/LazyVim/blob/main/lua/lazyvim/config/options.lua
-- Add any additional options here

vim.opt.backup = false
vim.opt.wrap = false
vim.opt.mouse = ""

vim.g.autoformat = false

if vim.fn.executable("arc") == 1 then
  local obj = vim.system({ "arc", "root" }, { text = true }):wait()
  if obj.code == 0 then
    vim.o.fsync = false
  end
end

vim.o.clipboard = "unnamedplus"

local function is_ssh()
  return os.getenv("SSH_TTY") ~= nil or os.getenv("SSH_CLIENT") ~= nil
end

local function in_zellij()
  return os.getenv("ZELLIJ") ~= nil
end

local function is_wsl()
  return os.getenv("WSL_DISTRO_NAME") ~= nil
end

if is_ssh() then
  local paste_fn = function() return {} end
  local osc52_paste = not in_zellij() and require("vim.ui.clipboard.osc52").paste("+") or paste_fn
  vim.g.clipboard = {
    name = "OSC 52",
    copy = {
      ["+"] = require("vim.ui.clipboard.osc52").copy("+"),
      ["*"] = require("vim.ui.clipboard.osc52").copy("*"),
    },
    paste = {
      ["+"] = osc52_paste,
      ["*"] = osc52_paste,
    },
  }
elseif is_wsl() then
  vim.g.clipboard = {
    name = "wsl",
    copy = {
      ["+"] = "clip.exe",
      ["*"] = "clip.exe",
    },
    paste = {
      ["+"] = { "powershell.exe", "-noprofile", "-command", "Get-Clipboard" },
      ["*"] = { "powershell.exe", "-noprofile", "-command", "Get-Clipboard" },
    },
  }
end

