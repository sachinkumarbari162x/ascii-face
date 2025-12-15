@echo off
set "VCVARS=C:\Program Files\Microsoft Visual Studio\18\Enterprise\VC\Auxiliary\Build\vcvars64.bat"

if exist "%VCVARS%" (
    call "%VCVARS%"
) else (
    echo "Warning: vcvars64.bat not found at expected location. Attempting to run cl.exe directly..."
)

"C:\Program Files\Microsoft Visual Studio\18\Enterprise\VC\Tools\MSVC\14.50.35717\bin\Hostx64\x64\cl.exe" launcher.c
if %ERRORLEVEL% EQU 0 (
    echo Build Successful! Run launcher.exe to start.
) else (
    echo Build Failed.
)
pause
