local shared_adapter_shema = {
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
}

local prompt_library = {
  ["Test workflow"] = {
    strategy = "workflow",
    description = "Use a workflow to test the plugin",
    opts = {
      index = 4,
    },
    prompts = {
      {
        {
          role = "user",
          content = "Generate a Python class for managing a book library with methods for adding, removing, and searching books",
          opts = {
            auto_submit = false,
          },
        },
      },
      {
        {
          role = "user",
          content = "Write unit tests for the library class you just created",
          opts = {
            auto_submit = true,
          },
        },
      },
      {
        {
          role = "user",
          content = "Create a TypeScript interface for a complex e-commerce shopping cart system",
          opts = {
            auto_submit = true,
          },
        },
      },
      {
        {
          role = "user",
          content = "Write a recursive algorithm to balance a binary search tree in Java",
          opts = {
            auto_submit = true,
          },
        },
      },
      {
        {
          role = "user",
          content = "Generate a comprehensive regex pattern to validate email addresses with explanations",
          opts = {
            auto_submit = true,
          },
        },
      },
      {
        {
          role = "user",
          content = "Create a Rust struct and implementation for a thread-safe message queue",
          opts = {
            auto_submit = true,
          },
        },
      },
      {
        {
          role = "user",
          content = "Write a GitHub Actions workflow file for CI/CD with multiple stages",
          opts = {
            auto_submit = true,
          },
        },
      },
      {
        {
          role = "user",
          content = "Create SQL queries for a complex database schema with joins across 4 tables",
          opts = {
            auto_submit = true,
          },
        },
      },
      {
        {
          role = "user",
          content = "Write a Lua configuration for Neovim with custom keybindings and plugins",
          opts = {
            auto_submit = true,
          },
        },
      },
      {
        {
          role = "user",
          content = "Generate documentation in JSDoc format for a complex JavaScript API client",
          opts = {
            auto_submit = true,
          },
        },
      },
    },
  },
}

return {
  {
    "olimorris/codecompanion.nvim",
    dependencies = {
      {
        "j-hui/fidget.nvim",
        opts = {
          notification = {
            window = {
              winblend = 0,
            },
          },
        },
      },
      "nvim-treesitter/nvim-treesitter",
      {
        "ravitemer/mcphub.nvim",
        cmd = "MCPHub",
        build = "npm install -g mcp-hub@latest",
        config = true,
      },
      {
        "Davidyz/VectorCode",
        version = "*",
        build = "pipx upgrade vectorcode",
        dependencies = { "nvim-lua/plenary.nvim" },
      },
    },
    opts = function()
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
            schema = vim.tbl_extend("force", {
              model = {
                default = "deepseek",
              },
            }, shared_adapter_shema),
          })
        end,
        yalm_deepseek_r1 = function()
          return require("codecompanion.adapters").extend("openai_compatible", {
            env = {
              url = "http://zeliboba.yandex-team.ru/balance/deepseek_r1",
              api_key = "cmd:cat ~/.yalm_token",
              chat_url = "/v1/chat/completions",
            },
            schema = vim.tbl_extend("force", {
              model = {
                default = "deepseek",
              },
            }, shared_adapter_shema),
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

      local display = {
        action_palette = {
          provider = "default",
        },
        chat = {
          -- show_references = true,
          -- show_header_separator = true,
          -- show_settings = true,
        },
        diff = {
          provider = "mini_diff",
        },
      }

      local extensions = {
        mcphub = {
          callback = "mcphub.extensions.codecompanion",
          opts = {
            make_vars = true,
            make_slash_commands = true,
            show_result_in_chat = true,
          },
        },
        vectorcode = {
          opts = {
            add_tool = true,
          },
        },
      }

      local strategies = {
        chat = {
          adapter = main_adapter,
          roles = {
            user = "deytenit",
          },
          keymaps = {
            send = {
              modes = {
                i = { "<C-CR>", "<C-s>" },
              },
            },
            completion = {
              modes = {
                i = "<C-x>",
              },
            },
          },
          slash_commands = {
            ["buffer"] = {
              opts = {
                keymaps = {
                  modes = {
                    i = "<C-b>",
                  },
                },
              },
            },
            ["help"] = {
              opts = {
                max_lines = 1000,
              },
            },
          },
          tools = {
            vectorcode = {
              description = "Run VectorCode to retrieve the project context.",
              callback = function()
                return require("vectorcode.integrations").codecompanion.chat.make_tool()
              end,
            },
            opts = {
              auto_submit_success = true,
              auto_submit_errors = false,
            },
          },
        },
        inline = { adapter = inline_adapter },
      }

      return {
        adapters = adapters,
        strategies = strategies,
        display = display,
        extensions = extensions,
        prompt_library = prompt_library,
      }
    end,
    init = function()
      require("plugins.custom.spinner"):init()
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
