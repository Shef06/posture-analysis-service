# Configurazione Python 3.12

Il microservizio è configurato per **Python 3.12**.

## Perché Python 3.12?

- ✅ Supporta MediaPipe (estrazione landmark da video)
- ✅ Supporta tutte le dipendenze necessarie
- ✅ Stabile e ben supportato
- ✅ Compatibile con NumPy 1.24.3+

## Dipendenze Incluse

Tutte le dipendenze sono incluse in `requirements.txt`:

- **FastAPI**: Framework web
- **Pydantic**: Validazione dati
- **NumPy**: Calcolo scientifico (>=1.24.3)
- **MediaPipe**: Estrazione landmark da video ✅
- **OpenCV**: Processing video ✅

## Installazione

### Locale (Python 3.12)
```bash
# Verifica versione Python
python --version  # Deve essere 3.12.x

# Installa dipendenze
pip install -r requirements.txt

# Esegui il servizio
python run.py
```

### Docker
```bash
# Build (usa Python 3.12 automaticamente)
docker build -t posture-math-engine:latest .

# Run
docker run -p 8000:8000 posture-math-engine:latest
```

## Endpoint Disponibili

Con Python 3.12, **tutti gli endpoint** sono disponibili:

- ✅ `POST /v1/compute-ghost-profile` - Calcolo Ghost Profile
- ✅ `POST /v1/analyze-run` - Analisi corsa
- ✅ `POST /v1/extract-from-video` - Estrazione landmark da video (MediaPipe)

## Note

- **Python 3.13**: Non supportato (MediaPipe non disponibile)
- **Python 3.11**: Supportato, ma si consiglia 3.12
- **Python 3.10 o inferiore**: Non testato

