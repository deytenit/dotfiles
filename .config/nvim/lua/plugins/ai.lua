return {
  {
    "olimorris/codecompanion.nvim",
    dependencies = {
      "nvim-lua/plenary.nvim",
      "nvim-treesitter/nvim-treesitter",
      {
        "saghen/blink.cmp",
        opts = {
          sources = {
            default = { "codecompanion" },
            providers = {
              codecompanion = {
                name = "CodeCompanion",
                module = "codecompanion.providers.completion.blink",
                enabled = true,
              },
            },
          },
        },
      },
    },
    opts = function ()
      vim.env["CODECOMPANION_TOKEN_PATH"] = vim.fn.expand("~/.config")

      vim.fn.systemlist("arc root 2>/dev/null")
      local use_yalm = vim.v.shell_error == 0

      local adapters = {
        yalm_deepseek_v3 = function()
          return require("codecompanion.adapters").extend("openai_compatible", {
            env = {
              url = "http://zeliboba.yandex-team.ru/balance/communal-deepseek-v3-0324-in-yt",
              api_key = "cmd:cat ~/.yalm_token",
              chat_url = "/v1/chat/completions",
            },
            schema = {
              model = {
                default = "deepseek",
              },
              temperature = {
                order = 2,
                mapping = "parameters",
                type = "number",
                optional = true,
                default = 0.8,
                desc = "What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. We generally recommend altering this or top_p but not both.",
                validate = function(n)
                  return n >= 0 and n <= 2, "Must be between 0 and 2"
                end,
              },
              max_completion_tokens = {
                order = 3,
                mapping = "parameters",
                type = "integer",
                optional = true,
                default = nil,
                desc = "An upper bound for the number of tokens that can be generated for a completion.",
                validate = function(n)
                  return n > 0, "Must be greater than 0"
                end,
              },
              stop = {
                order = 4,
                mapping = "parameters",
                type = "string",
                optional = true,
                default = nil,
                desc = "Sets the stop sequences to use. When this pattern is encountered the LLM will stop generating text and return. Multiple stop patterns may be set by specifying multiple separate stop parameters in a modelfile.",
                validate = function(s)
                  return s:len() > 0, "Cannot be an empty string"
                end,
              },
              logit_bias = {
                order = 5,
                mapping = "parameters",
                type = "map",
                optional = true,
                default = nil,
                desc = "Modify the likelihood of specified tokens appearing in the completion. Maps tokens (specified by their token ID) to an associated bias value from -100 to 100. Use https://platform.openai.com/tokenizer to find token IDs.",
                subtype_key = {
                  type = "integer",
                },
                subtype = {
                  type = "integer",
                  validate = function(n)
                    return n >= -100 and n <= 100, "Must be between -100 and 100"
                  end,
                },
              },
            },
          })
        end,
        yalm_deepseek_r1 = function()
          return require("codecompanion.adapters").extend("openai_compatible", {
            env = {
              url = "http://zeliboba.yandex-team.ru/balance/deepseek_r1",
              api_key = "cmd:cat ~/.yalm_token",
              chat_url = "/v1/chat/completions",
            },
            schema = {
              model = {
                default = "deepseek",
              },
              temperature = {
                order = 2,
                mapping = "parameters",
                type = "number",
                optional = true,
                default = 0.8,
                desc = "What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. We generally recommend altering this or top_p but not both.",
                validate = function(n)
                  return n >= 0 and n <= 2, "Must be between 0 and 2"
                end,
              },
              max_completion_tokens = {
                order = 3,
                mapping = "parameters",
                type = "integer",
                optional = true,
                default = nil,
                desc = "An upper bound for the number of tokens that can be generated for a completion.",
                validate = function(n)
                  return n > 0, "Must be greater than 0"
                end,
              },
              stop = {
                order = 4,
                mapping = "parameters",
                type = "string",
                optional = true,
                default = nil,
                desc = "Sets the stop sequences to use. When this pattern is encountered the LLM will stop generating text and return. Multiple stop patterns may be set by specifying multiple separate stop parameters in a modelfile.",
                validate = function(s)
                  return s:len() > 0, "Cannot be an empty string"
                end,
              },
              logit_bias = {
                order = 5,
                mapping = "parameters",
                type = "map",
                optional = true,
                default = nil,
                desc = "Modify the likelihood of specified tokens appearing in the completion. Maps tokens (specified by their token ID) to an associated bias value from -100 to 100. Use https://platform.openai.com/tokenizer to find token IDs.",
                subtype_key = {
                  type = "integer",
                },
                subtype = {
                  type = "integer",
                  validate = function(n)
                    return n >= -100 and n <= 100, "Must be between -100 and 100"
                  end,
                },
              },
            },
          })
        end,
        copilot_gemini_pro = function()
          return require("codecompanion.adapters").extend("copilot", {
            schema = {
              model = {
                default = "gemini-2.5-pro",
              },
            },
          })
        end,
        copilot_gemini_flash = function()
          return require("codecompanion.adapters").extend("copilot", {
            schema = {
              model = {
                default = "gemini-2.0-flash-001",
              },
            },
          })
        end,
      }

      local main_adapter
      local inline_adapter
      if use_yalm then
        vim.notify("CodeCompanion: Using 'yalm' based adapter (arc root)", vim.log.levels.INFO)
        main_adapter = "yalm_deepseek_r1"
        inline_adapter = "yalm_deepseek_v3"
      else
        vim.notify("CodeCompanion: Using 'copilot' adapter", vim.log.levels.INFO)
        main_adapter = "copilot_gemini_pro"
        inline_adapter = "copilot_gemini_flash"
        adapters.opts = {
          allow_insecure = true,
          -- xray proxy
          proxy = "socks5://127.0.0.1:2080",
        }
      end

      local strategies = {
        chat = { adapter = main_adapter, },
        inline = { adapter = inline_adapter },
        agent = { adapter = main_adapter },
      }

      local display =  {
        action_palette = {
          provider = "default",
        },
        chat = {
          show_references = true,
          show_header_separator = true,
          show_settings = true,
        },
        diff = {
          provider = "mini_diff",
        },
      }

      return {
        adapters = adapters,
        strategies = strategies,
        display = display,
      }
    end,
    keys = {
      {
        "<Leader>aa",
        "<cmd>CodeCompanionActions<CR>",
        desc = "Open the action palette",
        mode = { "n", "v" },
      },
      {
        "<Leader>ac",
        "<cmd>CodeCompanionChat Toggle<CR>",
        desc = "Toggle a chat buffer",
        mode = { "n" },
      },
      {
        "<Leader>ac",
        "<cmd>CodeCompanionChat Add<CR>",
        desc = "Add code to a chat buffer",
        mode = { "v" },
      },
    },
  },
}
