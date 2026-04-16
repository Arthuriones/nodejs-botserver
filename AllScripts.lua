if true then
-- !ConexaoBotServer.lua

-- --[REQUIRED] Change BotServer URL
-- Local/VPS: ws://IP:PORTA/
-- Railway:   wss://SEU-APP.railway.app/
BotServer.url = "ws://37.148.133.154:8000/"


local playerName = name()
local channel = "1"
BotServer.init(playerName, channel)

--[REQUIRED] Keep Connection Alive
macro(1000, function()
  if BotServer._websocket then
    BotServer._websocket.send({type="ping"})
  end
end)
end

if true then
-- ComboSystemNav.otui
g_ui.loadUIFromString([[
ComboNameItem < Label
  background-color: alpha
  text-offset: 2 0
  focusable: true
  height: 16
  padding-right: 10

  $focus:
    background-color: #00000055

  Button
    id: remove
    text: x
    anchors.right: parent.right
    margin-right: 2
    width: 14
    height: 14

  Button
    id: down
    text: v
    anchors.right: prev.left
    margin-right: 2
    width: 14
    height: 14

  Button
    id: up
    text: ^
    anchors.right: prev.left
    margin-right: 2
    width: 14
    height: 14

ComboListBlock < Panel
  height: 110
  margin-top: 3

  TextList
    id: list
    anchors.top: parent.top
    anchors.left: parent.left
    anchors.right: parent.right
    height: 83
    padding: 1
    vertical-scrollbar: listScrollBar

  VerticalScrollBar
    id: listScrollBar
    anchors.top: list.top
    anchors.bottom: list.bottom
    anchors.right: list.right
    step: 14
    pixels-scroll: true

  TextEdit
    id: nameEdit
    anchors.left: parent.left
    anchors.top: list.bottom
    margin-top: 5
    width: 110

  Button
    id: addBtn
    text: +
    anchors.right: parent.right
    anchors.left: nameEdit.right
    anchors.top: nameEdit.top
    margin-left: 3

ComboVocItem < Panel
  height: 20
  margin-top: 7

  BotSwitch
    id: check
    anchors.left: parent.left
    anchors.top: parent.top
    width: 80
    text-align: center

  TextEdit
    id: priority
    anchors.left: prev.right
    anchors.top: parent.top
    anchors.right: parent.right
    margin-left: 10
    text-align: center

ComboVocWindow < MainWindow
  text: Configuracao Vocacao
  size: 260 200
  @onEscape: self:hide()

  Label
    !text: string.format("Ativar Voc e Prioridade (Ex: %d)\n(prioridade menor ataca primeiro)", 1)
    anchors.top: parent.top
    anchors.left: parent.left
    anchors.right: parent.right
    text-align: center
    text-auto-resize: true

  ComboVocItem
    id: vocEK
    anchors.top: prev.bottom
    anchors.left: parent.left
    anchors.right: parent.right

  ComboVocItem
    id: vocED
    anchors.top: prev.bottom
    anchors.left: parent.left
    anchors.right: parent.right

  ComboVocItem
    id: vocMS
    anchors.top: prev.bottom
    anchors.left: parent.left
    anchors.right: parent.right

  ComboVocItem
    id: vocRP
    anchors.top: prev.bottom
    anchors.left: parent.left
    anchors.right: parent.right

  Button
    id: closeBtn
    text: Salvar
    anchors.bottom: parent.bottom
    anchors.right: parent.right
    width: 60

ComboHelpWindow < MainWindow
  text: Ajuda - Prioridades
  size: 500 250
  @onEscape: self:hide()

  Label
    id: desc
    !text: string.format("* Ordem da lista: Ataca os nomes de cima para baixo presentes na janela.\n\n* Por Vocacao: Ataca apenas as vocacoes marcadas no Config, seguindo a hierarquia do numero que voce colocou nelas (numero menor = ataca primeiro).\n\n* Por Level: Ordena do maior para o menor level (ou vice-versa).\n\n* Vocacao + Level: A sua Vocacao eh quem dita quem morre antes, mas se dois alvos tiverem o mesmo numero de prioridade (ex: 1), o desempate pra atacar sera o Level deles.\n\n*Nomes na lista tem prioridade sobre guild inimiga.")
    anchors.top: parent.top
    anchors.left: parent.left
    anchors.right: parent.right
    margin-bottom: 40
    text-align: topleft
    text-wrap: true
    text-auto-resize: true

  Button
    id: closeBtn
    text: Fechar
    anchors.bottom: parent.bottom
    anchors.right: parent.right
    width: 60

ComboWindow < MainWindow
  text: Combo Settings
  size: 500 400
  @onEscape: self:hide()

  Label
    id: lblLider
    text: Lideres
    anchors.top: parent.top
    anchors.left: parent.left
    width: 140
    text-align: center

  Label
    id: lblConnected
    text: Conectados
    anchors.top: parent.top
    anchors.left: lblLider.right
    margin-left: 50
    width: 140
    text-align: center

  Label
    id: lblEnemy
    text: Inimigos
    anchors.top: parent.top
    anchors.right: parent.right
    width: 140
    text-align: center

  ComboListBlock
    id: leaderListBlock
    anchors.top: lblLider.bottom
    anchors.left: parent.left
    width: 140

  Button
    id: btnMoveLeft
    text: <
    anchors.left: leaderListBlock.right
    anchors.top: leaderListBlock.top
    margin-left: 5
    margin-top: 30
    width: 20
    height: 20

  Button
    id: btnMoveRight
    text: >
    anchors.left: btnMoveLeft.right
    anchors.top: btnMoveLeft.top
    margin-left: 3
    width: 20
    height: 20

  ComboListBlock
    id: connectedListBlock
    anchors.top: lblConnected.bottom
    anchors.left: btnMoveRight.right
    margin-left: 5
    width: 140

  ComboListBlock
    id: enemyListBlock
    anchors.top: lblEnemy.bottom
    anchors.right: parent.right
    width: 140

  BotSwitch
    id: btnEnemyGuild
    text: Add Guild Inimiga
    anchors.top: enemyListBlock.bottom
    anchors.left: enemyListBlock.left
    anchors.right: enemyListBlock.right
    margin-top: 10

  HorizontalSeparator
    id: sep1
    anchors.top: btnEnemyGuild.bottom
    anchors.left: parent.left
    anchors.right: parent.right
    margin-top: 10

  Label
    id: lblPrio
    text: Prioridade de Ataque (Hotkey):
    anchors.top: prev.bottom
    anchors.left: parent.left
    anchors.right: parent.right
    margin-top: 10
    text-align: center

  BotSwitch
    id: btnOrder
    text: Ordem da Lista
    anchors.top: prev.bottom
    anchors.left: parent.left
    anchors.right: parent.horizontalCenter
    margin-right: 5
    margin-top: 5

  BotSwitch
    id: btnVoc
    text: Por Vocacao
    anchors.top: prev.top
    anchors.left: parent.horizontalCenter
    anchors.right: parent.right
    margin-left: 5

  Button
    id: btnVocSetup
    text: Config Vocacao
    anchors.top: btnVoc.bottom
    anchors.left: btnVoc.left
    anchors.right: btnVoc.right
    margin-top: 2
    height: 18

  BotSwitch
    id: btnLevel
    text: Por Level (Asc)
    anchors.top: btnOrder.bottom
    anchors.left: parent.left
    anchors.right: parent.horizontalCenter
    margin-right: 5
    margin-top: 5

  HorizontalSeparator
    id: sep3
    anchors.top: btnLevel.bottom
    anchors.left: parent.left
    anchors.right: parent.right
    margin-top: 10

  Button
    id: helpBtn
    text: Help
    anchors.bottom: parent.bottom
    anchors.left: parent.left
    width: 60

  Button
    id: btnSyncList
    text: Sync List
    anchors.bottom: parent.bottom
    anchors.left: prev.right
    margin-left: 10
    width: 80

  Button
    id: closeBtn
    text: Fechar
    anchors.bottom: parent.bottom
    anchors.right: parent.right
    width: 60
]])
end

