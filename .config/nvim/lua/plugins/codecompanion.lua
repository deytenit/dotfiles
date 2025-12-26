local shared_adapter_shema = require("etc.codecompanion.schemas.shared")

local prompt_library = {}

-- Load all workflows from the workflows directory
local workflow_dir = vim.fn.stdpath("config") .. "/lua/etc/codecompanion/workflows"
if vim.fn.isdirectory(workflow_dir) == 1 then
  local workflow_files = vim.fn.glob(workflow_dir .. "/*.lua", false, true)
  for _, file in ipairs(workflow_files) do
    local ok, workflow = pcall(require, "etc.codecompanion.workflows." .. vim.fn.fnamemodify(file, ":t:r"))
    if ok then
      prompt_library = vim.tbl_extend("force", prompt_library, workflow)
    end
  end
end

return {
  {
    "olimorris/codecompanion.nvim",
    dependencies = {
      "nvim-treesitter/nvim-treesitter",
      {
        "ravitemer/mcphub.nvim",
        cmd = "MCPHub",
        build = "npm install -g mcp-hub@latest",
        config = true,
        opts = {
          make_vars = true,
        }
      },
      {
        "Davidyz/VectorCode",
        version = "*",
        build = "uv tool upgrade vectorcode",
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
        yalm_anthropic = function()
          return require("codecompanion.adapters").extend("anthropic", {
            url = "https://api.eliza.yandex.net/raw/anthropic/v1/messages",
            env = {
              api_key = "cmd:cat ~/.eliza_token",
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
        main_adapter = "yalm_anthropic"
        inline_adapter = "yalm_deepseek_v3"
      else
        vim.notify("CodeCompanion: Using 'copilot' adapter", vim.log.levels.INFO)
        main_adapter = "copilot_gemini_pro"
        inline_adapter = "copilot_gemini_flash"
        adapters.opts = {
          allow_insecure = true,
          -- xray proxy
          proxy = "socks5://127.0.0.1:10808",
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
            opts = {
              auto_submit_success = true,
              auto_submit_errors = false,
            },
          },
        },
        inline = { adapter = inline_adapter },
      }

      local memory = {
        default = {
          description = "My default group",
          files = {
            "AGENTS.md",
          },
        },
        opts = {
          chat = {
            enabled = true,
            default_memory = { "default" },
          },
        },
      }

      return {
        adapters = adapters,
        strategies = strategies,
        display = display,
        extensions = extensions,
        prompt_library = prompt_library,
        memory = memory,
      }
    end,
    init = function()
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
