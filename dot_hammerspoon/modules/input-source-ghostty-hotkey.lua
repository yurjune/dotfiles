-- Switch input source to English when Ctrl+Cmd+H or Ctrl+Cmd+L is pressed in Ghostty

local englishInputSource = "ABC"
local ghosttyBundleID = "com.mitchellh.ghostty"

local function switchToEnglish()
	hs.keycodes.setLayout(englishInputSource)
end

-- Function to check if current focused app is Ghostty
local function isGhosttyFocused()
	local focusedApp = hs.application.frontmostApplication()
	return focusedApp and focusedApp:bundleID() == ghosttyBundleID
end

-- Clean up existing eventtap if it exists
if _G.ghosttyEventTap then
	_G.ghosttyEventTap:stop()
	_G.ghosttyEventTap = nil
end

-- Create eventtap to intercept key events
_G.ghosttyEventTap = hs.eventtap.new({ hs.eventtap.event.types.keyDown }, function(event)
	local keyCode = event:getKeyCode()
	local flags = event:getFlags()

	-- Check for Ctrl+Cmd+H (keyCode 4 = H) or Ctrl+Cmd+L (keyCode 37 = L)
	local hasCtrl = flags.ctrl
	local hasCmd = flags.cmd
	local isHKey = keyCode == 4
	local isLKey = keyCode == 37

	if hasCtrl and hasCmd and (isHKey or isLKey) and isGhosttyFocused() then
		-- Switch input source
		switchToEnglish()

		-- Let the original key event pass through
		return false
	end

	-- Let all other events pass through
	return false
end)

-- Start the eventtap
_G.ghosttyEventTap:start()