if true then
-- ComboSystemNav.lua
if type(storage.Combo) ~= "table" then
  storage.Combo = {}
end

local settings = storage.Combo

if settings.enabled == nil then settings.enabled = false end
if type(settings.leaderList) ~= "table" then settings.leaderList = {} end
if type(settings.enemyList) ~= "table" then settings.enemyList = {} end
if type(settings.voc) ~= "table" then settings.voc = {} end

local defaultVoc = {
  EK = { enabled = true, prio = 1 },
  ED = { enabled = true, prio = 2 },
  MS = { enabled = true, prio = 3 },
  RP = { enabled = true, prio = 4 },
}
for v, def in pairs(defaultVoc) do
  if type(settings.voc[v]) ~= "table" then settings.voc[v] = def end
end

if settings.hk == nil then settings.hk = "f5" end
if settings.levelDesc == nil then settings.levelDesc = false end

if settings.mode ~= nil then
  settings.useOrder = (settings.mode == 1)
  settings.useVoc = (settings.mode == 2)
  settings.useLevel = (settings.mode == 3)
  settings.mode = nil
end

if settings.useOrder == nil then settings.useOrder = true end
if settings.useVoc == nil then settings.useVoc = false end
if settings.useLevel == nil then settings.useLevel = false end
if settings.enemyGuild == nil then settings.enemyGuild = false end

local connectedMembers = {}

local comboUI = setupUI([[
Panel
  height: 19

  BotSwitch
    id: title
    anchors.top: parent.top
    anchors.left: parent.left
    text-align: center
    width: 130
    !text: tr('Combo System')

  Button
    id: push
    anchors.top: prev.top
    anchors.left: prev.right
    anchors.right: parent.right
    margin-left: 3
    height: 17
    text: Setup
]], parent)

local comboWindow = UI.createWindow('ComboWindow', rootWidget)
comboWindow:hide()

local vocWindow = UI.createWindow('ComboVocWindow', rootWidget)
vocWindow:hide()

local helpWindow = UI.createWindow('ComboHelpWindow', rootWidget)
helpWindow:hide()

comboUI.title:setOn(settings.enabled)
comboUI.title.onClick = function(widget)
  settings.enabled = not settings.enabled
  widget:setOn(settings.enabled)
end

comboUI.push.onClick = function()
  comboWindow:show()
  comboWindow:raise()
  comboWindow:focus()
end

comboWindow.closeBtn.onClick = function() comboWindow:hide() end
vocWindow.closeBtn.onClick = function() vocWindow:hide() end
helpWindow.closeBtn.onClick = function() helpWindow:hide() end

comboWindow.helpBtn.onClick = function()
  helpWindow:show()
  helpWindow:raise()
  helpWindow:focus()
end

comboWindow.btnVocSetup.onClick = function()
  vocWindow:show()
  vocWindow:raise()
  vocWindow:focus()
