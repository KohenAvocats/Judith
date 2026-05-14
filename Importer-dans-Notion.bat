@echo off
REM Wrapper Windows pour lancer l'import Notion en double-clic.
REM Cabinet Kohen Avocats.

cd /d "%~dp0"

REM Verifie Python 3
where python >nul 2>&1
if errorlevel 1 (
  echo Python 3 n'est pas installe.
  echo.
  echo Installez-le depuis https://www.python.org/downloads/
  echo IMPORTANT : cochez "Add Python to PATH" pendant l'installation.
  echo.
  start "" "https://www.python.org/downloads/"
  pause
  exit /b 1
)

REM Cree un venv local si pas deja la
if not exist ".venv" (
  echo Premiere utilisation : preparation de l'environnement Python...
  python -m venv .venv
)

REM Active venv
call .venv\Scripts\activate.bat

REM Lance le script
python import.py

echo.
echo ============================================================
pause
