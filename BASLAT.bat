@echo off
cd /d "%~dp0"
set /p DUAL_COM=ESP32 COM portunu yazin (ornek COM5): 
python -m viewer --port "%DUAL_COM%" --baud 460800
pause
