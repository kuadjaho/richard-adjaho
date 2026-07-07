#!/usr/bin/env python3
"""
scraper_adjaho.py — Collecte OSINT de la trace numérique de Richard Kokou ADJAHO (1949-2009)
Projet : site web hommage.

Stratégie :
  1. Jina Reader (https://r.jina.ai/<URL>) -> markdown nettoyé (pas de clé requise, rate-limité).
  2. Fallback : requests + BeautifulSoup (extraction texte propre) si Jina échoue.
  3. Rate-limiting poli PAR DOMAINE, délai renforcé pour *.gouv.bj.

Sorties :
  corpus/<slug>.md          -> contenu markdown par source
  corpus/_manifest.json     -> métadonnées de collecte (url, statut, méthode, horodatage, catégorie)

Usage :
  pip install requests beautifulsoup4
  python scraper_adjaho.py                  # scrape les TARGETS ci-dessous
  python scraper_adjaho.py urls.txt         # ou une liste d'URLs (une par ligne)
"""

from __future__ import annotations

import json
import re
import sys
import time
import unicodedata
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

# --------------------------------------------------------------------------
# 1. CIBLES — URLs clés vérifiées (web francophone, juillet 2026)
# --------------------------------------------------------------------------

@dataclass
class Target:
    url: str
    categorie: str          # biographie | presse_hommage | officiel_legislatif | bibliographie
    note: str = ""

