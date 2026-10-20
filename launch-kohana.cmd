@echo off
setlocal
set "HERMES_ROOT=%~dp0.."
cd /d "%~dp0.kohana\workspace"
"%HERMES_ROOT%\hermes-agent\venv\Scripts\hermes.exe" -p kohana-v3_1 chat --cli
endlocal
