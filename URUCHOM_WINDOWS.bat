@echo off
cd /d "%~dp0"
where py >nul 2>&1
if %ERRORLEVEL% EQU 0 (set "PY=py -3") else (where python >nul 2>&1 && (set "PY=python"))
if not defined PY (
 echo Python nie jest zainstalowany. Zainstaluj Python 3.11 ze strony python.org.
 pause
 exit /b 1
)
if not exist ".venv\Scripts\python.exe" (
 echo Tworze srodowisko Python...
 %PY% -m venv .venv
 if errorlevel 1 (echo Nie udalo sie utworzyc srodowiska.&pause&exit /b 1)
)
echo Sprawdzam wymagane pakiety...
 ".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (echo Instalacja bibliotek nie powiodla sie.&pause&exit /b 1)
echo.
echo OTWORZ W PRZEGLADARCE: http://127.0.0.1:8000
echo Nie zamykaj tego okna podczas analizy.
start "" "http://127.0.0.1:8000"
".venv\Scripts\python.exe" -m uvicorn server:app --host 127.0.0.1 --port 8000
pause