TARGETS: list[Target] = [
    # ===== BIOGRAPHIE DE BASE =====
    Target("https://fr.wikipedia.org/wiki/Richard_Adjaho",
           "biographie", "Fiche Wikipédia (Djèrègbè 1949 - Cotonou 2009, parcours complet, bibliographie 5 ouvrages)"),
    Target("https://www.wikidata.org/wiki/Q78039112",
           "biographie", "Wikidata : dates, fonctions, identifiants externes"),
    Target("https://wikimonde.com/article/Richard_Adjaho",
           "biographie", "Miroir Wikimonde (peut contenir versions antérieures de la fiche)"),
    Target("https://viadeo.journaldunet.com/p/richard-adjaho-3926047",
           "biographie", "Profil Viadeo archivé — Mairie de Cotonou"),

    # ===== ÉPOQUE 1 : HAUT FONCTIONNAIRE (1978-1990) =====
    # BOAD, Ciments d'Onigbolo, PCA BBD 1982-84, Dir. études/planification Finances,
    # DG Ministère Commerce & Tourisme 1984-90, PCA Sonacop
    Target("https://horizon.documentation.ird.fr/exl-doc/pleins_textes/divers13-09/010033732.pdf",
           "epoque_fonctionnaire", "IRD — références bibliographiques Pop-Bénin (contexte administration)"),

    # ===== ÉPOQUE 2 : MINISTRE (1990-1993) =====
    Target("https://francearchives.gouv.fr/facomponent/174d0f18e2e25bf573eba77f531647291af08cd4",
           "epoque_ministre", "FranceArchives — visite officielle de R. Adjaho, Ministre de l'Intérieur du Bénin"),
    Target("https://sgg.gouv.bj/documentheque/decrets/",
           "officiel_legislatif", "SGG — index des décrets, point d'entrée crawl 1990-1993"),
    Target("https://sgg.gouv.bj/doc/decret-1993-68/download",
           "officiel_legislatif", "Décret 1993 (PDF) — pattern /doc/decret-{annee}-{num}/download"),
    Target("https://sgg.gouv.bj/comptes-rendus-conseils-ministres/",
           "officiel_legislatif", "SGG — comptes rendus du Conseil des ministres"),

    # ===== ÉPOQUE 3 : AMBASSADEUR EN FRANCE (1994-1996) =====
    Target("https://www.legifrance.gouv.fr/affichTexte.do?cidTexte=JORFTEXT000000732435&categorieLien=id",
           "epoque_ambassadeur", "Légifrance/JORF — remise des lettres de créance à Paris"),
    Target("http://latribunedelacapitale.com/societe/4707-portrait-a-titre-posthume-richard-adjaho-un-ambassadeur-du-benin-en-france-hors-pair.html",
           "epoque_ambassadeur", "Tribune de la Capitale — 'un ambassadeur du Bénin en France hors pair' (2019)"),

    # ===== ÉPOQUE 4 : PÈRE DE LA DÉCENTRALISATION / ÉLU LOCAL (1997-2005) =====
    Target("http://www.hubrural.org/Interview-de-Richard-Adjaho-la.html",
           "epoque_decentralisation", "Hub Rural — INTERVIEW de R. Adjaho sur la décentralisation béninoise (verbatim rare)"),
    Target("https://decentralisation.gouv.bj/",
           "epoque_decentralisation", "Ministère de la Décentralisation — contexte historique de la réforme"),

    # ===== ÉPOQUE 5 : PRÉSIDENTIELLE 2006 & DERNIÈRES ANNÉES =====
    Target("https://fr.wikipedia.org/wiki/%C3%89lection_pr%C3%A9sidentielle_b%C3%A9ninoise_de_2006",
           "epoque_2006", "Wikipédia — élection 2006 (26 candidats, n°24 sur le bulletin, candidat RB)"),
    Target("http://www.bbc.co.uk/french/specials/136_benin_candidates/index.shtml",
           "epoque_2006", "BBC Afrique — présentation des candidats 2006 (probable PHOTO officielle)"),

    # ===== DÉCÈS & HOMMAGES (2009-2019) =====
    Target("https://lanouvelletribune.info/2009/12/richard-adjaho-a-tire-sa-reverence/",
           "presse_hommage", "La Nouvelle Tribune — annonce du décès, 'tout sur le parcours du disparu' (déc. 2009)"),
    Target("https://illassa-benoit.over-blog.com/article-carnet-noir-richard-adjaho-ancien-ministre-de-l-interieur-et-ancien-ambassadeur-du-benin-a-paris-est-decede-a-cotonou-benin-41412560",
           "presse_hommage", "Blog Illassa — carnet noir, circonstances du décès (2009)"),
    Target("https://lanationbenin.info/dix-ans-apres-son-deces-le-ministre-richard-adjaho-plus-vivant-que-jamais/",
           "presse_hommage", "La Nation — commémoration 10 ans (2019)"),
    Target("https://lanouvelletribune.info/2019/12/il-etait-une-fois-un-grand-commis-de-letat/",
           "presse_hommage", "La Nouvelle Tribune — 'Il était une fois, un grand commis de l'État' (2019)"),
    Target("http://news.acotonou.com/h/123097.html",
           "presse_hommage", "aCotonou — témoignage de Constant Agbidinoukoun, 10 ans après (leadership)"),

    # ===== BIBLIOGRAPHIE (5 ouvrages recensés, Éditions du Flamboyant) =====
    Target("https://books.google.com/books/about/Bonne_gouvernance_au_B%C3%A9nin.html?id=RFQWAQAAIAAJ",
           "bibliographie", "Google Books — 'Bonne gouvernance au Bénin : ma contribution', Flamboyant, 2005, 148 p."),
    Target("https://books.google.com/books/about/D%C3%A9centralisation_au_B%C3%A9nin_en_Afrique_e.html?id=RruOAAAAMAAJ",
           "bibliographie", "Google Books — 'Décentralisation au Bénin, en Afrique et ailleurs', 2002, 194 p."),
    Target("https://www.econbiz.de/Record/la-faillite-du-contr%C3%B4le-des-finances-publiques-au-b%C3%A9nin-1960-1990-adjaho-richard/10000951044",
           "bibliographie", "EconBiz — 'La faillite du contrôle des finances publiques au Bénin (1960-1990)', Flamboyant, 1992"),
]

# --------------------------------------------------------------------------
# 2. CONFIGURATION
# --------------------------------------------------------------------------

OUT_DIR = Path("corpus")
JINA_PREFIX = "https://r.jina.ai/"          # NB: le endpoint Reader est r.jina.ai, pas jina.ai
UA = ("Mozilla/5.0 (compatible; HommageAdjahoBot/1.0; "
      "+mailto:adjahoulysse@gmail.com; projet memorial familial)")

DEFAULT_DELAY = 4.0        # secondes entre deux requêtes vers un même domaine
GOV_DELAY = 10.0           # délai renforcé pour les serveurs gouvernementaux béninois
MAX_RETRIES = 3
TIMEOUT = 45

_last_hit: dict[str, float] = {}   # domaine -> timestamp dernière requête