end

-- Refresh functions for lists
local function refreshLists()
  comboWindow.leaderListBlock.list:destroyChildren()
  for _, name in ipairs(settings.leaderList) do
    local label = g_ui.createWidget('ComboNameItem', comboWindow.leaderListBlock.list)
    label:setText(name)
    label.remove.onClick = function()
      table.removevalue(settings.leaderList, label:getText())
      refreshLists()
    end
    label.up.onClick = function()
      local idx = table.find(settings.leaderList, label:getText())
      if idx and idx > 1 then
        local temp = settings.leaderList[idx - 1]
        settings.leaderList[idx - 1] = settings.leaderList[idx]
        settings.leaderList[idx] = temp
        refreshLists()
      end
    end
    label.down.onClick = function()
      local idx = table.find(settings.leaderList, label:getText())
      if idx and idx < #settings.leaderList then
        local temp = settings.leaderList[idx + 1]
        settings.leaderList[idx + 1] = settings.leaderList[idx]
        settings.leaderList[idx] = temp
        refreshLists()
      end
    end
  end
  
  comboWindow.enemyListBlock.list:destroyChildren()
  for _, name in ipairs(settings.enemyList) do
    local label = g_ui.createWidget('ComboNameItem', comboWindow.enemyListBlock.list)
    label:setText(name)
    label.remove.onClick = function()
      table.removevalue(settings.enemyList, label:getText())
      refreshLists()
    end
    label.up.onClick = function()
      local idx = table.find(settings.enemyList, label:getText())
      if idx and idx > 1 then
        local temp = settings.enemyList[idx - 1]
        settings.enemyList[idx - 1] = settings.enemyList[idx]
        settings.enemyList[idx] = temp
        refreshLists()
      end
    end
    label.down.onClick = function()
      local idx = table.find(settings.enemyList, label:getText())
      if idx and idx < #settings.enemyList then
        local temp = settings.enemyList[idx + 1]
        settings.enemyList[idx + 1] = settings.enemyList[idx]
        settings.enemyList[idx] = temp
        refreshLists()
      end
    end
  end
  
  comboWindow.connectedListBlock.list:destroyChildren()
  for name, timestamp in pairs(connectedMembers) do
    if now - timestamp < 10000 then -- 10 seconds timeout
      -- A member cannot be in both lists
      if not table.contains(settings.leaderList, name, true) then
        local label = g_ui.createWidget('ComboNameItem', comboWindow.connectedListBlock.list)
        label:setText(name)
        label.remove:hide()
        label.up:hide()
        label.down:hide()
      end
    end
  end
end

refreshLists()

-- Setup List Add Buttons
local function setupListBlock(block, listTable)
  block.addBtn.onClick = function()
    local name = block.nameEdit:getText()
    if name:len() > 0 and not table.contains(listTable, name, true) then
      table.insert(listTable, name)
      refreshBothLists()
      block.nameEdit:setText('')
    end
  end
  block.nameEdit.onKeyPress = function(self, keyCode, keyboardModifiers)
    if keyCode == 5 then -- Enter
      block.addBtn.onClick()
      return true
    end
    return false
  end
end

setupListBlock(comboWindow.enemyListBlock, settings.enemyList)

-- Hide input fields for leader and connected lists as they are automatic
comboWindow.leaderListBlock.nameEdit:hide()
comboWindow.leaderListBlock.addBtn:hide()
comboWindow.leaderListBlock:setHeight(85)
comboWindow.connectedListBlock.nameEdit:hide()
comboWindow.connectedListBlock.addBtn:hide()
comboWindow.connectedListBlock:setHeight(85)

-- Move buttons logic
comboWindow.btnMoveLeft.onClick = function()
  local focused = comboWindow.connectedListBlock.list:getFocusedChild()
  if focused then
    local name = focused:getText()
    if not table.contains(settings.leaderList, name, true) then
      table.insert(settings.leaderList, name)
      refreshLists()
    end
  end
end

comboWindow.btnMoveRight.onClick = function()
  local focused = comboWindow.leaderListBlock.list:getFocusedChild()
  if focused then
    local name = focused:getText()
    table.removevalue(settings.leaderList, name)
    refreshLists()
  end
end

comboWindow.btnSyncList.onClick = function()
  local data = {
    leaderList = settings.leaderList,
    enemyList = settings.enemyList,
    useOrder = settings.useOrder,
    useVoc = settings.useVoc,
    useLevel = settings.useLevel,
    levelDesc = settings.levelDesc,
    voc = settings.voc
  }
  
  BotServer.send("SyncEnemyList", data)
end


comboWindow.btnEnemyGuild.onClick = function(w)
  settings.enemyGuild = not settings.enemyGuild
  w:setOn(settings.enemyGuild)
end

-- Checkboxes logic
local function updateCheckboxes()
  comboWindow.btnOrder:setOn(settings.useOrder)
  comboWindow.btnVoc:setOn(settings.useVoc)
  comboWindow.btnLevel:setOn(settings.useLevel)
  
  if settings.useLevel then
    comboWindow.btnLevel:setText(settings.levelDesc and "Level (Maior->Menor)" or "Level (Menor->Maior)")
  else
    comboWindow.btnLevel:setText("Por Level")
  end
end

comboWindow.btnOrder.onClick = function()
  settings.useOrder = true
  settings.useVoc = false
  settings.useLevel = false
  updateCheckboxes()
end

