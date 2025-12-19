# Setup Windows - Guida Completa

Guida dettagliata per configurare il microservizio su Windows.

## Prerequisiti

1. **Python 3.12** installato
   - Scarica da: https://www.python.org/downloads/
   - Durante l'installazione, seleziona "Add Python to PATH"

2. **Verifica installazione:**
   ```powershell
   python --version
   # Output atteso: Python 3.12.x
   ```

## Setup Step-by-Step

### 1. Apri PowerShell

Apri PowerShell nella directory del progetto:
```powershell
cd "C:\Users\shafa\OneDrive\Desktop\Code\JOB\posture-analysis-service\math_engine"
```

### 2. Verifica che la directory esista

```powershell
Get-Location
# Dovresti vedere: ...\posture-analysis-service\math_engine

# Verifica che requirements.txt esista
Test-Path requirements.txt
# Dovrebbe restituire: True
```

### 3. Crea Virtual Environment

**Opzione A: Script PowerShell (Consigliato)**

```powershell
# Abilita esecuzione script (solo per questa sessione)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

# Esegui script
.\setup_venv.ps1
```

**Opzione B: Script Batch**

```cmd
setup_venv.bat
```

**Opzione C: Manuale**

```powershell
# Crea venv
python -m venv venv

# Attiva venv
.\venv\Scripts\Activate.ps1

# Aggiorna pip
python -m pip install --upgrade pip

# Installa dipendenze
pip install -r requirements.txt
```

### 4. Attiva Virtual Environment

**PowerShell:**
```powershell
.\venv\Scripts\Activate.ps1
```

**CMD:**
```cmd
venv\Scripts\activate.bat
```

Dovresti vedere `(venv)` all'inizio del prompt.

### 5. Verifica Installazione

```powershell
# Verifica Python
python --version
# Output: Python 3.12.x

# Verifica pacchetti installati
pip list
# Dovresti vedere: fastapi, uvicorn, numpy, mediapipe, etc.
```

### 6. Esegui il Servizio

```powershell
python run.py
```

Il servizio sarà disponibile su: `http://localhost:8000`

## Troubleshooting

### Errore: "Impossibile trovare il percorso 'math_engine'"

**Soluzione:** Assicurati di essere nella directory corretta:
```powershell
# Vai nella directory del progetto
cd "C:\Users\shafa\OneDrive\Desktop\Code\JOB\posture-analysis-service"

# Verifica che math_engine esista
Test-Path math_engine
# Dovrebbe restituire: True

# Entra in math_engine
cd math_engine
```

### Errore: "python3.12 non riconosciuto"

**Soluzione:** Su Windows, usa `python` invece di `python3.12`:
```powershell
# Verifica quale Python hai
python --version

# Se è 3.12, usa semplicemente:
python -m venv venv
```

### Errore: "ExecutionPolicy"

**Soluzione:** Abilita esecuzione script:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Errore: "requirements.txt non trovato"

**Soluzione:** Assicurati di essere nella directory `math_engine`:
```powershell
Get-Location
# Dovresti vedere: ...\math_engine

# Verifica file
Get-ChildItem requirements.txt
```

### Errore: "Module not found"

**Soluzione:** Attiva il venv e reinstalla:
```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Comandi Utili

### Attivare venv
```powershell
.\venv\Scripts\Activate.ps1
```

### Disattivare venv
```powershell
deactivate
```

### Verificare venv attivo
```powershell
# Dovresti vedere (venv) nel prompt
# Oppure:
python -c "import sys; print(sys.prefix)"
# Dovrebbe mostrare il percorso di venv
```

### Reinstallare dipendenze
```powershell
.\venv\Scripts\Activate.ps1
pip install --force-reinstall -r requirements.txt
```

## Struttura Directory Attesa

```
posture-analysis-service/
└── math_engine/
    ├── venv/              # Virtual environment (creato dopo setup)
    ├── requirements.txt
    ├── setup_venv.ps1
    ├── setup_venv.bat
    ├── main.py
    └── ...
```

## Prossimi Passi

Dopo il setup:
1. Attiva il venv: `.\venv\Scripts\Activate.ps1`
2. Esegui il servizio: `python run.py`
3. Testa: `curl http://localhost:8000/health`
4. Documentazione API: `http://localhost:8000/docs`