def polite_wait(url: str) -> None:
    """Rate-limiting par domaine, avec délai renforcé pour *.gouv.bj."""
    domain = urlparse(url).netloc
    delay = GOV_DELAY if domain.endswith("gouv.bj") else DEFAULT_DELAY
    elapsed = time.monotonic() - _last_hit.get(domain, 0.0)
    if elapsed < delay:
        time.sleep(delay - elapsed)
    _last_hit[domain] = time.monotonic()


def slugify(url: str) -> str:
    p = urlparse(url)
    raw = f"{p.netloc}{p.path}"
    raw = unicodedata.normalize("NFKD", raw).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-zA-Z0-9]+", "-", raw).strip("-").lower()[:120]


# --------------------------------------------------------------------------
# 3. RÉCUPÉRATION : Jina Reader -> fallback requests/BS4
# --------------------------------------------------------------------------

def fetch_via_jina(url: str, session: requests.Session) -> str | None:
    """Markdown nettoyé via Jina Reader."""
    try:
        polite_wait(JINA_PREFIX)  # Jina a aussi ses limites (~20 rpm sans clé)
        r = session.get(JINA_PREFIX + url,
                        headers={"User-Agent": UA, "X-Return-Format": "markdown"},
                        timeout=TIMEOUT)
        if r.ok and len(r.text.strip()) > 200:   # ignore les coquilles vides
            return r.text
    except requests.RequestException as e:
        print(f"    [jina] {e}")
    return None


def fetch_via_requests(url: str, session: requests.Session) -> str | None:
    """Fallback : HTML brut -> texte structuré via BeautifulSoup."""
    try:
        polite_wait(url)
        r = session.get(url, headers={"User-Agent": UA}, timeout=TIMEOUT)
        r.raise_for_status()

        ctype = r.headers.get("content-type", "")
        if "pdf" in ctype or url.endswith("/download"):
            # PDF (ex: décrets SGG) : sauvegarde binaire, extraction à part (pdfplumber)
            pdf_path = OUT_DIR / f"{slugify(url)}.pdf"
            pdf_path.write_bytes(r.content)
            return f"[PDF sauvegardé : {pdf_path.name} — extraire avec pdfplumber/OCR]"

        r.encoding = r.apparent_encoding or "utf-8"
        soup = BeautifulSoup(r.text, "html.parser")
        for tag in soup(["script", "style", "nav", "header", "footer", "aside",
                         "form", "iframe", "noscript"]):
            tag.decompose()
        main = (soup.find("article") or soup.find("main")
                or soup.find(id=re.compile("content|article", re.I)) or soup.body)
        if not main:
            return None
        lines = []
        for el in main.find_all(["h1", "h2", "h3", "h4", "p", "li", "blockquote", "td"]):
            txt = el.get_text(" ", strip=True)
            if not txt or len(txt) < 3:
                continue
            if el.name.startswith("h"):
                lines.append(f"\n{'#' * int(el.name[1])} {txt}\n")
            elif el.name == "blockquote":
                lines.append(f"> {txt}")
            elif el.name == "li":
                lines.append(f"- {txt}")
            else:
                lines.append(txt)
        text = "\n".join(lines)
        return text if len(text) > 200 else None
    except requests.RequestException as e:
        print(f"    [requests] {e}")
        return None


def fetch(target: Target, session: requests.Session) -> dict:
    """Tente Jina puis fallback, avec retries + backoff exponentiel."""
    record = {**asdict(target), "slug": slugify(target.url), "methode": None,
              "statut": "echec", "fichier": None,
              "horodatage": datetime.now(timezone.utc).isoformat()}

    for attempt in range(1, MAX_RETRIES + 1):
        content = fetch_via_jina(target.url, session) or fetch_via_requests(target.url, session)
        if content:
            record["methode"] = "jina" if content and not content.startswith("[PDF") else "requests"
            path = OUT_DIR / f"{record['slug']}.md"
            header = (f"---\nsource_url: {target.url}\ncategorie: {target.categorie}\n"
                      f"note: {target.note}\ncollecte: {record['horodatage']}\n---\n\n")
            path.write_text(header + content, encoding="utf-8")
            record.update(statut="ok", fichier=str(path))
            return record
        wait = 2 ** attempt * 3
        print(f"    tentative {attempt}/{MAX_RETRIES} échouée, pause {wait}s")
        time.sleep(wait)
    return record


