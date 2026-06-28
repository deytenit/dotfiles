-- Cached helpers for detecting an Arcadia (arc) repository.
-- `arc root` is a synchronous subprocess and was previously spawned several
-- times during startup; the result is computed once and reused.

local M = {}

local checked = false
local root_cache = nil

--- Absolute path of the enclosing arc repo, or nil when not in one.
function M.root()
  if not checked then
    checked = true
    if vim.fn.executable("arc") == 1 then
      local result = vim.system({ "arc", "root" }, { text = true }):wait()
      if result.code == 0 and result.stdout then
        root_cache = vim.trim(result.stdout)
      end
    end
  end
  return root_cache
end

--- Whether the current directory is inside an arc repo.
function M.is_repo()
  return M.root() ~= nil
end

return M
