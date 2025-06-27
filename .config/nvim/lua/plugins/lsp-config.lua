local vtsls = {
  settings = {
    complete_function_calls = true,
    vtsls = {
      enableMoveToFileCodeAction = true,
      experimental = {
        maxInlayHintLength = 30,
        completion = {
          enableServerSideFuzzyMatch = true,
          entriesLimit = 10,
        },
      },
    },
    typescript = {
      updateImportsOnFileMove = { enabled = "always" },
      tsserver = {
        maxTsServerMemory = 16184,
      },
      suggest = {
        completeFunctionCalls = true,
      },
      inlayHints = {
        enumMemberValues = { enabled = true },
        functionLikeReturnTypes = { enabled = true },
        parameterNames = { enabled = "literals" },
        parameterTypes = { enabled = true },
        propertyDeclarationTypes = { enabled = true },
        variableTypes = { enabled = false },
      },
    },
  },
}

return {
  {
    "neovim/nvim-lspconfig",
    opts = {
      servers = {
        vtsls = vtsls,
      },
    },
  },
}
