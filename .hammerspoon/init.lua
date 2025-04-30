-- Required Hammerspoon Modules
local fs = require("hs.fs")
local task = require("hs.task")
local logger = hs.logger.new("AppearanceSwitcher")

logger.i("--- Hammerspoon Config Loading ---")

-- Load the custom darkmode library
local dm = require("darkmode")
if not dm then
    logger.e("Failed to load darkmode.lua library. Ensure it is in ~/.hammerspoon/")
    return -- Stop loading if library fails
end

-- Define paths relative to the Hammerspoon config directory
local configDir = hs.configdir
local scriptsBaseDir = configDir .. "/scripts"
local darkScriptsDir = scriptsBaseDir .. "/dark-mode.d"
local lightScriptsDir = scriptsBaseDir .. "/light-mode.d"

-- --- Helper Function to Run Scripts in a Directory ---
-- Takes a directory path, finds executable files within it, and runs them.
local function runScriptsInDirectory(dirPath)
    logger.i("Attempting to run scripts in: " .. dirPath)

    -- Check if the directory exists
    local dirAttrs = fs.attributes(dirPath)
    if not dirAttrs or dirAttrs.mode ~= "directory" then
        logger.w("Directory not found or is not a directory: " .. dirPath)
        return
    end

    local fileList = {}
    for file in fs.dir(dirPath) do
        table.insert(fileList, file)
    end

    if #fileList == 0 then
        logger.i("No scripts found in: " .. dirPath)
        return
    end

    for _, file in ipairs(fileList) do
        -- Skip hidden files (like .DS_Store)
        if string.sub(file, 1, 1) ~= "." then
            local scriptPath = dirPath .. "/" .. file
            local attrs = fs.attributes(scriptPath)

            -- Check if it's a file
            if attrs and attrs.mode == "file" then
                 -- Ensure the script has execute permissions (`chmod +x script.sh`)
                logger.i("Executing script: " .. scriptPath)
                local runner = task.new(scriptPath, function(exitCode, stdOut, stdErr)
                    if exitCode == 0 then
                        logger.i("Script finished successfully: " .. scriptPath)
                        if stdOut and stdOut ~= "" then logger.d("stdout:\n" .. stdOut) end
                        if stdErr and stdErr ~= "" then logger.w("stderr:\n" .. stdErr) end
                    else
                        logger.e("Script failed: " .. scriptPath .. " (Exit Code: " .. exitCode .. ")")
                        if stdOut and stdOut ~= "" then logger.e("stdout:\n" .. stdOut) end
                        if stdErr and stdErr ~= "" then logger.e("stderr:\n" .. stdErr) end
                    end
                end)
                if runner then
                    local started = runner:start()
                    if not started then
                        logger.e("Failed to start task for script: " .. scriptPath)
                    end
                else
                    logger.e("Failed to create task for script: " .. scriptPath)
                end
            else
                logger.w("Skipping non-file or unreadable item: " .. scriptPath .. (attrs and (" (mode: " .. attrs.mode .. ")") or " (attributes not found)"))
            end
        end
    end
end

-- --- Appearance Change Handler ---
-- This function is called by the darkmode library when the mode changes.
local function handleAppearanceChange(isDarkMode)
    if isDarkMode then
        logger.i("System switched to DARK mode.")
        runScriptsInDirectory(darkScriptsDir)
    else
        logger.i("System switched to LIGHT mode.")
        runScriptsInDirectory(lightScriptsDir)
    end
end

-- --- Initialization ---

-- Register the handler with the darkmode library
dm.addHandler(handleAppearanceChange)
logger.i("Dark mode change handler registered.")

-- Run scripts for the *current* mode on startup/reload
logger.i("Running initial scripts based on current mode...")
local currentModeIsDark = dm.getDarkMode()
handleAppearanceChange(currentModeIsDark) -- Call the handler directly

-- Optional: Add a notification on reload
-- hs.notify.new({title="Hammerspoon", informativeText="Config reloaded."}):send()

