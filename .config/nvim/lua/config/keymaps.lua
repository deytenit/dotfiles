-- Keymaps are automatically loaded on the VeryLazy event
-- Default keymaps that are always set: https://github.com/LazyVim/LazyVim/blob/main/lua/lazyvim/config/keymaps.lua
-- Add any additional keymaps here

local keymap = vim.keymap
local opts = { noremap = true, silent = true }

-- base
keymap.set("n", "x", '"_x')

-- (inc/dec)rement
keymap.set("n", "+", "<C-a>")
keymap.set("n", "-", "<C-x>")

-- windows
keymap.set("n", "<Leader>-", "<cmd>split<CR><C-w>j", opts)
keymap.set("n", "<Leader>\\", "<cmd>vsplit<CR><C-w>l", opts)

keymap.set("n", "<C-M-h>", "<C-w><")
keymap.set("n", "<C-M-j>", "<C-w>+")
keymap.set("n", "<C-M-k>", "<C-w>-")
keymap.set("n", "<C-M-l>", "<C-w>>")

-- sixty.nvim
local sixty_status, sixty = pcall(require, "sixty")
if sixty_status then
  sixty.set("n", "<Up>")
  sixty.set("n", "<Down>")
end
