-- Temporarily switch to English for terminal Ctrl shortcuts in Ghostty.
-- This lets terminal Ctrl-letter shortcuts pass through the normal input path
-- even when the current macOS input source is Korean.

local englishInputSource = "com.apple.keylayout.ABC"
local ghosttyBundleID = "com.mitchellh.ghostty"
local eventTypes = hs.eventtap.event.types
local spaceKeyCode = hs.keycodes.map.space

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

_G.ghosttyCtrlInputSourceEventTap = hs.eventtap.new({ eventTypes.flagsChanged, eventTypes.keyDown }, function(event)
	local flags = event:getFlags()

	if not flags.ctrl or not isGhosttyFocused() then
		finishCtrlShortcut()
	elseif flags.cmd or flags.alt then
		cancelRestore()
	elseif event:getType() == eventTypes.keyDown then
		-- Let macOS handle its Ctrl+Space input-source shortcut.
		if event:getKeyCode() == spaceKeyCode then
			finishCtrlShortcut()
		else
			beginCtrlShortcut()
		end
	end

	return false
end)

_G.ghosttyCtrlInputSourceEventTap:start()
