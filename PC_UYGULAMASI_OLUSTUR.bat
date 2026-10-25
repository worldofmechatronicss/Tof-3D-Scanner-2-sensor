@echo off
setlocal
cd /d "%~dp0"
echo Dual LiDAR S3 - Windows uygulamasi olusturma
if not exist ".desktop-venv\Scripts\python.exe" (
    python -m venv .desktop-venv
    if errorlevel 1 goto :error
)
".desktop-venv\Scripts\python.exe" -m pip install -r desktop_requirements.txt
if errorlevel 1 goto :error
".desktop-venv\Scripts\python.exe" -m PyInstaller --noconfirm DualLidarS3.spec
if errorlevel 1 goto :error
echo.
echo Hazir: dist\DualLidarS3\DualLidarS3.exe
echo Bu klasorun tamamini birlikte tasiyin.
explorer "dist\DualLidarS3"
pause
exit /b 0
:error
echo Olusturma tamamlanamadi. Yukaridaki hata metnini paylasin.
pause
exit /b 1
