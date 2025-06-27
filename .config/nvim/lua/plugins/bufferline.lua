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
}
