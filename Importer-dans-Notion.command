#!/bin/bash
# Wrapper macOS pour lancer l'import Notion en double-clic.
# Cabinet Kohen Avocats - juris-notion.
# Installe Python 3 automatiquement via les Xcode Command Line Tools si absent.

set -e
cd "$(dirname "$0")"

# --- Verifie / installe Python 3 -----------------------------------------
if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 n'est pas installe sur ce Mac."
  echo "Lancement de l'installation automatique des outils de developpement..."
  echo

  RESPONSE=$(osascript -e 'display dialog "Python 3 est requis pour importer la jurisprudence dans Notion.\n\nMacOS va vous proposer d'\''installer les outils Apple necessaires (environ 200 Mo, 5 minutes).\n\nCliquez OK pour lancer l'\''installation." buttons {"Annuler", "OK"} default button "OK" with icon note' 2>/dev/null || echo "cancelled")

  if echo "$RESPONSE" | grep -q "Annuler\|cancelled"; then
    echo "Installation annulee. Vous pouvez aussi installer Python 3 depuis :"
    echo "  https://www.python.org/downloads/macos/"
    open "https://www.python.org/downloads/macos/"
    exit 1
  fi

  # Declenche le dialog macOS pour les Command Line Tools (qui incluent python3)
  xcode-select --install 2>/dev/null || true

  echo
  echo "Le dialog d'installation s'est ouvert."
  echo "  1. Cliquez 'Installer' dans la fenetre macOS qui vient d'apparaitre."
  echo "  2. Acceptez la licence."
  echo "  3. Attendez la fin du telechargement (~5 minutes)."
  echo

  # Attente active jusqu'a ce que python3 soit disponible
  echo "En attente de la fin de l'installation..."
  for i in $(seq 1 600); do
    if command -v python3 >/dev/null 2>&1; then
      echo "Python 3 detecte !"
      break
    fi
    sleep 2
  done

  if ! command -v python3 >/dev/null 2>&1; then
    echo
    echo "Timeout : Python 3 toujours absent apres 20 minutes."
    echo "Telechargez manuellement depuis https://www.python.org/downloads/macos/"
    open "https://www.python.org/downloads/macos/"
    read -p "Appuyez sur Entree pour quitter..."
    exit 1
  fi
fi

# --- Environnement virtuel local -----------------------------------------
if [ ! -d ".venv" ]; then
  echo "Premiere utilisation : preparation de l'environnement Python..."
  python3 -m venv .venv
fi

source .venv/bin/activate

# --- Lancement du script -------------------------------------------------
python3 import.py

# Garde la fenetre ouverte a la fin
echo
echo "============================================================"
read -p "Appuyez sur Entree pour fermer cette fenetre..."
