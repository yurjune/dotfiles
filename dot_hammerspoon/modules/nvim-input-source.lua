-- Manage the macOS input source for Neovim through the Hammerspoon CLI.

-- Enable the IPC bridge that lets Neovim call this module through `hs -c`.
require("hs.ipc")

local englishInputSource = "com.apple.keylayout.ABC"
local lastInputSource = nil

local M = {}

function M.leaveInsert()
	lastInputSource = hs.keycodes.currentSourceID()
	hs.keycodes.currentSourceID(englishInputSource)
end

function M.enterInsert()
	if lastInputSource and lastInputSource ~= englishInputSource then
		hs.keycodes.currentSourceID(lastInputSource)
	end
end

function M.switchToEnglish()
	hs.keycodes.currentSourceID(englishInputSource)
end

-- Expose the module to commands evaluated by the `hs` CLI.
_G.nvimInputSource = M

return M
