#!/usr/bin/env bash
# build.sh — Régénère tous les assets dérivés du mémorial.
# Idempotent : à relancer après toute modification des données, du CSS ou des images.
#
#   ./scripts/build.sh
#
# Prérequis : python3 (+ pydantic, Pillow), npx (Node) pour Tailwind.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "1/3 · Données : validation Pydantic -> assets/js/data.js"
python3 scripts/build_data.py

echo "2/3 · Images : dérivés WebP (les originaux + leur SHA-256 restent la référence)"
python3 - <<'PY'
from PIL import Image
from pathlib import Path
for src in sorted(Path("assets/images").glob("*")):
    if src.suffix.lower() not in (".jpg", ".jpeg", ".gif", ".png"):
        continue
    im = Image.open(src)
    if im.mode in ("P", "RGBA", "LA"):
        im = im.convert("RGB")
    q = 90 if max(im.size) <= 200 else 82
    im.save(src.with_suffix(".webp"), "WEBP", quality=q, method=6)
    print(f"   {src.name} -> {src.stem}.webp")
PY

echo "3/4 · Polices : téléchargement, sous-ensemble et fonts.css"
python3 scripts/build_fonts.py

echo "4/4 · CSS : Tailwind compilé et minifié (classes réellement utilisées) -> assets/css/tailwind.css"
npx -y tailwindcss@3 -c tailwind.config.js -i assets/css/tailwind-input.css -o assets/css/tailwind.css --minify

echo "Terminé. Pense à incrémenter le ?v= des assets dans index.html si CSS/JS ont changé."
