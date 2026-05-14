#!/bin/bash
# Wrapper macOS pour lancer l'import Notion en double-clic.
# Cabinet Kohen Avocats.

set -e
cd "$(dirname "$0")"

# Verifie Python 3
if ! command -v python3 >/dev/null 2>&1; then
  osascript -e 'display dialog "Python 3 n'\''est pas installe.\n\nInstallez-le depuis https://www.python.org/downloads/\npuis double-cliquez a nouveau sur ce fichier." buttons {"OK"} default button "OK" with icon stop'
  open "https://www.python.org/downloads/"
  exit 1
fi

# Cree un venv local si pas deja la
if [ ! -d ".venv" ]; then
  echo "Premiere utilisation : preparation de l'environnement Python..."
  python3 -m venv .venv
fi

# Active venv (compatible bash et zsh)
source .venv/bin/activate

# Installe requests si manquant (rare car on n'utilise que la stdlib)
python3 -c "import urllib.request" 2>/dev/null || pip install --quiet requests

# Lance le script
python3 import.py

# Garde la fenetre ouverte
echo ""
echo "============================================================"
read -p "Appuyez sur Entree pour fermer cette fenetre..."
