@echo off
cd /d "%~dp0"
echo Starting ASCII Face Detection...
"C:\Program Files\Go\bin\go.exe" run main.go
pause
