# Licences des polices auto-hébergées

Les deux familles utilisées par ce mémorial sont publiées sous la
**SIL Open Font License, Version 1.1**, qui autorise explicitement l'usage,
la modification, l'incorporation et la redistribution — y compris
l'auto-hébergement et la création de sous-ensembles, comme ici.

| Police | Auteur | Licence | Source |
|---|---|---|---|
| **Playfair Display** | Claus Eggers Sørensen | SIL OFL 1.1 | <https://fonts.google.com/specimen/Playfair+Display> |
| **Inter** | Rasmus Andersson | SIL OFL 1.1 | <https://fonts.google.com/specimen/Inter> |

## Modifications apportées

Les fichiers `.woff2` présents ici sont des **sous-ensembles** des originaux :
seuls les glyphes utilisés par le site (plus une marge couvrant l'alphabet
français complet, ligatures `œ`/`Œ` incluses) ont été conservés, afin d'alléger
le chargement. Aucune modification du dessin des caractères n'a été faite.
Les noms des familles sont inchangés, conformément à l'OFL.

Texte intégral de la licence : <https://openfontlicense.org/>

## Régénération

```bash
python3 scripts/build_fonts.py
```
