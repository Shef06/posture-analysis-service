# Installazione - Python 3.12

## Requisiti

- **Python 3.12** (richiesto)
- pip (gestore pacchetti Python)

## Verifica Versione Python

```bash
python --version
# Output atteso: Python 3.12.x
```

Se non hai Python 3.12, installalo da:
- [python.org](https://www.python.org/downloads/)
- oppure usa pyenv: `pyenv install 3.12`

## Installazione con Virtual Environment (Consigliato)

### Windows

```bash
cd math_engine
setup_venv.bat
```

### Linux/Mac

```bash
cd math_engine
chmod +x setup_venv.sh
./setup_venv.sh
```

### Manuale

```bash
cd math_engine

# Crea venv con Python 3.12
python3.12 -m venv venv

# Attiva venv
# Windows:
venv\Scripts\activate.bat
# Linux/Mac:
source venv/bin/activate

# Installa dipendenze
pip install --upgrade pip
pip install -r requirements.txt
```

## Installazione Dipendenze (senza venv)

### Metodo 1: pip diretto

```bash
cd math_engine
pip install -r requirements.txt
```

### Metodo 2: pip con pyproject.toml

```bash
cd math_engine
pip install -e .
```

## Esecuzione

### Con Virtual Environment

```bash
# Attiva venv (se non già attivo)
# Windows:
venv\Scripts\activate.bat
# Linux/Mac:
source venv/bin/activate

# Esegui
python run.py
```

### Senza Virtual Environment

```bash
python run.py
```

Il servizio sarà disponibile su: `http://localhost:8000`

### Produzione

```bash
uvicorn math_engine.main:app --host 0.0.0.0 --port 8000
```

## Docker

### Build

```bash
cd math_engine
docker build -t posture-math-engine:latest .
```

### Run

```bash
docker run -p 8000:8000 posture-math-engine:latest
```

### Docker Compose

```bash
cd math_engine
docker-compose up
```

## Verifica Installazione

```bash
# Test health check
curl http://localhost:8000/health

# Output atteso: {"status":"healthy"}
```

## Troubleshooting

### Errore: "Python version not supported"

Assicurati di usare Python 3.12:
```bash
python --version  # Deve essere 3.12.x
```

### Errore: "MediaPipe not found"

MediaPipe è incluso in `requirements.txt` per Python 3.12. Se hai problemi:
```bash
pip install --upgrade mediapipe opencv-python-headless
```

### Errore: "Module not found"

Reinstalla tutte le dipendenze:
```bash
pip install --force-reinstall -r requirements.txt
```

