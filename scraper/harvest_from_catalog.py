#!/usr/bin/env python3
"""harvest_from_catalog.py — Récupère les photos de data/photos_catalog.json.

Pour chaque entrée :
  - si url_image est connue -> téléchargement direct ;
  - sinon -> on scrape la page_source (og:image + <img>) pour découvrir une image.
Calcule le SHA-256 complet, sauvegarde dans site/photos/, et met à jour le catalogue.

Réutilise la logique de scraper_adjaho.py (UA poli, filtres taille/motif, dédoublonnage).
"""
from __future__ import annotations
import hashlib, json, re, sys, time
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "data" / "photos_catalog.json"
PHOTO_DIR = ROOT / "site" / "photos"

UA = {"User-Agent": ("Mozilla/5.0 (compatible; HommageAdjahoBot/1.0; "
                     "+mailto:adjahoulysse@gmail.com; projet memorial familial)")}
TIMEOUT = 45
MIN_BYTES = 15_000
IMG_EXT = re.compile(r"\.(jpe?g|png|webp|gif)(\?|$)", re.I)
SKIP_PAT = re.compile(r"logo|icon|sprite|avatar-default|banner|pub|ads?[-_/.]|favicon", re.I)

_last: dict[str, float] = {}
def polite(url: str, delay: float = 3.0) -> None:
    d = urlparse(url).netloc
    el = time.monotonic() - _last.get(d, 0.0)
    if el < delay:
        time.sleep(delay - el)
    _last[d] = time.monotonic()

def get(url: str) -> requests.Response | None:
    try:
        polite(url)
        r = requests.get(url, headers=UA, timeout=TIMEOUT)
        return r if r.ok else None
    except requests.RequestException as e:
        print(f"    [err] {type(e).__name__}: {str(e)[:70]}")
        return None

def discover_image(page: str) -> str | None:
    """Trouve la meilleure image candidate sur une page (og:image prioritaire)."""
    r = get(page)
    if not r:
        return None
    soup = BeautifulSoup(r.text, "html.parser")
    for prop in ("og:image", "twitter:image", "twitter:image:src"):
        m = soup.find("meta", attrs={"property": prop}) or soup.find("meta", attrs={"name": prop})
        if m and m.get("content"):
            cand = urljoin(page, m["content"])
            if not SKIP_PAT.search(cand):
                return cand
    for img in soup.find_all("img", src=True):
        full = urljoin(page, img["src"])
        if IMG_EXT.search(full) and not SKIP_PAT.search(full):
            return full
    return None

def download(url: str) -> tuple[bytes, str] | None:
    r = get(url)
    if not r:
        return None
    ctype = r.headers.get("content-type", "")
    if "image" not in ctype and not IMG_EXT.search(url):
        print(f"    [skip] pas une image ({ctype})")
        return None
    return r.content, ctype

def ext_for(url: str, ctype: str) -> str:
    for e in ("jpeg", "jpg", "png", "webp", "gif"):
        if e in ctype:
            return "jpg" if e == "jpeg" else e
    m = IMG_EXT.search(url)
    return (m.group(1).lower().replace("jpeg", "jpg")) if m else "img"

def main() -> None:
    PHOTO_DIR.mkdir(parents=True, exist_ok=True)
    cat = json.loads(CATALOG.read_text(encoding="utf-8"))
    seen: dict[str, int] = {}   # sha256 -> rang déjà enregistré
    ok = 0

    for p in cat["photos"]:
        rang = p["rang"]
        print(f"\n[{rang}/12] {p['description_alt'][:60]}")
        url = p.get("url_image")
        source = "url_image"
        if not url:
            print(f"    découverte via page_source : {p['page_source'][:70]}")
            if p["page_source"].startswith(("archives_familiales", "https://web.archive.org/web/2006*",
                                            "https://web.archive.org/web/2009*",
                                            "https://www.gettyimages.com", "https://www.getty")):
                print("    -> source non automatisable (archives/Wayback glob/Getty) — ignorée")
                p["statut"] = p.get("statut", "a_recuperer")
                continue
            url = discover_image(p["page_source"])
            source = "og:image découverte"
            if not url:
                print("    -> aucune image trouvée")
                continue
            p["url_image"] = url
            print(f"    -> {url[:75]}")

        dl = download(url)
        if not dl:
            continue
        content, ctype = dl
        kb = len(content) // 1024
        sha = hashlib.sha256(content).hexdigest()
        if len(content) < MIN_BYTES:
            print(f"    [petit] {kb} Ko (<{MIN_BYTES//1024} Ko) — probable placeholder, sha calculé quand même")
        if sha in seen:
            print(f"    [doublon] même SHA que rang {seen[sha]} — non ré-enregistré")
            p["sha256"] = sha
            p["note_harvest"] = f"doublon du rang {seen[sha]}"
            continue
        seen[sha] = rang
        fname = f"{rang:02d}_{sha[:12]}.{ext_for(url, ctype)}"
        (PHOTO_DIR / fname).write_bytes(content)
        p["sha256"] = sha
        p["fichier_local"] = f"site/photos/{fname}"
        p["octets"] = len(content)
        if p["statut"] == "a_recuperer":
            p["statut"] = "confirmee"
        ok += 1
        print(f"    [ok] {fname} ({kb} Ko) via {source}")
        print(f"         sha256 = {sha}")

    cat["genere_le"] = "2026-07-07"
    cat["note"] = ("SHA-256 complets calculés au téléchargement par harvest_from_catalog.py. "
                   "Images enregistrées dans site/photos/. Entrées sans fichier_local = à récupérer "
                   "manuellement (Wayback/Getty/archives familiales).")
    CATALOG.write_text(json.dumps(cat, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n=== {ok} image(s) téléchargée(s) -> {PHOTO_DIR} ===")
    print(f"=== catalogue mis à jour : {CATALOG} ===")

if __name__ == "__main__":
    main()