# --------------------------------------------------------------------------
# 4. MODULE PHOTOS — objectif : 12 clichés pour le site hommage
# --------------------------------------------------------------------------
# Pages les plus susceptibles de contenir des photos de Richard Adjaho :
# articles de presse hommage, interview Hub Rural, page candidats BBC 2006,
# couvertures d'ouvrages (Google Books), blog Illassa.

import hashlib
from urllib.parse import urljoin

PHOTO_DIR = Path("photos")
MIN_BYTES = 15_000          # écarte icônes, logos, pixels de tracking
PHOTOS_TARGET = 12
IMG_EXT = re.compile(r"\.(jpe?g|png|webp)(\?|$)", re.I)
SKIP_PAT = re.compile(r"logo|icon|sprite|avatar-default|banner|pub|ads?[-_/.]|favicon", re.I)

def harvest_photos(page_urls: list[str], session: requests.Session) -> list[dict]:
    """Télécharge les images candidates des pages sources, dédoublonne par hash.
    Tri final MANUEL indispensable : garder les 12 meilleures dans photos/retenues/."""
    PHOTO_DIR.mkdir(exist_ok=True)
    seen_hashes: set[str] = set()
    catalog: list[dict] = []

    for page in page_urls:
        try:
            polite_wait(page)
            r = session.get(page, headers={"User-Agent": UA}, timeout=TIMEOUT)
            if not r.ok:
                continue
            soup = BeautifulSoup(r.text, "html.parser")
            candidates = []
            # og:image = généralement LA photo de l'article
            og = soup.find("meta", property="og:image")
            if og and og.get("content"):
                candidates.append((og["content"], "og:image"))
            for img in soup.find_all("img", src=True):
                candidates.append((img["src"], img.get("alt", "")))

            for src, ctx in candidates:
                full = urljoin(page, src)
                if not IMG_EXT.search(full) or SKIP_PAT.search(full):
                    continue
                try:
                    polite_wait(full)
                    ir = session.get(full, headers={"User-Agent": UA}, timeout=TIMEOUT)
                    if not ir.ok or len(ir.content) < MIN_BYTES:
                        continue
                    h = hashlib.sha256(ir.content).hexdigest()[:16]
                    if h in seen_hashes:
                        continue
                    seen_hashes.add(h)
                    ext = full.rsplit(".", 1)[-1].split("?")[0].lower()
                    fname = PHOTO_DIR / f"{h}.{ext}"
                    fname.write_bytes(ir.content)
                    catalog.append({"fichier": str(fname), "url_image": full,
                                    "page_source": page, "contexte_alt": str(ctx)[:200],
                                    "octets": len(ir.content)})
                    print(f"    [photo] {fname.name} ({len(ir.content)//1024} Ko) <- {full[:80]}")
                except requests.RequestException:
                    continue
        except requests.RequestException as e:
            print(f"    [photos] {page} : {e}")

    (PHOTO_DIR / "_catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n[photos] {len(catalog)} images candidates -> {PHOTO_DIR}/ "
          f"(objectif : en retenir {PHOTOS_TARGET} manuellement)")
    return catalog


# --------------------------------------------------------------------------
# 5. MAIN
# --------------------------------------------------------------------------

def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)
    targets = TARGETS
    if len(sys.argv) > 1:  # liste d'URLs fournie en argument
        targets = [Target(u.strip(), "custom") for u in
                   Path(sys.argv[1]).read_text().splitlines() if u.strip()]

    session = requests.Session()
    manifest = []
    for i, t in enumerate(targets, 1):
        print(f"[{i}/{len(targets)}] {t.url}")
        rec = fetch(t, session)
        print(f"    -> {rec['statut']} ({rec['methode']})")
        manifest.append(rec)

    (OUT_DIR / "_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    ok = sum(1 for r in manifest if r["statut"] == "ok")
    print(f"\nTerminé : {ok}/{len(manifest)} sources collectées -> {OUT_DIR}/")

    # Récolte de photos sur les pages les plus visuelles
    photo_pages = [t.url for t in targets if t.categorie in
                   ("presse_hommage", "epoque_2006", "epoque_decentralisation",
                    "bibliographie", "biographie")]
    harvest_photos(photo_pages, session)


if __name__ == "__main__":
    main()
