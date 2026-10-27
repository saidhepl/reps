#!/usr/bin/env bash
# Installe URS (Universal Reddit Scraper) depuis le sous-module vendor/URS.
# Prérequis : Python 3.11+, Poetry, Rust (cargo).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
URS_DIR="$ROOT/vendor/URS"

for cmd in python3 poetry cargo; do
  command -v "$cmd" >/dev/null || { echo "Manquant : $cmd" >&2; exit 1; }
done

git -C "$ROOT" submodule update --init vendor/URS

cd "$URS_DIR"
poetry install --no-root
poetry run maturin develop --release

# Les résultats d'URS sont écrits dans vendor/URS/scrapes ; lien à la racine pour y accéder.
mkdir -p "$URS_DIR/scrapes"
ln -sfn "vendor/URS/scrapes" "$ROOT/scrapes"

[ -f "$ROOT/.env" ] || cp "$ROOT/.env.example" "$ROOT/.env"
echo "URS installé. Renseigne tes identifiants Reddit dans .env puis lance : ./scripts/scrape.sh -h"