comboWindow.btnVoc.onClick = function()
  settings.useVoc = not settings.useVoc
  settings.useOrder = false
  if not settings.useVoc and not settings.useLevel then
    settings.useOrder = true
  end
  updateCheckboxes()
end

comboWindow.btnLevel.onClick = function()
  if settings.useLevel then
    if not settings.levelDesc then
      settings.levelDesc = true
    else
      settings.useLevel = false
      settings.levelDesc = false
      if not settings.useVoc then settings.useOrder = true end
    end
  else
    settings.useLevel = true
    settings.levelDesc = false
    settings.useOrder = false
  end
  updateCheckboxes()
end

updateCheckboxes()

-- Voc Setup Logic
local vocs = {"EK", "ED", "MS", "RP"}
for _, v in ipairs(vocs) do
  local item = vocWindow["voc" .. v]
  if not settings.voc[v] then settings.voc[v] = { enabled = true, prio = 1 } end
  
  item.check:setText(v)
  item.check:setOn(settings.voc[v].enabled)
  item.check.onClick = function(w)
    settings.voc[v].enabled = not settings.voc[v].enabled
    w:setOn(settings.voc[v].enabled)
  end
  item.priority:setText(tostring(settings.voc[v].prio))
  item.priority.onTextChange = function(w, text)
    local num = tonumber(text)
    if num then settings.voc[v].prio = num end
  end
end

-- Attack Hotkey Hook

macro(200, function(m)
  
  if not settings.enabled then return end
  if g_game.isAttacking() then return end
  
  local getVoc = function(c)
    local txt = c:getText()
    if not txt or txt == "" then return nil end
    local txtUpper = txt:upper()
    if txtUpper:find("EK") then return "EK"
    elseif txtUpper:find("ED") then return "ED"
    elseif txtUpper:find("MS") then return "MS"
    elseif txtUpper:find("RP") then return "RP"
    end
    return nil
  end
  
  local getLevel = function(c)
    local txt = c:getText()
    if not txt then return 0 end
    local num = string.match(txt, "%d+")
    return tonumber(num) or 0
  end
  
  local enemies = {}
  local manualEnemyFound = {}
  for _, enemyName in ipairs(settings.enemyList) do
    local enemy = getCreatureByName(enemyName)
    if enemy then
      local enemyT = g_map.getTile(enemy:getPosition())
      if enemyT and enemyT:canShoot() then
        local v = getVoc(enemy)
        if not v or (settings.voc[v] and settings.voc[v].enabled) then
          table.insert(enemies, enemy)
          manualEnemyFound[enemy:getName()] = true
        end
      end
    end
  end
  
  if settings.enemyGuild then
    for _, spec in ipairs(getSpectators(false)) do
      if spec:isPlayer() and spec ~= player then
        if spec:getEmblem() == 2 then 
          if not manualEnemyFound[spec:getName()] then
            local specT = g_map.getTile(spec:getPosition())
            if specT and specT:canShoot() then
              local v = getVoc(spec)
              if not v or (settings.voc[v] and settings.voc[v].enabled) then
                table.insert(enemies, spec)
                print("Enemy found: " .. spec:getName())
              end
            end
          end
        end
      end
    end
  end
  
  if #enemies == 0 then return end
  
  -- Sorting Logic
  if settings.useOrder then
    -- Order in List
    table.sort(enemies, function(a, b)
      local maxIdx = #settings.enemyList + 1
      local idxA = table.find(settings.enemyList, a:getName(), true) or maxIdx
      local idxB = table.find(settings.enemyList, b:getName(), true) or maxIdx
      if idxA == idxB then
        return getDistanceBetween(a:getPosition(), pos()) < getDistanceBetween(b:getPosition(), pos())
      end
      return idxA < idxB
    end)
  else    
    table.sort(enemies, function(a, b)
      if settings.useVoc then
        local vA = getVoc(a)
        local vB = getVoc(b)
        if vA and vB then
          local prioA = settings.voc[vA].prio
          local prioB = settings.voc[vB].prio
          if prioA ~= prioB then
            return prioA < prioB
          end
        end
      end
      
      if settings.useLevel then
        local lA = getLevel(a)
        local lB = getLevel(b)
        if lA ~= lB then
          if settings.levelDesc then
            return lA > lB
          else
            return lA < lB
          end
        end
      end
      
      return getDistanceBetween(a:getPosition(), pos()) < getDistanceBetween(b:getPosition(), pos())
    end)
  end
  
  local target = enemies[1]
  if target then
    g_game.attack(target)
  end
  
end)
-- using comboWindow as parent for the hotkey so that it behaves standardly if VBot attempts to attach it somewhere or requires a parent

-- BotServer Listeners
BotServer.listen("ComboMember", function(name)
  local isNew = (connectedMembers[name] == nil)
  connectedMembers[name] = now
  if isNew then
    refreshLists()
  end
end)

local targetId = nil
local targetName = nil
BotServer.listen("LeaderTarget", function(sender, newTarget)
  if not settings.enabled then return end
  if not newTarget then
    if g_game.isAttacking() then
      g_game.attack()
    end
    targetId = nil
    targetName = nil
  else
    -- Aceita tanto formato antigo (só ID) quanto novo (objeto {id, name})
    if type(newTarget) == "table" then
      targetId = newTarget.id
      targetName = newTarget.name
    elseif type(newTarget) == "number" then
      targetId = newTarget
      targetName = nil
    elseif type(newTarget) == "string" then
      -- Vindo do ElfBot via Bridge (só nome)
      targetId = nil
      targetName = newTarget
    end
  end
end)

