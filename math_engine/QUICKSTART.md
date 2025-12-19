# Quick Start - Python 3.12

Guida rapida per iniziare con il microservizio.

## Prerequisiti

- Python 3.12 installato
- pip (incluso con Python)

## Setup Rapido

### 1. Vai nella directory math_engine

```powershell
cd "C:\Users\shafa\OneDrive\Desktop\Code\JOB\posture-analysis-service\math_engine"
```

### 2. Crea Virtual Environment

**Windows (PowerShell - Consigliato):**
```powershell
# Esegui con permessi di esecuzione
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\setup_venv.ps1
```

**Windows (CMD/Batch):**
```cmd
setup_venv.bat
```

**Linux/Mac:**
```bash
chmod +x setup_venv.sh
./setup_venv.sh
```

### 3. Attiva Virtual Environment

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

Dovresti vedere `(venv)` nel prompt.

### 4. Esegui il Servizio

```powershell
python run.py
```

### 5. Testa il Servizio

Apri un altro terminale e testa:

```bash
curl http://localhost:8000/health
```

Dovresti vedere: `{"status":"healthy"}`

## Documentazione API

Una volta avviato, visita:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Disattivare Virtual Environment

```bash
deactivate
```

## Troubleshooting

### "Python 3.12 non trovato"

Installa Python 3.12 da: https://www.python.org/downloads/

### "venv non funziona"

Assicurati di usare Python 3.12:
```bash
python --version  # Deve essere 3.12.x
python -m venv venv
```

### "Module not found"

Attiva il venv e reinstalla:
```bash
source venv/bin/activate  # o venv\Scripts\activate.bat su Windows
pip install -r requirements.txt
```

