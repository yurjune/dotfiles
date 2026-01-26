-- toggle desktop 1 <-> 2
hs.hotkey.bind({ "ctrl" }, "2", function()
	local currentSpace = hs.spaces.focusedSpace()
	local allSpaces = hs.spaces.allSpaces()
	local mainScreen = hs.screen.mainScreen():getUUID()
	local spaces = allSpaces[mainScreen]

	if currentSpace == spaces[1] then
		-- Setting > Keyboard > Keyboard Shortcut > Mission Control > Your shortcut
		hs.eventtap.keyStroke({ "cmd", "alt", "ctrl" }, "2", 0)
	else
		hs.eventtap.keyStroke({ "cmd", "alt", "ctrl" }, "1", 0)
	end
end)