macro(200, function(m)
  -- Tenta por ID primeiro, depois por nome (compatibilidade ElfBot)
  local target = nil
  if targetId then
    target = getCreatureById(targetId)
  end
  if not target and targetName then
    target = getCreatureByName(targetName)
  end

  if target then
    local currentTarget = g_game.getAttackingCreature()
    if not currentTarget or currentTarget ~= target then
      local friendList = storage.playerList and storage.playerList.friendList or {}
      if not table.find(friendList, target:getName(), true) then
        g_game.attack(target)
      end
    end
  end
end)

BotServer.listen("SyncEnemyList", function(sender, data)
  if not data or type(data) ~= "table" then return end
  
  if data.leaderList then settings.leaderList = data.leaderList end
  if data.enemyList then settings.enemyList = data.enemyList end
  if data.useOrder ~= nil then settings.useOrder = data.useOrder end
  if data.useVoc ~= nil then settings.useVoc = data.useVoc end
  if data.useLevel ~= nil then settings.useLevel = data.useLevel end
  if data.levelDesc ~= nil then settings.levelDesc = data.levelDesc end
  if data.voc then settings.voc = data.voc end
  refreshLists()
  updateCheckboxes()
  -- Update Voc Window UI
  local vocs = {"EK", "ED", "MS", "RP"}
  for _, v in ipairs(vocs) do
    local item = vocWindow["voc" .. v]
    if settings.voc[v] then
      item.check:setOn(settings.voc[v].enabled)
      item.priority:setText(tostring(settings.voc[v].prio))
    end
  end
end)

-- Periodic Member Register
macro(1000, function()
  if settings.enabled then
    BotServer.send("ComboMember", player:getName())
  end
  -- Cleanup stale members
  local changed = false
  for name, timestamp in pairs(connectedMembers) do
    if now - timestamp >= 10000 then
      connectedMembers[name] = nil
      changed = true
    end
  end
  if changed then refreshLists() end
end)

local nextSendAttack = 0
onAttackingCreatureChange(function(creature, oldCreature)
  if not settings.enabled then return end
  
  
  -- BotServer Target Sync (if leader)
  -- Envia ID + Nome para compatibilidade com ElfBot via Bridge
  if table.contains(settings.leaderList, player:getName(), true) then
    if creature then
      print("sending target", creature:getId(), creature:getName())
      BotServer.send("LeaderTarget", { id = creature:getId(), name = creature:getName() })
    else
      BotServer.send("LeaderTarget", nil)
    end
  end
end)
end

if true then
-- MapPlayers.lua
modules.mapPlayers = modules.mapPlayers or {}
local mapPlayers = modules.mapPlayers
local m_mapInfo = macro(1000, "Map Info", function(m) end)

BotServer.listen("MapInfo", function(sender, data)
  if m_mapInfo.isOff() then return end
  
  local name = data.name
  local position = data.position
  local outfit = data.outfit

  if not name or not position or not outfit then return end

  local minimapWidget = modules.game_minimap.minimapWidget
  if not minimapWidget then return end

  -- A cada nova atualização da informação a widget deve ser deletada
  if mapPlayers[name] then
    if mapPlayers[name].widget then
      mapPlayers[name].widget:destroy()
    end
  end

  -- E criada novamente para poder atualizar a posição do player no mapa
  local widget = g_ui.createWidget('UICreature')
  
  -- Tamanho fixo de 80x80
  widget:setSize({width = 60, height = 60})
  widget:setPhantom(true)
  widget:setFocusable(false)
  minimapWidget:insertChild(1, widget)

  -- Identifica o andar atual do mapa para forçar a widget a aparecer (ignorando o position.z real)
  local cameraPosZ = minimapWidget:getCameraPosition().z
  local renderPosition = {x = position.x, y = position.y, z = cameraPosZ}
  
  widget.pos = renderPosition -- Ancorado no andar visivel no mapa
  widget:setOutfit(outfit)
  widget:setTooltip(name)
  minimapWidget:centerInPosition(widget, renderPosition)

  -- Calcula a diferença de altura entre a câmera e o player real
  local diffZ = cameraPosZ - position.z
  if diffZ > 0 then
     diffZ = "+" .. diffZ
  end
  local textToShow = name .. " (" .. diffZ .. ")"

  -- Texto com o nome do personagem acima da creature
  local nameLabel = g_ui.createWidget('UILabel', widget)
  nameLabel:setText(textToShow)
  nameLabel:setColor('#00FF00') -- Verde puro
  nameLabel:setFont('verdana-11px-rounded') -- Fonte padrão legível com borda preta
  nameLabel:setTextAutoResize(true)
  nameLabel:addAnchor(6, 'parent', 6)
  nameLabel:addAnchor(2, 'parent', 1)

  -- Salva os dados do jogador com atributos extra para atualizar vivo
  mapPlayers[name] = { 
    widget = widget, 
    label = nameLabel,
    name = name,
    positionX = position.x,
    positionY = position.y,
    positionZ = position.z,
    lastUpdate = now 
  }
end)

