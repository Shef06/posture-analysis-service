# Guida Esecuzione - Math Engine

## Metodi di Esecuzione

### ✅ Metodo Consigliato: Usa `run.py`

```powershell
# Attiva venv (se necessario)
.\venv\Scripts\Activate.ps1

# Esegui
python run.py
```

Questo metodo funziona sempre perché esegue il modulo come package.

### ✅ Metodo Alternativo: Uvicorn Diretto

```powershell
# Dalla directory math_engine
uvicorn math_engine.main:app --host 0.0.0.0 --port 8000 --reload
```

### ❌ NON Usare: Esecuzione Diretta

```powershell
# NON funziona a causa degli import relativi
python main.py  # ❌ Errore: ImportError
```

## Perché `python main.py` non funziona?

Il file `main.py` usa import relativi (`.models`, `.ghost_engine`) che funzionano solo quando il modulo è importato come parte di un package Python.

- ✅ `python run.py` → Esegue `math_engine.main:app` come package
- ✅ `uvicorn math_engine.main:app` → Importa come package
- ❌ `python main.py` → Esecuzione diretta, non è un package

## Soluzione Implementata

Il codice è stato aggiornato per supportare entrambi i casi:
- Quando eseguito come package: usa import relativi (`.models`)
- Quando eseguito direttamente: usa import assoluti (`math_engine.models`)

Tuttavia, **si consiglia sempre di usare `run.py`** per evitare problemi.

## Verifica Funzionamento

Dopo l'avvio, verifica:

```powershell
# Health check
curl http://localhost:8000/health

# Dovresti vedere: {"status":"healthy"}
```

## Documentazione API

Una volta avviato:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc





