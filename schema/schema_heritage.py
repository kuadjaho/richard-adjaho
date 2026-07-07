"""schema_heritage.py — Modèle Pydantic v2 définitif pour richard_adjaho_heritage.json
Couvre les périodes : 1968-1978 (formation), 1978-1984, 1984-1990, transition 1990-1991,
Intérieur 1991-1993, ambassade 1994-1996, décentralisation/IDEC 1996-2005, Mairie de
Cotonou 2003-2005, présidentielle 2006, commissions Boni Yayi 2006-2009, hommages 2009+.

Usage LLM (extraction structurée) :
    from pydantic import TypeAdapter
    HeritageAdapter = TypeAdapter(RichardAdjahoHeritage)
    data = HeritageAdapter.validate_json(llm_output)
"""

from __future__ import annotations
from typing import Literal, Optional
from pydantic import BaseModel, Field, HttpUrl


class Dates(BaseModel):
    naissance: str = "1949-01-01"
    deces: str = "2009-12-18"
    lieu_naissance: str = "Djèrègbè (ex-colonie du Dahomey, act. commune de Sèmè-Kpodji, Bénin)"
    lieu_deces: str = "CNHU Hubert K. Maga, Cotonou (Bénin)"
    cause_deces: Optional[str] = None


class Famille(BaseModel):
    epouse: Optional[str] = None
    enfants: Optional[str] = None


class Formation(BaseModel):
    diplome: str
    institution: str
    remarque: Optional[str] = None


class Identite(BaseModel):
    nom_complet: str = "Richard Kokou Adjaho"
    dates: Dates = Field(default_factory=Dates)
    titres: list[str] = Field(default_factory=list)
    corps: list[str] = Field(default_factory=list,
                             description="Corps d'appartenance : Inspecteur d'État, Inspecteur général des Finances…")
    formation: list[Formation] = Field(default_factory=list)
    famille: Famille = Field(default_factory=Famille)
    partis: list[str] = Field(default_factory=list)


class TexteLoi(BaseModel):
    reference: str = Field(description="Ex: Décret N°93-68")
    titre: str
    url_source: str = ""
    statut_verification: Literal["verifie", "a_verifier"] = "a_verifier"


class CitationPresse(BaseModel):
    texte: str
    auteur: Optional[str] = None
    source: str
    date: Optional[str] = None
    url: str = ""


PeriodeType = Literal[
    "formation", "haut_fonctionnaire", "ministre_transition", "ministre_interieur",
    "ambassadeur", "decentralisation_idec", "elu_local", "presidentielle_2006",
    "commissions_boni_yayi", "posthume",
]


class EtapeCarriere(BaseModel):
    periode: str = Field(description="Ex: 1991-1993")
    type_periode: PeriodeType
    poste: str
    institution: Optional[str] = None
    contexte_historique: Optional[str] = None
    realisations_cles: list[str] = Field(default_factory=list)
    textes_loi_associes: list[TexteLoi] = Field(default_factory=list)
    citations_presse: list[CitationPresse] = Field(default_factory=list)


class Ouvrage(BaseModel):
    titre: str
    editeur: str = "Éditions du Flamboyant"   # Correction : PAS L'Harmattan
    lieu: Optional[str] = None
    annee: str
    pages: Optional[int] = None
    isbn: Optional[str] = None
    co_auteur: Optional[str] = None
    resume_analytique: str = ""
    piliers_gouvernance: list[str] = Field(default_factory=list)
    urls_reference: list[str] = Field(default_factory=list)


class ArchiveHommage(BaseModel):
    source: str
    date_publication: str = ""
    titre_article: str = ""
    auteur: Optional[str] = None
    extrait_citation: str = ""
    url_origine: str = ""


class PhotoCandidate(BaseModel):
    rang: int
    description_alt: str = Field(description="Texte alternatif accessible pour le site")
    page_source: str
    url_image: Optional[str] = None
    credit: str = ""
    statut: Literal["confirmee", "a_recuperer", "archives_familiales"] = "a_recuperer"
    sha256: Optional[str] = Field(None, description="Calculé au téléchargement par harvest_photos()")


class RichardAdjahoHeritage(BaseModel):
    schema_version: str = "2.0"
    identite: Identite
    chronologie_carriere: list[EtapeCarriere]
    bibliographie: list[Ouvrage] = Field(description="5 ouvrages recensés, Éditions du Flamboyant")
    archives_hommages: list[ArchiveHommage]
    notes_methodologiques: list[str] = Field(default_factory=list)
