#!/usr/bin/env python3
"""build_fonts.py — Télécharge, sous-ensemble et déclare les polices du mémorial.

Le site n'appelle aucun service tiers : les .woff2 vivent dans assets/fonts/ et
assets/css/fonts.css est généré ici, avec des unicode-range EXACTS (un caractère
absent bascule proprement sur la police de repli au lieu d'afficher un carré vide).

Le jeu de caractères est déduit du contenu réel du site + une marge couvrant
l'alphabet français complet (ligatures œ/Œ incluses).

Prérequis : pip install fonttools brotli
Usage     : python3 scripts/build_fonts.py
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "assets" / "fonts"
CSS = ROOT / "assets" / "css" / "fonts.css"

API = ("https://fonts.googleapis.com/css2?"
       "family=Playfair+Display:ital,wght@0,500;0,700;0,900;1,500"
       "&family=Inter:wght@400;500;600&display=swap")
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")

# Seul le sous-ensemble « latin » est retenu : « latin-ext » n'apporterait que
# Ÿ et †, absents du site (vérifié). œ et Œ sont bien dans « latin ».
SUBSET = "latin"

# Marge de sécurité : ASCII + accents et ponctuation français/européens.
MARGE = (" !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`"
         "abcdefghijklmnopqrstuvwxyz{|}~"
         "àâäæçéèêëîïôöœùûüÿÀÂÄÆÇÉÈÊËÎÏÔÖŒÙÛÜŸ"
         "«»‹›“”‘’–—…·•€°§†‡™©®±×÷"
         "áãåíìñóòõúÁÃÅÍÌÑÓÒÕÚ")

SOURCES_TEXTE = [
    "data/richard_adjaho_heritage.json", "data/photos_catalog.json", "index.html",
    "assets/js/timeline.js", "assets/js/gallery.js", "assets/js/temoignages.js",
    "assets/js/main.js",
]


def charset() -> str:
    chars: set[str] = set(MARGE)
    for rel in SOURCES_TEXTE:
        chars |= set((ROOT / rel).read_text(encoding="utf-8"))
    return "".join(sorted(c for c in chars if ord(c) >= 32))


def unicode_range(path: Path) -> str:
    font = TTFont(path)
    cps: set[int] = set()
    for table in font["cmap"].tables:
        cps |= set(table.cmap.keys())
    font.close()
    ordered = sorted(c for c in cps if c >= 32)
    parts, i = [], 0
    while i < len(ordered):
        j = i
        while j + 1 < len(ordered) and ordered[j + 1] == ordered[j] + 1:
            j += 1
        parts.append(f"U+{ordered[i]:04X}" if i == j
                     else f"U+{ordered[i]:04X}-{ordered[j]:04X}")
        i = j + 1
    return ", ".join(parts)


def main() -> None:
    FONTS.mkdir(parents=True, exist_ok=True)
    txt = charset()
    liste = ROOT / "assets" / "fonts" / ".charset.txt"
    liste.write_text(txt, encoding="utf-8")
    print(f"Jeu de caractères : {len(txt)} glyphes")

    css = subprocess.run(["curl", "-sS", "--fail", "-A", UA, API],
                         check=True, capture_output=True, text=True).stdout

    specs = []
    for sub, bloc in re.findall(r"/\*\s*([a-z0-9\-]+)\s*\*/\s*(@font-face\s*\{[^}]+\})", css):
        if sub != SUBSET:
            continue
        fam = re.search(r"font-family:\s*'([^']+)'", bloc).group(1)
        style = re.search(r"font-style:\s*(\w+)", bloc).group(1)
        poids = re.search(r"font-weight:\s*(\d+)", bloc).group(1)
        url = re.search(r"url\((https[^)]+\.woff2)\)", bloc).group(1)
        nom = f"{fam.lower().replace(' ', '-')}-{poids}{'-italic' if style == 'italic' else ''}-{sub}.woff2"
        dest = FONTS / nom
        subprocess.run(["curl", "-sS", "--fail", "--retry", "3", "-A", UA, url,
                        "-o", str(dest)], check=True)
        subprocess.run([sys.executable, "-m", "fontTools.subset", str(dest),
                        f"--text-file={liste}", "--flavor=woff2",
                        "--layout-features=kern,liga,clig,calt,ccmp,locl,mark,mkmk",
                        f"--output-file={dest}"], check=True, stdout=subprocess.DEVNULL)
        specs.append((fam, style, poids, nom))
        print(f"  {nom:40} {dest.stat().st_size // 1024:>3} Ko")

    entete = ("/* fonts.css — GÉNÉRÉ PAR scripts/build_fonts.py, ne pas éditer à la main.\n"
              "   Polices auto-hébergées : aucune requête vers un service tiers.\n"
              "   Playfair Display (Claus Eggers Sørensen) et Inter (Rasmus Andersson),\n"
              "   SIL Open Font License 1.1 — voir assets/fonts/LICENSE.md. */\n")
    blocs = [f"""@font-face {{
  font-family: '{fam}';
  font-style: {style};
  font-weight: {poids};
  font-display: swap;
  src: url(../fonts/{nom}) format('woff2');
  unicode-range: {unicode_range(FONTS / nom)};
}}""" for fam, style, poids, nom in specs]
    CSS.write_text(entete + "\n" + "\n".join(blocs) + "\n", encoding="utf-8")
    total = sum(f.stat().st_size for f in FONTS.glob("*.woff2"))
    print(f"\n{len(specs)} polices, {total // 1024} Ko au total -> {CSS.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
