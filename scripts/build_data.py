#!/usr/bin/env python3
"""build_data.py — Régénère assets/js/data.js depuis data/*.json.

Garde une source unique de vérité : le site n'embarque jamais de données
saisies à la main. Valide le corpus contre le schéma Pydantic avant d'écrire.

Usage : python3 scripts/build_data.py
"""
from __future__ import annotations
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "schema"))

from schema_heritage import RichardAdjahoHeritage  # noqa: E402


def main() -> None:
    heritage = json.loads((ROOT / "data" / "richard_adjaho_heritage.json").read_text(encoding="utf-8"))
    photos = json.loads((ROOT / "data" / "photos_catalog.json").read_text(encoding="utf-8"))

    # Validation stricte avant embarquement
    RichardAdjahoHeritage.model_validate(heritage)
    print("Schéma Pydantic : VALIDE ✓")

    out = (
        "// GÉNÉRÉ PAR scripts/build_data.py — NE PAS ÉDITER À LA MAIN.\n"
        f"// Source : data/richard_adjaho_heritage.json + data/photos_catalog.json (build du {date.today().isoformat()})\n"
        f"window.HERITAGE = {json.dumps(heritage, ensure_ascii=False, indent=1)};\n"
        f"window.PHOTOS = {json.dumps(photos, ensure_ascii=False, indent=1)};\n"
    )
    dest = ROOT / "assets" / "js" / "data.js"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(out, encoding="utf-8")
    print(f"Écrit : {dest.relative_to(ROOT)} ({len(out)//1024} Ko)")


if __name__ == "__main__":
    main()
