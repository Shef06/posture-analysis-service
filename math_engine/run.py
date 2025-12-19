"""
Script per eseguire il microservizio localmente
"""
import sys
import os
from pathlib import Path

# Aggiungi la directory padre al PYTHONPATH per permettere l'import di math_engine
current_dir = Path(__file__).parent.absolute()
parent_dir = current_dir.parent.absolute()

if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

import uvicorn

if __name__ == "__main__":
    # Esegui il modulo math_engine.main:app
    uvicorn.run(
        "math_engine.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Auto-reload in sviluppo
    )

