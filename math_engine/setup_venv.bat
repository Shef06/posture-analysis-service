@echo off
REM Script per creare e configurare ambiente virtuale Python 3.12 (Windows)
REM Esegui questo file nella directory math_engine

echo === Setup Virtual Environment Python 3.12 ===

REM Verifica che siamo nella directory corretta
if not exist "requirements.txt" (
    echo Errore: requirements.txt non trovato
    echo Assicurati di eseguire questo script dalla directory math_engine
    echo Percorso attuale: %CD%
    pause
    exit /b 1
)

REM Verifica Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Errore: Python non trovato
    echo Installa Python 3.12 da https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Python trovato: %PYTHON_VERSION%

REM Verifica che sia 3.12 (o almeno 3.x)
echo %PYTHON_VERSION% | findstr /R "^3\." >nul
if errorlevel 1 (
    echo Avviso: Python 3.12 consigliato, trovato %PYTHON_VERSION%
    echo Continuo comunque...
)

echo Python verificato

REM Crea venv
set VENV_DIR=venv
if exist "%VENV_DIR%" (
    echo Virtual environment già esistente in %VENV_DIR%
    set /p RECREATE="Vuoi ricrearlo? (y/N): "
    if /i "%RECREATE%"=="y" (
        echo Rimozione venv esistente...
        rmdir /s /q "%VENV_DIR%"
    ) else (
        echo Usando venv esistente
        call "%VENV_DIR%\Scripts\activate.bat"
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        echo Setup completato!
        exit /b 0
    )
)

REM Crea nuovo venv
echo Creazione virtual environment...
python -m venv "%VENV_DIR%"

REM Attiva venv
echo Attivazione virtual environment...
call "%VENV_DIR%\Scripts\activate.bat"

REM Aggiorna pip
echo Aggiornamento pip...
python -m pip install --upgrade pip

REM Installa dipendenze
echo Installazione dipendenze...
pip install -r requirements.txt

echo.
echo Virtual environment configurato con successo!
echo.
echo Per attivare il venv:
echo   venv\Scripts\activate.bat
echo.
echo Per disattivare:
echo   deactivate
echo.

pause

