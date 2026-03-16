return {
  {
    "yetone/avante.nvim",
    event = "VeryLazy",
    -- Never pin to "*" — avante releases frequently and the API changes fast.
    version = false,
    build = "make",
    dependencies = {
      "nvim-lua/plenary.nvim",
      "MunifTanjim/nui.nvim",
      "nvim-treesitter/nvim-treesitter",
      "nvim-tree/nvim-web-devicons",
      -- Required for provider = "copilot" variants.
      -- LazyVim's extras.coding.copilot already sets this up; mark optional here.
      { "zbirenbaum/copilot.lua", optional = true },
      {
        "ravitemer/mcphub.nvim",
        cmd = "MCPHub",
        build = "pnpm install -g mcp-hub@latest",
        config = true,
        opts = {
          make_vars = true,
          -- Expose MCP server prompts as /mcp:server:prompt slash commands in chat
          extensions = {
            avante = {
              make_slash_commands = true,
            },
          },
        },
      },
      -- NOTE: Davidyz/VectorCode has no avante extension — it is CodeCompanion-only.
      -- Dropped from dependencies. Keep as a standalone plugin if you still use it
      -- for other purposes (e.g. CLI indexing), just without the avante tool opt.
    },

    opts = function()
      -- ⚠ BUG FIX from original config:
      -- filereadable() returns 1 when readable, 0 when not.
      -- The original `== 0` condition meant "use yalm when the token DOESN'T exist",
      -- which is the inverse of the intent. Changed to `~= 0`.
      local use_yalm = vim.fn.filereadable(vim.fn.expand("~/.yalm_token")) ~= 0

      -- ── Providers ──────────────────────────────────────────────────────────
      -- Avante uses __inherited_from to extend built-in providers, exactly like
      -- CodeCompanion's adapter.extend(). All extra LLM params go in
      -- extra_request_body (not at the top level — that's the new migration rule).

      local providers = {
        -- Yandex YALM → DeepSeek V3 (OpenAI-compatible endpoint)
        -- Original: adapters.http.yalm_deepseek_v3 extending "openai_compatible"
        -- avante's openai provider appends "/chat/completions" to `endpoint`,
        -- so endpoint = base_url + "/v1".
        yalm_deepseek_v3 = {
          __inherited_from = "openai",
          endpoint = "http://zeliboba.yandex-team.ru/balance/communal-deepseek-v3-0324-in-yt/v1",
          api_key_name = "cmd:cat ~/.yalm_token",
          model = "deepseek",
          extra_request_body = {
            max_tokens = 8192,
          },
        },

        -- Yandex Eliza → Anthropic proxy
        -- Original: adapters.http.yalm_anthropic extending "anthropic"
        -- avante's claude provider appends "/v1/messages" to `endpoint`,
        -- so strip that suffix from the original URL.
        yalm_anthropic = {
          __inherited_from = "claude",
          endpoint = "https://api.eliza.yandex.net/raw/anthropic",
          api_key_name = "cmd:cat ~/.eliza_token",
          extra_request_body = {
            max_tokens = 8192,
          },
        },

        -- Copilot → Claude Sonnet 4
        -- Original: adapters.http.copilot_claude_sonnet extending "copilot"
        copilot_claude_sonnet = {
          __inherited_from = "copilot",
          model = "claude-sonnet-4",
          extra_request_body = {
            max_tokens = 8192,
          },
        },

        -- Copilot → Gemini 2.0 Flash
        -- Original: adapters.http.copilot_gemini_flash extending "copilot"
        copilot_gemini_flash = {
          __inherited_from = "copilot",
          model = "gemini-2.0-flash-001",
          extra_request_body = {
            max_tokens = 8192,
          },
        },
      }

      -- ── Provider selection (mirrors original adapter branching) ─────────────
      local main_provider
      local suggestions_provider

      if use_yalm then
        vim.notify("Avante: Using 'yalm' based provider (arc root)", vim.log.levels.INFO)
        main_provider = "yalm_anthropic"
        suggestions_provider = "yalm_deepseek_v3"
      else
        vim.notify("Avante: Using 'copilot' provider", vim.log.levels.INFO)
        main_provider = "copilot_claude_sonnet"
        suggestions_provider = "copilot_gemini_flash"
        -- Proxy (replaces adapters.opts.proxy / allow_insecure):
        -- avante has no top-level http proxy config. Set these env vars instead,
        -- either in your shell profile or in Neovim's init before this loads:
        --   export ALL_PROXY=socks5://127.0.0.1:10808
        --   export HTTPS_PROXY=socks5://127.0.0.1:10808
        -- For allow_insecure (skip TLS verify), set: CURL_CA_BUNDLE=""
        vim.env.ALL_PROXY = vim.env.ALL_PROXY or "socks5://127.0.0.1:10808"
        vim.env.HTTPS_PROXY = vim.env.HTTPS_PROXY or "socks5://127.0.0.1:10808"
      end

      -- ── System prompt (replaces rules + extensions.mcphub make_vars) ────────
      -- This function is evaluated on every message, so MCP server state is
      -- always current — even in existing chat sessions.
      local function build_system_prompt()
        local parts = {}

        -- Replaces codecompanion `rules.files = { "AGENTS.md" }`:
        -- avante natively reads `avante.md` from project root; for AGENTS.md
        -- we read it ourselves here.
        local agents_path = vim.fn.getcwd() .. "/AGENTS.md"
        if vim.fn.filereadable(agents_path) == 1 then
          local lines = vim.fn.readfile(agents_path)
          table.insert(parts, table.concat(lines, "\n"))
        end

        -- MCP Hub active-servers prompt (replaces extensions.mcphub make_vars)
        local hub = require("mcphub").get_hub_instance()
        if hub then
          local mcp = hub:get_active_servers_prompt()
          if mcp and mcp ~= "" then
            table.insert(parts, mcp)
          end
        end

        return table.concat(parts, "\n\n")
      end

      -- ── Return full opts ────────────────────────────────────────────────────
      return {
        -- Main chat provider (strategies.chat.adapter equivalent)
        provider = main_provider,

        -- Inline/suggestions provider (strategies.inline.adapter equivalent)
        -- ⚠ avante warns that using copilot here can cause request-rate issues:
        -- https://github.com/yetone/avante.nvim/issues/1048
        -- Set to nil to disable auto-suggestions if that becomes a problem.
        auto_suggestions_provider = suggestions_provider,

        providers = providers,

        -- Dynamic system prompt (MCP + AGENTS.md)
        system_prompt = build_system_prompt,

        -- MCP tools (replaces extensions.mcphub callback/show_result_in_chat)
        custom_tools = function()
          return { require("mcphub.extensions.avante").mcp_tool() }
        end,

        behaviour = {
          -- Replaces tools.opts.auto_submit_success = true
          auto_approve_tool_permissions = true,
          -- tools.opts.auto_submit_errors = false has no direct equivalent;
          -- avante surfaces tool errors as chat messages automatically.
          auto_set_keymaps = false, -- we set our own below
        },

        -- Rules directory for .avanterules jinja template files.
        -- Replaces the concept of codecompanion prompt_library / workflows:
        rules = {
          global_dir = "~/.config/nvim/lua/etc/avante/rules",
        },

        -- Replaces display.action_palette.provider = "default".
        -- LazyVim ships with snacks.nvim; change to "telescope" or "fzf_lua" if preferred.
        file_selector = {
          provider = "snacks",
        },

        -- Mappings (replaces keys section keymaps)
        mappings = {
          ask = "<Leader>aa",
          edit = "<Leader>ae",
          refresh = "<Leader>ar",
          toggle = {
            default = "<Leader>at",
          },
        },
      }
    end,

    keys = {
      -- Replaces <Leader>aa → CodeCompanionActions (open action palette)
      {
        "<Leader>aa",
        "<cmd>AvanteAsk<CR>",
        desc = "Avante Ask",
        mode = { "n", "v" },
      },
      -- Replaces <Leader>ac (n) → CodeCompanionChat Toggle
      {
        "<Leader>ac",
        "<cmd>AvanteChat<CR>",
        desc = "Avante Chat",
        mode = { "n" },
      },
      -- Replaces <Leader>ac (v) → CodeCompanionChat Add
      -- AvanteAsk in visual mode automatically uses the selection as context.
      {
        "<Leader>ac",
        "<cmd>AvanteAsk<CR>",
        desc = "Avante Ask (selection)",
        mode = { "v" },
      },
    },
  },
}

