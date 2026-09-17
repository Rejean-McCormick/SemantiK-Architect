@echo off
cd /d "%~dp0"
if "%PGF_PATH%"=="" set "PGF_PATH=%CD%\runtime\semantik_architect.pgf"
python manage.py doctor || exit /b 1
python manage.py serve --reload
