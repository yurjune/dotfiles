-- Manage the macOS input source for Neovim through the Hammerspoon CLI.

-- Enable the IPC bridge that lets Neovim call this module through `hs -c`.
require("hs.ipc")

local englishInputSource = "com.apple.keylayout.ABC"
local lastInputSource = nil

local M = {}

function M.saveCurrentSource()
	lastInputSource = hs.keycodes.currentSourceID()
end

function M.restoreSavedSource()
	if lastInputSource then
		hs.keycodes.currentSourceID(lastInputSource)
	end
end

function M.switchToEnglish()
	hs.keycodes.currentSourceID(englishInputSource)
end

function M.saveSourceAndSwitchToEnglish()
	M.saveCurrentSource()
	M.switchToEnglish()
end

-- Expose the module to commands evaluated by the `hs` CLI.
_G.nvimInputSource = M

return M
