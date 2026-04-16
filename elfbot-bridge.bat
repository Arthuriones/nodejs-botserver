@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1
title ElfBot Bridge

REM ============================================================
REM  CONFIGURACAO DO TIME (mesmo IP do BotServer, mesmo canal)
REM ============================================================
set "SERVER=http://37.148.133.154:8080"
set "CHANNEL=1"
REM ============================================================

where curl >nul 2>&1
if errorlevel 1 (
    echo [ERRO] curl nao encontrado. Precisa de Windows 10+.
    pause
    exit /b
)

cls
echo.
echo   =============================================
echo        ElfBot Bridge v1.0 - Combo Sync
echo   =============================================
echo.

if exist "bridge-name.txt" (
    set /p "NAME="<bridge-name.txt
    for /f "tokens=*" %%a in ("!NAME!") do set "NAME=%%a"
    echo   Jogador: !NAME!
) else (
    set /p "NAME=  Nome do personagem: "
    for /f "tokens=*" %%a in ("!NAME!") do set "NAME=%%a"
)

>bridge-name.txt echo !NAME!

if not exist "bridge-leaders.txt" (
    echo. > bridge-leaders.txt
    echo.
    echo   [!] Arquivo bridge-leaders.txt criado.
    echo       Adicione os nomes dos lideres que voce quer seguir,
    echo       um por linha. Pode editar a qualquer momento.
)

echo.
echo   Servidor: %SERVER%
echo   Canal: %CHANNEL%
echo.
echo   ----------- HOTKEYS DO ELFBOT -----------
echo.
echo   SEGUIDOR (recebe alvo do lider):
echo     Hotkey: Always / 500ms / Sem condicao
echo     Action: attack $fileline.'bridge_target_in.txt'.1
echo.
echo   LIDER (envia alvo pro time):
echo     Hotkey: Always / 500ms / Condition: istargeting
echo     Action: filewrite bridge_target_out.txt $target.name
echo.
echo   ------------------------------------------
echo.
echo   [Bridge] Iniciando...
echo.

set "LAST_TARGET="
set "LAST_RECV="
set "LAST_MEMBERS="
set "TICK=0"

:loop
REM === Ler lideres do bridge-leaders.txt ===
set "LEADERS="
if exist "bridge-leaders.txt" (
    for /f "usebackq tokens=* delims=" %%a in ("bridge-leaders.txt") do (
        set "LINE=%%a"
        for /f "tokens=*" %%b in ("!LINE!") do set "LINE=%%b"
        if defined LINE (
            if defined LEADERS (
                set "LEADERS=!LEADERS!,!LINE!"
            ) else (
                set "LEADERS=!LINE!"
            )
        )
    )
)

REM === Buscar conectados a cada 5 segundos ===
set /a "MOD=!TICK! %% 5"
if !MOD! equ 0 (
    curl -s -G "%SERVER%/api/bridge/members" --data-urlencode "channel=%CHANNEL%" >bridge-members.txt 2>nul
    set "MEMBERS="
    if exist "bridge-members.txt" (
        for /f "usebackq tokens=* delims=" %%a in ("bridge-members.txt") do (
            if defined MEMBERS (set "MEMBERS=!MEMBERS!, %%a") else (set "MEMBERS=%%a")
        )
    )
    if not "!MEMBERS!"=="!LAST_MEMBERS!" (
        if defined MEMBERS (
            echo   [!time:~0,8!] Conectados: !MEMBERS!
        ) else (
            echo   [!time:~0,8!] Nenhum jogador conectado
        )
        set "LAST_MEMBERS=!MEMBERS!"
    )
)

REM === Buscar alvo dos lideres selecionados ===
if defined LEADERS (
    curl -s -G "%SERVER%/api/bridge/target" --data-urlencode "channel=%CHANNEL%" --data-urlencode "leaders=!LEADERS!" >bridge_target_in.txt 2>nul

    set "RECV_TARGET="
    set /p "RECV_TARGET="<bridge_target_in.txt 2>nul
    if defined RECV_TARGET (
        if not "!RECV_TARGET!"=="!LAST_RECV!" (
            echo   [!time:~0,8!] Alvo do lider: !RECV_TARGET!
            set "LAST_RECV=!RECV_TARGET!"
        )
    ) else (
        if defined LAST_RECV (
            echo   [!time:~0,8!] Lider parou de atacar
            set "LAST_RECV="
        )
    )
) else (
    if !MOD! equ 0 (
        echo   [!time:~0,8!] Nenhum lider em bridge-leaders.txt
    )
)

REM === Heartbeat ===
curl -s -X POST "%SERVER%/api/bridge/heartbeat" -H "Content-Type: application/json" -d "{\"name\":\"!NAME!\",\"channel\":\"%CHANNEL%\"}" >nul 2>&1

REM === Se for lider, envia alvo ===
if exist "bridge_target_out.txt" (
    set "CURRENT_TARGET="
    set /p "CURRENT_TARGET="<bridge_target_out.txt 2>nul
    if defined CURRENT_TARGET (
        if not "!CURRENT_TARGET!"=="!LAST_TARGET!" (
            echo   [!time:~0,8!] Enviando alvo: !CURRENT_TARGET!
            curl -s -X POST "%SERVER%/api/bridge/target" -H "Content-Type: application/json" -d "{\"name\":\"!NAME!\",\"channel\":\"%CHANNEL%\",\"target\":\"!CURRENT_TARGET!\"}" >nul 2>&1
            set "LAST_TARGET=!CURRENT_TARGET!"
        )
    )
)

set /a "TICK=!TICK!+1"
timeout /t 1 /nobreak >nul
goto loop
