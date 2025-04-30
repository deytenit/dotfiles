return {
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