macro(100, function()
  if m_mapInfo.isOff() then return end
  
  local minimapWidget = modules.game_minimap.minimapWidget
  if not minimapWidget then return end
  
  local cameraPos = minimapWidget:getCameraPosition()
  if not cameraPos then return end
  local cameraPosZ = cameraPos.z
  
  -- Checagem dinâmica de timeout e recálculo da tela
  for playerName, playerData in pairs(mapPlayers) do
    if now - playerData.lastUpdate >= 10000 then
      if playerData.widget then
        playerData.widget:destroy()
      end
      mapPlayers[playerName] = nil
    else
      -- Se a câmera mudou de Z através do minimapa, ancoramos de novo sem piscar!
      if playerData.widget and playerData.widget.pos and playerData.widget.pos.z ~= cameraPosZ then
        local renderPos = {x = playerData.positionX, y = playerData.positionY, z = cameraPosZ}
        playerData.widget.pos = renderPos
        minimapWidget:centerInPosition(playerData.widget, renderPos)
      end
      
      -- Atualiza dinamicamente o texto com a distância Z (estamos um andar acima = -1)
      if playerData.label then
         local diffZ = cameraPosZ - playerData.positionZ
         if diffZ > 0 then
            diffZ = "+" .. diffZ
         end
         playerData.label:setText(playerData.name .. " (" .. diffZ .. ")")
      end
    end
  end
end)

macro(1000, function(m)
  if m_mapInfo.isOff() then return end
  
  if BotServer._websocket then
    BotServer.send("MapInfo", {
      name = player:getName(),
      position = pos(),
      outfit = player:getOutfit()
    })  
  end
end)

hotkey("Ctrl+M", function()
  modules.game_minimap.toggleFullMap()
end)
end

if true then
-- NavPotion.lua

--[[
===================================================
NavPotion - Potion Friends via Navigation
===================================================
]]--

-------------------------------------------------
-- 1. STORAGE — defaults & migration
-------------------------------------------------
local panelName = "NavPotion"

if not storage[panelName] then
    storage[panelName] = {
        enabled       = false,
        potDistance   = 5,
        
        -- Player Config
        mpRequestEnabled = false,
        mpRequestPercent = 50,
        
        -- HP thresholds (0–100)
        hpEK = 80, hpED = 80, hpMS = 80, hpRP = 80,
        
        -- HP flags (boolean)
        hpEnabledEK = true, hpEnabledED = true,
        hpEnabledMS = true, hpEnabledRP = true,
        
        -- MP flags (boolean)
        mpEnabledEK = true, mpEnabledED = true,
        mpEnabledMS = true, mpEnabledRP = true,
        
        -- Potion item ids
        hpItemEK = 266, hpItemED = 266, hpItemMS = 266, hpItemRP = 266,
        mpItemEK = 268, mpItemED = 268, mpItemMS = 268, mpItemRP = 268,
    }
end

local function ensureField(key, default)
    if storage[panelName][key] == nil then
        storage[panelName][key] = default
    end
end

ensureField("potDistance", 5)
ensureField("mpRequestEnabled", false)
ensureField("mpRequestPercent", 50)

ensureField("hpEK", 80) ensureField("hpED", 80)
ensureField("hpMS", 80) ensureField("hpRP", 80)

ensureField("hpEnabledEK", true) ensureField("hpEnabledED", true)
ensureField("hpEnabledMS", true) ensureField("hpEnabledRP", true)

ensureField("mpEnabledEK", true) ensureField("mpEnabledED", true)
ensureField("mpEnabledMS", true) ensureField("mpEnabledRP", true)

ensureField("hpItemEK", 0) ensureField("hpItemED", 0)
ensureField("hpItemMS", 0) ensureField("hpItemRP", 0)

ensureField("mpItemEK", 0) ensureField("mpItemED", 0)
ensureField("mpItemMS", 0) ensureField("mpItemRP", 0)

local settings = storage[panelName]

-------------------------------------------------
-- 2. WIDGET DEFINITIONS
-------------------------------------------------
g_ui.loadUIFromString([[
NavPotionScrollBar < Panel
  height: 28
  margin-top: 3

  UIWidget
    id: text
    anchors.left: parent.left
    anchors.right: parent.right
    anchors.top: parent.top
    text-align: center

  HorizontalScrollBar
    id: scroll
    anchors.left: parent.left
    anchors.right: parent.right
    anchors.top: prev.bottom
    margin-top: 3
    minimum: 0
    maximum: 100
    step: 1

NavPotionItem < Panel
  height: 34
  margin-top: 7
  margin-left: 25
  margin-right: 25

  UIWidget
    id: text
    anchors.left: parent.left
    anchors.verticalCenter: next.verticalCenter

  BotItem
    id: item
    anchors.top: parent.top
    anchors.right: parent.right

NavPotionCheckBox < BotSwitch
  height: 20
  margin-top: 5

NavPotionRadioBox < Panel
  height: 20
  margin-top: 5
  layout:
    type: horizontalBox
    spacing: 5
    align-content: center

NavPotionBox < Panel
  padding: 8
  padding-top: 22
  margin-top: 8
  margin-bottom: 8  
  image-border: 1
  layout:
    type: verticalBox
    fit-children: true

NavPotionWindow < MainWindow
  text: Configuracao do NavPotion
  size: 520 700
  @onEscape: self:hide()

  Panel
    id: content
    anchors.top: parent.top
    anchors.left: parent.left
    anchors.right: parent.right
    anchors.bottom: closeButton.top
    margin-bottom: 10

    Panel
      id: topConfig
      anchors.top: parent.top
      anchors.left: parent.left
      anchors.right: parent.right
      layout:
        type: verticalBox
        fit-children: true

    Panel
      id: left
      anchors.top: topConfig.bottom
      anchors.left: parent.left
      anchors.right: parent.horizontalCenter
      margin-top: 5
      margin-left: 10
      margin-right: 10
      layout:
        type: verticalBox
        fit-children: true

    Panel
      id: right
      anchors.top: topConfig.bottom
      anchors.left: parent.horizontalCenter
      anchors.right: parent.right
      margin-top: 5
      margin-left: 10
      margin-right: 10
      layout:
        type: verticalBox
        fit-children: true

    VerticalSeparator
      anchors.top: left.top
      anchors.bottom: parent.bottom
      anchors.left: parent.horizontalCenter
      margin-top: 5
      margin-bottom: 5
    
  Button
    id: closeButton
    text: Fechar
    font: cipsoftFont
    anchors.right: parent.right
    anchors.bottom: parent.bottom
    size: 45 21
    margin-right: 5
]])

