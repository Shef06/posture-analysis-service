# Dockerfile per Motore Matematico Postura Analysis
# Python 3.12 Slim con MediaPipe e OpenCV per estrazione video

FROM python:3.12-slim

# Metadati
LABEL maintainer="Posture Analysis Team"
LABEL description="Microservizio matematico puro per calcolo Ghost Profile"

# Variabili ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Installa dipendenze di sistema per MediaPipe/OpenCV
# libgl1 è necessario per OpenCV, libglib2.0-0 per MediaPipe
# Se NON usi extract-from-video, puoi rimuovere queste righe
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Crea directory di lavoro
WORKDIR /app

# Copia requirements e installa dipendenze Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia codice applicazione mantenendo struttura package
# NOTA: Dockerfile è dentro math_engine/, quindi copiamo tutto in /app/math_engine/
COPY . ./math_engine/

# Aggiungi /app al PYTHONPATH per permettere import math_engine
ENV PYTHONPATH=/app

# Esponi porta
EXPOSE 8000

# Comando di avvio (usa struttura package)
CMD ["uvicorn", "math_engine.main:app", "--host", "0.0.0.0", "--port", "8000"]

