-- Switch input source to English when focused on a specific app.

local englishInputSource = "ABC"
local targetApps = {
	"com.todesktop.230313mzl4w4u92", -- Cursor
	"com.microsoft.VSCode", -- VSCode
	"com.mitchellh.ghostty", -- Ghostty
	"com.neovide.neovide", -- Neovide
}

function _G.applicationWatcherCallback(appName, eventType, appObject)
	if eventType == hs.application.watcher.activated then
		local bundleID = appObject:bundleID()
		if not bundleID then
			return
		end

		for _, targetApp in ipairs(targetApps) do
			if bundleID == targetApp then
				-- Using a timer is good practice to ensure the app is fully focused.
				hs.timer.doAfter(0.1, function()
					hs.keycodes.setLayout(englishInputSource)
				end)
				break
			end
		end
	end
end

-- Stop any previously running watcher before starting a new one.
-- This check is now primarily in init.lua, but kept here for robustness
-- in case the module is reloaded manually.
if _G.appWatcher and _G.appWatcher.stop then
	_G.appWatcher:stop()
end

-- Storing watcher in a global variable to prevent being garbage collected.
_G.appWatcher = hs.application.watcher.new(_G.applicationWatcherCallback)
_G.appWatcher:start()
