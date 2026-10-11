"""Offline rule-based Lua module composer; not a trained language model."""
import re

MODULES = {
 'speed': r'''-- Speed: use the slider-like variable below
local speedValue = 32
local function applySpeed(character)
    local humanoid = character:WaitForChild("Humanoid", 5)
    if humanoid then humanoid.WalkSpeed = speedValue end
end
applySpeed(player.Character or player.CharacterAdded:Wait())
player.CharacterAdded:Connect(applySpeed)
''',
 'highlight': r'''-- Highlight players; clean up on exit
local highlights = {}
local function highlightPlayer(other)
    if other == player then return end
    local function attach(character)
        if highlights[other] then highlights[other]:Destroy() end
        local marker = Instance.new("Highlight")
        marker.Name = "ScriptHuntHighlight"
        marker.FillColor = Color3.fromRGB(255, 200, 30)
        marker.OutlineColor = Color3.fromRGB(255, 255, 255)
        marker.DepthMode = Enum.HighlightDepthMode.AlwaysOnTop
        marker.Parent = character
        highlights[other] = marker
    end
    if other.Character then attach(other.Character) end
    other.CharacterAdded:Connect(attach)
end
for _, other in ipairs(Players:GetPlayers()) do highlightPlayer(other) end
Players.PlayerAdded:Connect(highlightPlayer)
Players.PlayerRemoving:Connect(function(other)
    if highlights[other] then highlights[other]:Destroy() end
    highlights[other] = nil
end)
''',
 'fly': r'''-- Fly toggle: F key on desktop; requires a local character and camera
local flying = false
local flySpeed = 55
local flyVelocity, flyGyro
local function stopFly()
    flying = false
    if flyVelocity then flyVelocity:Destroy(); flyVelocity = nil end
    if flyGyro then flyGyro:Destroy(); flyGyro = nil end
    local hum = player.Character and player.Character:FindFirstChildOfClass("Humanoid")
    if hum then hum.PlatformStand = false end
end
local function startFly()
    local char = player.Character
    local root = char and char:FindFirstChild("HumanoidRootPart")
    local hum = char and char:FindFirstChildOfClass("Humanoid")
    if not (root and hum) then return end
    flying = true
    hum.PlatformStand = true
    flyVelocity = Instance.new("BodyVelocity")
    flyVelocity.MaxForce = Vector3.new(1e6, 1e6, 1e6)
    flyVelocity.Parent = root
    flyGyro = Instance.new("BodyGyro")
    flyGyro.MaxTorque = Vector3.new(1e6, 1e6, 1e6)
    flyGyro.P = 1e4
    flyGyro.Parent = root
end
local UIS = game:GetService("UserInputService")
local RunService = game:GetService("RunService")
UIS.InputBegan:Connect(function(input, processed)
    if not processed and input.KeyCode == Enum.KeyCode.F then
        if flying then stopFly() else startFly() end
    end
end)
RunService.RenderStepped:Connect(function()
    if not flying then return end
    local cam = workspace.CurrentCamera
    if not (cam and flyVelocity and flyGyro) then stopFly(); return end
    local direction = Vector3.zero
    if UIS:IsKeyDown(Enum.KeyCode.W) then direction += cam.CFrame.LookVector end
    if UIS:IsKeyDown(Enum.KeyCode.S) then direction -= cam.CFrame.LookVector end
    if UIS:IsKeyDown(Enum.KeyCode.D) then direction += cam.CFrame.RightVector end
    if UIS:IsKeyDown(Enum.KeyCode.A) then direction -= cam.CFrame.RightVector end
    if UIS:IsKeyDown(Enum.KeyCode.Space) then direction += Vector3.yAxis end
    if UIS:IsKeyDown(Enum.KeyCode.LeftControl) then direction -= Vector3.yAxis end
    flyVelocity.Velocity = direction.Magnitude > 0 and direction.Unit * flySpeed or Vector3.zero
    flyGyro.CFrame = cam.CFrame
end)
player.CharacterAdded:Connect(stopFly)
''',
}
ALIASES = {
 'speed': ('speed', 'скорост', 'спид', 'walkspeed'),
 'highlight': ('esp', 'подсвет', 'highlight', 'обводк'),
 'fly': ('fly', 'полет', 'полёт', 'летать', 'летат', 'флай'),
}

def build(prompt):
    prompt = prompt.lower()
    selected = [name for name, terms in ALIASES.items() if any(t in prompt for t in terms)]
    if not selected:
        return None, []
    header = '-- Script Hunt AI Engine: offline module composer\n-- No runtime testing performed; compatibility depends on game/client\nlocal Players = game:GetService("Players")\nlocal player = Players.LocalPlayer\nif not player then return end\n\n'
    return header + '\n'.join(MODULES[x] for x in selected), selected

def check(code):
    if not code or len(code) > 100000: return False, 'Empty or oversized output'
    if any(x in code.lower() for x in ('loadstring(', 'httpget(', 'writefile(', 'readfile(')):
        return False, 'Unexpected remote or file operation'
    if code.count('(') != code.count(')'):
        return False, 'Unbalanced parentheses (basic check)'
    return True, 'Basic structure checked; no Lua runtime test'
