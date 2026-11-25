@echo off
setlocal
where py.exe >nul 2>nul
if errorlevel 1 goto NoLauncher
py -3 "%~dp0tools\build_windows.py" %*
exit /b %errorlevel%
:NoLauncher
where python.exe >nul 2>nul
if errorlevel 1 goto NeedsPython
python "%~dp0tools\build_windows.py" %*
exit /b %errorlevel%
:NeedsPython
echo Building from source needs Python 3.9+. To use the app, run the ready-made x64 installer instead.
exit /b 1
