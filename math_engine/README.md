# Math Engine - Motore Matematico Puro per Analisi Postura

Microservizio Dockerizzato che funge da **Motore Matematico Puro** per l'analisi della postura.

**Python 3.12** richiesto. 

## Caratteristiche

- ✅ **Nessuna dipendenza da file video**: Riceve direttamente dati numerici (liste di landmark)
- ✅ **Calcolo Ghost Profile**: Normalizzazione temporale, media, tolleranze, best run selection
- ✅ **API RESTful**: FastAPI con validazione Pydantic
- ✅ **Dockerizzato**: Pronto per deployment

## Struttura

```
math_engine/
├── __init__.py
├── models.py          # Modelli Pydantic (Landmark, RunData, GhostRequest, etc.)
├── ghost_engine.py    # Logica matematica pura (normalizzazione, media, best run)
├── main.py            # API FastAPI
├── requirements.txt   # Dipendenze Python
├── Dockerfile         # Immagine Docker
└── README.md          # Questo file
```

## Endpoints API

### `POST /v1/compute-ghost-profile`

Calcola il Ghost Profile da 5 corse baseline.

**Input**: `GhostRequest` con 5 `RunData` (liste di landmark)

**Logica Matematica**:
1. Allinea temporalmente le 5 corse (interpolazione lineare)
2. Calcola media punto per punto (X, Y, Z, visibility) per creare lo "Scheletro Ghost"
3. Calcola le tolleranze (deviazione standard)
4. Selezione Best Run: confronta matematicamente (Distanza Euclidea) ogni run originale con la media calcolata

**Output**: `GhostProfile` con:
- `ghost_data`: Lista dei landmark medi (33 landmark)
- `tolerances`: Soglie di errore (deviazioni standard)
- `best_run_index`: Intero (0-4) che indica quale dei 5 dataset è il migliore
- `best_run_distance`: Distanza euclidea della best run

### `POST /v1/analyze-run` (Opzionale)

Analizza una nuova corsa confrontandola con il Ghost Profile.

**Input**: `RunAnalysisRequest` con nuova corsa + Ghost Profile

**Output**: `RunAnalysisResult` con errori calcolati

### `POST /v1/extract-from-video` (Opzionale)

Estrae landmark da un video usando MediaPipe.

**Input**: File video (multipart/form-data)

**Output**: `VideoExtractionResult` con `RunData` estratto

## Modelli Dati

### Landmark
```json
{
  "x": 0.5,
  "y": 0.6,
  "z": 0.1,
  "visibility": 0.9
}
```

### RunData
```json
{
  "frames": [
    {
      "landmarks": [/* 33 landmark */]
    }
  ]
}
```

### GhostRequest
```json
{
  "runs": [/* 5 RunData */],
  "target_frames": 100  // Opzionale
}
```

## Build e Deploy

### Build Docker Image
```bash
cd math_engine
docker build -t posture-math-engine:latest .
```

### Run Container
```bash
docker run -p 8000:8000 posture-math-engine:latest
```

### Test Locale (senza Docker)

**Setup con Virtual Environment (Consigliato):**

```bash
# Windows
setup_venv.bat

# Linux/Mac
chmod +x setup_venv.sh
./setup_venv.sh

# Attiva venv
# Windows: venv\Scripts\activate.bat
# Linux/Mac: source venv/bin/activate

# Esegui
python run.py
```

**Setup diretto (senza venv):**

```bash
# Richiede Python 3.12
pip install -r requirements.txt
python run.py
# oppure
uvicorn math_engine.main:app --host 0.0.0.0 --port 8000
```

## Esempio di Utilizzo

### Calcolo Ghost Profile

```python
import requests

# Prepara dati (5 corse con landmark)
ghost_request = {
    "runs": [
        {"frames": [/* frame 1 */, /* frame 2 */, ...]},  # Run 0
        {"frames": [/* frame 1 */, /* frame 2 */, ...]},  # Run 1
        {"frames": [/* frame 1 */, /* frame 2 */, ...]},  # Run 2
        {"frames": [/* frame 1 */, /* frame 2 */, ...]},  # Run 3
        {"frames": [/* frame 1 */, /* frame 2 */, ...]}   # Run 4
    ],
    "target_frames": 100  # Opzionale
}

response = requests.post(
    "http://localhost:8000/v1/compute-ghost-profile",
    json=ghost_request
)

ghost_profile = response.json()
print(f"Best Run Index: {ghost_profile['best_run_index']}")
print(f"Ghost Data: {ghost_profile['ghost_data']}")
```

## Note

- **Normalizzazione Temporale**: Usa interpolazione lineare per allineare tutte le corse allo stesso numero di frame
- **Best Run Selection**: Calcola distanza euclidea totale tra ogni corsa e la media, seleziona quella con distanza minima
- **Tolleranze**: Deviazioni standard calcolate su tutti i frame normalizzati
- **MediaPipe**: **OPZIONALE** - Richiesto solo per endpoint `extract-from-video`
  - **IMPORTANTE**: MediaPipe supporta solo Python < 3.13
  - Per Python 3.13: l'endpoint `extract-from-video` non è disponibile
  - Per Python 3.11-3.12: installa manualmente `pip install mediapipe opencv-python-headless`
  - Il servizio funziona completamente senza MediaPipe (solo gli endpoint matematici)

## Dipendenze

### Dipendenze Base
- **FastAPI**: Framework web
- **Pydantic**: Validazione dati
- **NumPy**: Calcolo scientifico (>=1.24.3 per Python 3.12)

### Dipendenze per Estrazione Video
- **MediaPipe**: Estrazione landmark da video (supporta Python 3.11-3.12)
- **OpenCV**: Processing video

**Configurazione Python 3.12**: 
- Tutte le dipendenze sono incluse in `requirements.txt`
- MediaPipe è installato automaticamente
- L'endpoint `extract-from-video` è completamente funzionale

