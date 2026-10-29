@echo off
rem Launch File Searcher at http://localhost:8765/ (no install required)
cd /d "%~dp0"
start "" http://localhost:8765/
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0server.ps1"
