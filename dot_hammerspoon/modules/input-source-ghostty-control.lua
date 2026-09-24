-- Temporarily switch to English while Ctrl is held in Ghostty.
-- This lets terminal Ctrl-letter shortcuts pass through the normal input path
-- even when the current macOS input source is Korean.

local englishInputSource = "com.apple.keylayout.ABC"
local ghosttyBundleID = "com.mitchellh.ghostty"

local savedInputSource = nil

local function isGhosttyFocused()
	local focusedApp = hs.application.frontmostApplication()
	return focusedApp and focusedApp:bundleID() == ghosttyBundleID
end

local function currentSource()
	return hs.keycodes.currentSourceID()
end

local function switchSource(sourceID)
	if sourceID and currentSource() ~= sourceID then
		hs.keycodes.currentSourceID(sourceID)
	end
end

local function beginCtrlShortcut()
	if savedInputSource then
		return
	end

	savedInputSource = currentSource()
	switchSource(englishInputSource)
end

local function finishCtrlShortcut()
	local sourceToRestore = savedInputSource
	savedInputSource = nil

	if sourceToRestore then
		switchSource(sourceToRestore)
	end
end

local function cancelRestore()
	savedInputSource = nil
end

if _G.ghosttyCtrlInputSourceEventTap then
	_G.ghosttyCtrlInputSourceEventTap:stop()
	_G.ghosttyCtrlInputSourceEventTap = nil
end

_G.ghosttyCtrlInputSourceEventTap = hs.eventtap.new({ hs.eventtap.event.types.flagsChanged }, function(event)
	local flags = event:getFlags()
	local hasCtrl = flags.ctrl
	local hasCmdOrAlt = flags.cmd or flags.alt

	if not isGhosttyFocused() then
		if savedInputSource then
			finishCtrlShortcut()
		end
		return false
	end

	if hasCtrl and not hasCmdOrAlt then
		beginCtrlShortcut()
	elseif savedInputSource and hasCtrl and hasCmdOrAlt then
		cancelRestore()
	elseif savedInputSource and not hasCtrl then
		finishCtrlShortcut()
	end

	return false
end)

_G.ghosttyCtrlInputSourceEventTap:start()
