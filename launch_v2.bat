@echo off
setlocal EnableDelayedExpansion

REM ANSI Colors
for /F %%a in ('echo prompt $E^| cmd') do set "ESC=%%a"
set "RED=%ESC%[31m"
set "GREEN=%ESC%[32m"
set "YELLOW=%ESC%[33m"
set "BLUE=%ESC%[34m"
set "MAGENTA=%ESC%[35m"
set "CYAN=%ESC%[36m"
set "WHITE=%ESC%[37m"
set "RESET=%ESC%[0m"
set "BOLD=%ESC%[1m"

cls
echo.
echo %CYAN%
echo  ================================================================================
echo        %BOLD%PODCAST AGENT v2 // QUANTUM INTERFACE LOADED%RESET%%CYAN%
echo  ================================================================================
echo %MAGENTA%
echo      / \   _ __ ^| ^|_(_) __ _ _ __ __ ___   __(_) ^|_ _   _
echo     / _ \ ^| '_ \^| __^| ^|/ _` ^| '__/ _` \ \ / /^| ^| __^| ^| ^| ^|
echo    / ___ \^| ^| ^| ^| ^|_^| ^| (_^| ^| ^| ^| (_^| ^|\ V / ^| ^| ^|_^| ^|_^| ^|
echo   /_/   \_\_^| ^|_^|\__^|_^|\__, ^|_^|  \__,_^| \_/  ^|_^|\__^|\__, ^|
echo                        ^|___/                        ^|___/
echo %CYAN%
echo  --------------------------------------------------------------------------------
echo   %WHITE%[SYSTEM]  Architecture: %GREEN%Neural-Symbolic Hybrid%WHITE%
echo   %WHITE%[STATUS]  Core Systems: %GREEN%ONLINE%WHITE%
echo   %WHITE%[VISUAL]  Terminal logs:%GREEN% ENABLED%WHITE%
echo   %WHITE%[AUDIO]   Suno Bark TTS:%GREEN% MOUNTED%WHITE%
echo  --------------------------------------------------------------------------------
echo %RESET%

REM --- PATH HANDLING ---
REM Store the script directory
set "SCRIPT_DIR=%~dp0"
REM Navigate to root directory (check if .venv is in current dir or parent)
if exist "%SCRIPT_DIR%.venv\Scripts\activate.bat" (
    pushd "%SCRIPT_DIR%"
) else (
    pushd "%SCRIPT_DIR%.."
)

echo %YELLOW%[INIT] Initializing Neural Environment...%RESET%

if not exist ".venv\Scripts\activate.bat" (
    echo %RED%[CRITICAL] Virtual environment containment breach (not found).%RESET%
    echo %RED%[ACTION]   Run original launch.bat to re-stabilize core.%RESET%
    popd
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo %RED%[ERROR] Failed to activate environment.%RESET%
    popd
    pause
    exit /b 1
)

echo %GREEN%[SUCCESS] Environment Stabilized.%RESET%
echo.

if "%~1"=="" (
    echo %YELLOW%[INPUT REQUIRED] Please supply PDF Intelligence Source.%RESET%
    echo.
    echo %WHITE%Usage:   launch_v2.bat "C:\path\to\dossier.pdf"%RESET%
    echo.
    popd
    pause
    exit /b 1
)

echo %BLUE%[PROCESS] Injecting Payload: %WHITE%"%~1"%RESET%
echo %BLUE%[PROCESS] Engaging Main Orchestrator...%RESET%
echo.

python podcast_agent_v2\main.py "%~1" %2 %3 %4

echo.
echo %CYAN%================================================================================%RESET%
echo %GREEN%   MISSION COMPLETE. SYSTEM STANDBY.%RESET%
echo %CYAN%================================================================================%RESET%

popd
pause