-------------------------------------------------
-- 3. INLINE PANEL (bot tab) & WINDOW SETUP
-------------------------------------------------
local navPotionUI = setupUI([[
Panel
  height: 19

  BotSwitch
    id: status
    anchors.top: parent.top
    anchors.left: parent.left
    text-align: center
    width: 130
    height: 18
    text: NavPotion

  Button
    id: btnSetup
    anchors.top: prev.top
    anchors.left: prev.right
    anchors.right: parent.right
    margin-left: 3
    height: 17
    text: Setup
]], parent)

rootWidget = g_ui.getRootWidget()

local tcSwitch = navPotionUI.status
local npWindow = UI.createWindow('NavPotionWindow', rootWidget)
npWindow:hide()

npWindow.closeButton.onClick = function() npWindow:hide() end
navPotionUI.btnSetup.onClick = function()
    npWindow:show()
    npWindow:raise()
    npWindow:focus()
end

tcSwitch:setOn(settings.enabled)
tcSwitch.onClick = function(widget)
    settings.enabled = not settings.enabled
    widget:setOn(settings.enabled)
end

local topPanel   = npWindow.content.topConfig
local leftPanel  = npWindow.content.left
local rightPanel = npWindow.content.right

-------------------------------------------------
-- Helper: add UI components
-------------------------------------------------
local function addCheckBox(id, title, defaultValue, dest, tooltip)
    local widget = UI.createWidget('NavPotionCheckBox', dest)
    widget.onClick = function()
        widget:setOn(not widget:isOn())
        settings[id] = widget:isOn()
    end
    widget:setText(title)
    if tooltip then widget:setTooltip(tooltip) end
    if settings[id] == nil then widget:setOn(defaultValue) else widget:setOn(settings[id]) end
    settings[id] = widget:isOn()
    return widget
end

local function addItem(id, title, defaultItem, dest, tooltip)
    local widget = UI.createWidget('NavPotionItem', dest)
    widget.text:setText(title)
    if tooltip then
        widget.text:setTooltip(tooltip)
        widget.item:setTooltip(tooltip)
    end
    widget.item:setItemId(settings[id] or defaultItem)
    widget.item.onItemChange = function(w) settings[id] = w:getItemId() end
    settings[id] = settings[id] or defaultItem
    return widget
end

local function addScrollBar(id, title, min, max, defaultValue, dest, tooltip)
    local widget = UI.createWidget('NavPotionScrollBar', dest)
    if tooltip then widget.text:setTooltip(tooltip) end
    widget.scroll.onValueChange = function(scroll, value)
        widget.text:setText(title .. ": " .. value .. (max > 10 and "%" or " SQMs"))
        settings[id] = value
    end
    widget.scroll:setRange(min, max)
    if tooltip then widget.scroll:setTooltip(tooltip) end
    widget.scroll:setValue(settings[id] or defaultValue)
    widget.scroll.onValueChange(widget.scroll, widget.scroll:getValue())
    return widget
end

local function addLabel(text, dest)
    local lbl = g_ui.createWidget('Label', dest)
    lbl:setText(text)
    lbl:setTextAlign(AlignCenter)
    lbl:setMarginTop(8)
    lbl:setMarginBottom(4)
    return lbl
end

local function addSeparator(dest)
    local sep = g_ui.createWidget('HorizontalSeparator', dest)
    sep:setMarginTop(6)
    sep:setMarginBottom(6)
    return sep
end

local function createBox(title, dest)
    local box = UI.createWidget('NavPotionBox', dest)
    local titleLabel = g_ui.createWidget('Label', box)
    titleLabel:setText(title)
    titleLabel:setTextAlign(AlignCenter)
    titleLabel:setMarginTop(-20)
    titleLabel:setMarginBottom(8)
    return box
end


-------------------------------------------------
-- TOP PANEL — General Settings
-------------------------------------------------
local generalBox = createBox("Configuracoes Gerais", topPanel)

addLabel("Minha Vocacao:", generalBox)
local myVocPanel = UI.createWidget('NavPotionRadioBox', generalBox)
local myVocs = {"EK", "ED", "MS", "RP"}
local radioWidgets = {}

if not settings.myVoc then settings.myVoc = "EK" end

for _, v in ipairs(myVocs) do
    local btn = UI.createWidget('NavPotionCheckBox', myVocPanel)
    btn:setText(v)
    btn:setWidth(60)
    btn:setMarginTop(0)
    btn.onClick = function()
        for _, w in ipairs(radioWidgets) do w:setOn(false) end
        btn:setOn(true)
        settings.myVoc = v
    end
    btn:setOn(settings.myVoc == v)
    table.insert(radioWidgets, btn)
end

