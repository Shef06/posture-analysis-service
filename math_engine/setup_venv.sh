#!/bin/bash
# Script per creare e configurare ambiente virtuale Python 3.12

set -e

echo "=== Setup Virtual Environment Python 3.12 ==="

# Verifica Python 3.12
PYTHON_VERSION=$(python3.12 --version 2>&1 || python --version 2>&1)
if [[ ! "$PYTHON_VERSION" =~ "3.12" ]]; then
    echo "❌ Errore: Python 3.12 non trovato"
    echo "   Versione trovata: $PYTHON_VERSION"
    echo "   Installa Python 3.12 da https://www.python.org/downloads/"
    exit 1
fi

echo "✅ Python 3.12 trovato: $PYTHON_VERSION"

# Crea venv
VENV_DIR="venv"
if [ -d "$VENV_DIR" ]; then
    echo "⚠️  Virtual environment già esistente in $VENV_DIR"
    read -p "Vuoi ricrearlo? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗑️  Rimozione venv esistente..."
        rm -rf "$VENV_DIR"
    else
        echo "✅ Usando venv esistente"
        source "$VENV_DIR/bin/activate"
        pip install --upgrade pip
        pip install -r requirements.txt
        echo "✅ Setup completato!"
        exit 0
    fi
fi

# Crea nuovo venv
echo "📦 Creazione virtual environment..."
python3.12 -m venv "$VENV_DIR"

# Attiva venv
echo "🔌 Attivazione virtual environment..."
source "$VENV_DIR/bin/activate"

# Aggiorna pip
echo "⬆️  Aggiornamento pip..."
pip install --upgrade pip

# Installa dipendenze
echo "📥 Installazione dipendenze..."
pip install -r requirements.txt

echo ""
echo "✅ Virtual environment configurato con successo!"
echo ""
echo "Per attivare il venv:"
echo "  source venv/bin/activate"
echo ""
echo "Per disattivare:"
echo "  deactivate"
echo ""

