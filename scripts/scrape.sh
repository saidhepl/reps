#!/usr/bin/env bash
# Lance URS avec les identifiants du .env à la racine du repo.
# Exemple : ./scripts/scrape.sh -r france h 25
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
URS_DIR="$ROOT/vendor/URS"

if [ -f "$ROOT/.env" ]; then
  set -a; . "$ROOT/.env"; set +a
fi

cd "$URS_DIR/urs"
exec "$URS_DIR/.venv/bin/python" ./Urs.py "$@"