addScrollBar("potDistance", "Distancia Maxima P/ Potar", 1, 10, 5, generalBox, "Distancia maxima para potar um aliado na tela"):setMarginTop(8)
addScrollBar("mpRequestPercent", "Pedir Mana se tiver < ", 0, 100, 50, generalBox, "Pede mana quando ficar com menos que essa porcentagem"):setMarginTop(8)
addCheckBox("mpRequestEnabled", "Pedir Mana (Meu Personagem)", false, generalBox, "Ative para o seu personagem pedir mana aos aliados via BotServer"):setMarginTop(8)

-------------------------------------------------
-- LEFT & RIGHT PANELS — Vocations
-------------------------------------------------
local function buildVocBox(voc, destPanel)
    local vocBox = createBox(voc, destPanel)
    
    addScrollBar("hp" .. voc, "HP " .. voc, 0, 100, 80, vocBox, "Usa se a vida for menor que X%")
    addItem("hpItem" .. voc, "Pocao de HP", 0, vocBox, "Pocao de HP para " .. voc)
    addItem("mpItem" .. voc, "Pocao de MP", 0, vocBox, "Pocao de MP para " .. voc)
    addCheckBox("hpEnabled" .. voc, "Ativar HP", true, vocBox, "Habilita HP para " .. voc)
    addCheckBox("mpEnabled" .. voc, "Responder pedido de MP", true, vocBox, "Habilita enviar pocao de MP para " .. voc)
    
    
    
end

-- EK e ED do lado esquerdo
buildVocBox("EK", leftPanel)
buildVocBox("ED", leftPanel)

-- MS e RP do lado direito
buildVocBox("MS", rightPanel)
buildVocBox("RP", rightPanel)

local potMembers = {}

local lockPotion = {}
-------------------------------------------------
-- 6. MP BOTSERVER LISTENER E PING HEARTBEAT
-------------------------------------------------
BotServer.listen("NavPotionReq", function(name, data)
    if not settings.enabled or not data then return end
    if lockPotion[name] then return end
    
    -- Atualiza e salva a vocacao do aliado sempre que ele envia um pacote
    if data.voc then
        potMembers[name] = data.voc
    end
    
    -- Ignora se nao for pedido de MP
    if data.type ~= "MP" then return end
    
    local spec = getPlayerByName(name)
    if not spec or spec == player then return end
    
    -- Checa distancia
    local myPos = pos()
    local targetPos = spec:getPosition()
    if not myPos or not myPos.x or not targetPos or not targetPos.x then return end

    if getDistanceBetween(myPos, targetPos) > settings.potDistance then return end
    
    -- Pega a vocacao via ping em vez de ler texto
    local voc = data.voc
    if not voc then return end
    
    local mpEnabled = settings["mpEnabled" .. voc]
    local mpItemId  = settings["mpItem" .. voc]
    
    if mpEnabled and mpItemId and mpItemId > 0 then
        usewith(mpItemId, spec)
    end
end)

-- Health Ping: Manda a cada segundo para atestar nossa vocacao no Nav
macro(1000, function()
    if not settings.enabled then return end
    BotServer.send("NavPotionReq", {type = "ping", voc = settings.myVoc})
end)

-------------------------------------------------
-- 7. HP LOOP 
-------------------------------------------------
macro(1000, function()
    if not settings.enabled then return end
    
    -- HP (Checa pela tela, filtrando pela validacao do Botserver de quem e aliado)
    for _, spec in ipairs(getSpectators(false)) do
        if spec:isPlayer() and spec ~= player then
            local specName = spec:getName()
            -- apenas membros locais registrados no potMembers e que nao estao sob "lockPotion"
            if potMembers[specName] and not lockPotion[specName] then
                -- Checa distancia configuravel
                local myPos = pos()
                local targetPos = spec:getPosition()
                if myPos and myPos.x and targetPos and targetPos.x then
                    if getDistanceBetween(myPos, targetPos) <= settings.potDistance then
                        -- A Vocacao vem do cache atualizado do BotServer ping
                        local voc = potMembers[specName]
                        if voc then
                            local hpEnabled   = settings["hpEnabled" .. voc]
                            local hpThreshold = settings["hp" .. voc]
                            local hpItemId    = settings["hpItem" .. voc]
                            local hp          = spec:getHealthPercent()
                            
                            if hpEnabled and hp and hpThreshold and hp <= hpThreshold and hpItemId and hpItemId > 0 then
                                usewith(hpItemId, spec)
                                return -- respeita o cooldown de action
                            end
                        end
                    end
                end
            end
        end
    end
end)

-------------------------------------------------
-- TICK: Pedir Potion de MP
-------------------------------------------------
macro(1000, function()
    if not settings.enabled then return end
    
    -- Caso queria dar lock nas suas proprias peds quando anda, descomente abaixo
    -- if lockPotion[player:getName()] then return end
    
    if settings.mpRequestEnabled then
        if manapercent() <= settings.mpRequestPercent then
            BotServer.send("NavPotionReq", {type = "MP", voc = settings.myVoc})
        end
    end
end)

onCreaturePositionChange(function(creature, newPos, oldPos)
  if not settings.enabled then return end
  if not creature:isPlayer() or creature == player then return end
  
  local name = creature:getName()
  if not name or not potMembers[name] then return end
  local myPos = pos()
  if not myPos or not myPos.x or not newPos or not newPos.x then return end
  if getDistanceBetween(myPos, newPos) > settings.potDistance then return end

  lockPotion[name] = true
  schedule(1000, function()
    lockPotion[name] = false
  end)
end)
end
