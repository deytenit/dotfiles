local function get_arc_root()
  if vim.fn.executable("arc") == 0 then
    return nil
  end
  local result = vim.system({ "arc", "root" }, { text = true }):wait()
  if result.code == 0 and result.stdout then
    return vim.trim(result.stdout)
  end
  return nil
end

local ARC_ROOT = get_arc_root()

--- Detect total system RAM in GB.
--- Supports Linux (/proc/meminfo) and macOS (sysctl).
local function get_total_ram_gb()
  local f = io.open("/proc/meminfo", "r")
  if f then
    local content = f:read("*a")
    f:close()
    local kb = content:match("MemTotal:%s+(%d+)")
    if kb then
      return math.floor(tonumber(kb) / 1024 / 1024)
    end
  end

  if vim.fn.executable("sysctl") == 1 then
    local result = vim.system({ "sysctl", "-n", "hw.memsize" }, { text = true }):wait()
    if result.code == 0 and result.stdout then
      local bytes = tonumber(vim.trim(result.stdout))
      if bytes then
        return math.floor(bytes / 1024 / 1024 / 1024)
      end
    end
  end

  return nil
end

--- min(max(4, total/2), 32) GB — diminishing returns, hard cap at 32 GB.
local function tsgo_memory_bytes()
  local total_gb = get_total_ram_gb()
  if not total_gb or total_gb == 0 then
    return 8 * 1024 * 1024 * 1024 -- 8 GB fallback
  end
  local limit_gb = math.max(4, math.min(math.floor(total_gb / 2), 32))
  return limit_gb * 1024 * 1024 * 1024
end

local TSGO_MEMORY_BYTES = tsgo_memory_bytes()

local function resolve_tsgo_cmd(root_dir)
  local candidates = {}

  if root_dir then
    table.insert(candidates, vim.fs.joinpath(root_dir, "node_modules/.bin", "tsgo"))
  end

  if ARC_ROOT then
    table.insert(
      candidates,
      vim.fs.joinpath(
        ARC_ROOT,
        "adv/frontend/packages/direct-modules/node_modules/.bin/tsgo"
      )
    )
  end

  table.insert(candidates, "tsgo")

  for _, cmd in ipairs(candidates) do
    if cmd == "tsgo" or vim.fn.executable(cmd) == 1 then
      return cmd
    end
  end
end

local tsgo_settings = {
  typescript = {
    preferences = {
      importModuleSpecifierEnding = "minimal",
      importModuleSpecifierPreference = "non-relative",
    },
    inlayHints = {
      parameterNames = {
        enabled = "literals",
        suppressWhenArgumentMatchesName = true,
      },
      parameterTypes = { enabled = true },
      variableTypes = { enabled = true },
      propertyDeclarationTypes = { enabled = true },
      functionLikeReturnTypes = { enabled = true },
      enumMemberValues = { enabled = true },
    },
  },
}

local function tsgo_cmd(dispatchers, config)
  local cmd = resolve_tsgo_cmd(config and config.root_dir)
  return vim.lsp.rpc.start({ cmd, "--lsp", "--stdio" }, dispatchers, {
    env = { GOMEMLIMIT = tostring(TSGO_MEMORY_BYTES) },
  })
end

local function tsgo_root_dir(bufnr, on_dir)
  local root_markers = {
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "bun.lockb",
    "bun.lock",
  }

  root_markers = vim.fn.has("nvim-0.11.3") == 1
      and { root_markers, { ".git" } }
    or vim.list_extend(root_markers, { ".git" })

  local deno_root = vim.fs.root(bufnr, { "deno.json", "deno.jsonc" })
  local deno_lock_root = vim.fs.root(bufnr, { "deno.lock" })
  local project_root = vim.fs.root(bufnr, root_markers)

  if deno_lock_root and (not project_root or #deno_lock_root > #project_root) then
    return
  end

  if deno_root and (not project_root or #deno_root >= #project_root) then
    return
  end

  on_dir(project_root or vim.fn.getcwd())
end

local tsgo_config = {
  enabled = true,
  cmd = tsgo_cmd,
  filetypes = {
    "javascript",
    "javascriptreact",
    "typescript",
    "typescriptreact",
  },
  root_dir = tsgo_root_dir,
  settings = tsgo_settings,
}

return {
  {
    "neovim/nvim-lspconfig",
    opts = {
      servers = {
        vtsls = false,
        tsgo = tsgo_config,
      },
    },
  },
}
