-- 특정 앱으로 전환할 때 키보드 입력을 영문으로 전환하는 스크립트

-- 영문 입력소스 ID (실제 시스템에서 확인된 값)
local englishInputSource = "ABC"

local targetApps = {
    "com.todesktop.230313mzl4w4u92",  -- Cursor
    "com.microsoft.VSCode",           -- VSCode
    "com.mitchellh.ghostty",          -- Ghostty
    "com.neovide.neovide"             -- Neovide
}

function switchToEnglish()
    hs.keycodes.setLayout(englishInputSource)
end

-- 앱이 활성화될 때 호출되는 함수
function applicationWatcher(appName, eventType, appObject)
    if eventType == hs.application.watcher.activated then
        local bundleID = appObject:bundleID()
        
        -- 영문 전환 대상 앱인지 확인
        for _, targetApp in ipairs(targetApps) do
            if bundleID == targetApp then
                -- 약간의 지연 후 입력 소스 변경 (앱 전환이 완전히 끝난 후)
                hs.timer.doAfter(0.1, function()
                    switchToEnglish()
                end)
                break
            end
        end
    end
end

-- 앱 감시자 시작
appWatcher = hs.application.watcher.new(applicationWatcher)
appWatcher:start()
