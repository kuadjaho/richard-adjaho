# Richard Kokou ADJAHO (1949 – 2009) — Site hommage

Projet mémorial dédié à **Richard Kokou Adjaho** : haut fonctionnaire, ministre de
l'Intérieur (1991-1993), ambassadeur du Bénin en France (1994-1996), l'un des pères
de la décentralisation béninoise, et écrivain.

Ce dépôt rassemble le corpus documentaire (collecte OSINT du 7 juillet 2026) et la
base du site web hommage.

## Structure du dépôt

| Dossier | Contenu |
|---------|---------|
| `data/` | Données structurées — `richard_adjaho_heritage.json` (corpus principal, schéma v2.0) et `photos_catalog.json` (12 photos planifiées) |
| `schema/` | `schema_heritage.py` — modèle Pydantic v2 validant le JIS du corpus |
| `scraper/` | `scraper_adjaho.py` — script de collecte OSINT (Jina Reader + fallback BeautifulSoup, module photos) |
| `docs/` | `dossier_sources_adjaho.md` — synthèse du balayage web, chronologie, bibliographie, sources |
| `site/` | `index.html` — aperçu web (onglets Chronologie / Bibliographie / Hommages / Photos / JSON) |

## Données clés

- **Chronologie** : 11 périodes, de la formation en France (≈1968-1978) aux hommages posthumes (2009+).
- **Bibliographie** : 5 ouvrages, tous aux **Éditions du Flamboyant** (Cotonou) — *pas* L'Harmattan.
- **Hommages** : 6 articles de presse (La Nouvelle Tribune, La Nation, L'Événement Précis, etc.).
- **Photos** : 12 planifiées — 3 confirmées, 9 à récupérer (dont archives familiales).

## Prévisualiser le site

Ouvrir `site/index.html` dans un navigateur, ou servir localement :

```bash
python3 -m http.server -d site 8000
# puis http://localhost:8000
```

## Relancer la collecte

```bash
pip install requests beautifulsoup4
python scraper/scraper_adjaho.py            # collecte les cibles + récolte photos
```

Les sorties (`corpus/`, `photos/`) sont ignorées par git (voir `.gitignore`).

## Valider le corpus contre le schéma

```bash
pip install pydantic
python -c "from schema.schema_heritage import RichardAdjahoHeritage; import json; \
RichardAdjahoHeritage.model_validate(json.load(open('data/richard_adjaho_heritage.json')))"
```

## Notes méthodologiques

Voir le champ `notes_methodologiques` dans `data/richard_adjaho_heritage.json`.
Corrections majeures déjà intégrées : éditeur (Flamboyant), dates du ministère de
l'Intérieur (1991-1993), intitulé exact du portefeuille (« Administration territoriale »).

## Pistes ouvertes

- Récupérer les 9 photos « à_recuperer » (Wayback Machine, BnF/WorldCat, archives familiales).
- Extraire les sources rendues côté client (La Nation, Tribune de la Capitale, Hub Rural).
- Inventorier les décrets 1991-1993 sur `sgg.gouv.bj`.
- Verser un portrait libre de droits sur Wikimedia Commons (la fiche Wikipédia n'a pas de photo).
