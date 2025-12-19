# Script PowerShell per creare e configurare ambiente virtuale Python 3.12
# Esegui con: powershell -ExecutionPolicy Bypass -File setup_venv.ps1

Write-Host "=== Setup Virtual Environment Python 3.12 ===" -ForegroundColor Cyan

# Verifica Python
$pythonCmd = $null
$pythonVersion = $null

# Prova python3.12
try {
    $pythonVersion = python3.12 --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        $pythonCmd = "python3.12"
    }
} catch {
    # Ignora
}

# Prova python (potrebbe essere 3.12)
if (-not $pythonCmd) {
    try {
        $versionOutput = python --version 2>&1
        if ($versionOutput -match "3\.12") {
            $pythonCmd = "python"
            $pythonVersion = $versionOutput
        }
    } catch {
        Write-Host "❌ Errore: Python non trovato" -ForegroundColor Red
        Write-Host "   Installa Python 3.12 da https://www.python.org/downloads/" -ForegroundColor Yellow
        exit 1
    }
}

if (-not $pythonCmd) {
    Write-Host "❌ Errore: Python 3.12 non trovato" -ForegroundColor Red
    Write-Host "   Versione trovata: $pythonVersion" -ForegroundColor Yellow
    Write-Host "   Installa Python 3.12 da https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Python trovato: $pythonVersion" -ForegroundColor Green

# Crea venv
$venvDir = "venv"
if (Test-Path $venvDir) {
    Write-Host "⚠️  Virtual environment già esistente in $venvDir" -ForegroundColor Yellow
    $recreate = Read-Host "Vuoi ricrearlo? (y/N)"
    if ($recreate -eq "y" -or $recreate -eq "Y") {
        Write-Host "🗑️  Rimozione venv esistente..." -ForegroundColor Yellow
        Remove-Item -Recurse -Force $venvDir
    } else {
        Write-Host "✅ Usando venv esistente" -ForegroundColor Green
        & "$venvDir\Scripts\Activate.ps1"
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        Write-Host "✅ Setup completato!" -ForegroundColor Green
        exit 0
    }
}

# Crea nuovo venv
Write-Host "📦 Creazione virtual environment..." -ForegroundColor Cyan
& $pythonCmd -m venv $venvDir

if (-not (Test-Path "$venvDir\Scripts\Activate.ps1")) {
    Write-Host "❌ Errore nella creazione del venv" -ForegroundColor Red
    exit 1
}

# Attiva venv
Write-Host "🔌 Attivazione virtual environment..." -ForegroundColor Cyan
& "$venvDir\Scripts\Activate.ps1"

# Aggiorna pip
Write-Host "⬆️  Aggiornamento pip..." -ForegroundColor Cyan
python -m pip install --upgrade pip

# Installa dipendenze
Write-Host "📥 Installazione dipendenze..." -ForegroundColor Cyan
pip install -r requirements.txt

Write-Host ""
Write-Host "✅ Virtual environment configurato con successo!" -ForegroundColor Green
Write-Host ""
Write-Host "Per attivare il venv:" -ForegroundColor Cyan
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "  oppure" -ForegroundColor Gray
Write-Host "  venv\Scripts\activate.bat" -ForegroundColor White
Write-Host ""
Write-Host "Per disattivare:" -ForegroundColor Cyan
Write-Host "  deactivate" -ForegroundColor White
Write-Host ""

