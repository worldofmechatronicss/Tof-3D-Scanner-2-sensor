@echo off
cd /d "%~dp0"
if not exist ".desktop-venv\Scripts\pythonw.exe" (
  echo Once PC_UYGULAMASI_OLUSTUR.bat dosyasini calistirin.
  pause
  exit /b 1
)
start "" ".desktop-venv\Scripts\pythonw.exe" desktop.py
