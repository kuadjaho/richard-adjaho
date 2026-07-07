// timeline.js — Chronologie interactive en 11 étapes (III).
// Rend chaque étape de HERITAGE.chronologie_carriere en carte alternée
// autour d'un axe central, avec badges décrets et citations verbatim.
(function () {
  "use strict";

  const LIBELLES_PERIODES = {
    formation: "Formation",
    haut_fonctionnaire: "Haut fonctionnaire",
    ministre_transition: "Ministre de la transition",
    ministre_interieur: "Ministre de l'Intérieur",
    ambassadeur: "Ambassadeur",
    decentralisation_idec: "Père de la décentralisation",
    elu_local: "Élu local",
    presidentielle_2006: "Présidentielle 2006",
    commissions_boni_yayi: "Commissions nationales",
    posthume: "Mémoire",
  };

  const esc = (s) =>
    String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

  // "2019-12-18" -> "18 décembre 2019" ; "2019-12" -> "décembre 2019" ; "2019" -> "2019".
  const MOIS = ["janvier", "février", "mars", "avril", "mai", "juin",
    "juillet", "août", "septembre", "octobre", "novembre", "décembre"];
  window.dateFR = function (iso) {
    if (!iso) return "";
    const [a, m, j] = String(iso).split("-");
    if (!m) return a;
    const mois = MOIS[Number(m) - 1] || "";
    if (!j) return `${mois} ${a}`;
    const jour = Number(j) === 1 ? "1er" : String(Number(j));
    return `${jour} ${mois} ${a}`;
  };

  // Périodes du corpus rendues en mots ("≈1968-1978" -> "Vers 1968-1978").
  function periodeEnMots(p) {
    return String(p).replace(/^≈/, "Vers ").replace(/-…$/, " et après");
  }

  function badgeLoi(t) {
    const ok = t.statut_verification === "verifie";
    const badge = ok
      ? '<span class="badge-verifie" title="Source vérifiée">✓ vérifié</span>'
      : '<span class="badge-averifier" title="À vérifier">⚠ à vérifier</span>';
    const titre = `${esc(t.reference)} · ${esc(t.titre)}`;
    const lien = t.url_source
      ? `<a href="${esc(t.url_source)}" target="_blank" rel="noopener" class="underline decoration-dotted underline-offset-2 hover:text-[--foret]">${titre}</a>`
      : titre;
    return `<li class="flex flex-wrap items-baseline gap-x-2 gap-y-1 text-xs text-[--encre-2]">
      <span aria-hidden="true">📜</span>${lien} ${badge}</li>`;
  }

  function citation(c) {
    const annee = c.date ? String(c.date).slice(0, 4) : "";
    return `<figure class="mt-4 border-l-2 border-[--or] pl-4">
      <blockquote class="font-serif italic text-[0.95rem] leading-relaxed text-gray-700">« ${esc(c.texte)} »</blockquote>
      <figcaption class="mt-1 text-xs text-[--encre-2]">— ${esc(c.auteur || c.source)}, <cite>${esc(c.source)}</cite>${annee ? ", " + annee : ""}</figcaption>
    </figure>`;
  }

  function carte(etape, i) {
    const gauche = i % 2 === 0; // alternance desktop
    const realisations = etape.realisations_cles.length
      ? `<ul class="mt-3 space-y-1.5 text-sm leading-snug list-disc list-inside marker:text-[--or]">
          ${etape.realisations_cles.map((r) => `<li>${esc(r)}</li>`).join("")}</ul>`
      : "";
    const lois = etape.textes_loi_associes.length
      ? `<ul class="mt-3 space-y-1">${etape.textes_loi_associes.map(badgeLoi).join("")}</ul>`
      : "";
    const citations = etape.citations_presse.map(citation).join("");

    return `
    <li class="timeline-etape reveal relative pl-10 pb-12 md:pl-0 md:grid md:grid-cols-2 md:gap-10">
      <span class="timeline-puce" aria-hidden="true"></span>
      <div class="${gauche ? "md:col-start-1 md:text-right" : "md:col-start-2"} md:row-start-1">
        <p class="timeline-annee text-2xl md:text-3xl">${esc(periodeEnMots(etape.periode))}</p>
        <p class="mt-0.5 text-[0.7rem] font-semibold uppercase tracking-[0.18em] text-[--or]">
          ${esc(LIBELLES_PERIODES[etape.type_periode] || etape.type_periode)}</p>
      </div>
      <article class="${gauche ? "md:col-start-2" : "md:col-start-1 md:text-left"} md:row-start-1 mt-3 md:mt-0
                      bg-white/70 border border-[--filet] rounded-xl p-5 shadow-sm">
        <h3 class="font-serif font-bold text-lg leading-snug">${esc(etape.poste)}</h3>
        ${etape.institution ? `<p class="mt-1 text-xs font-medium uppercase tracking-wide text-[--encre-2]">${esc(etape.institution)}</p>` : ""}
        ${etape.contexte_historique ? `<p class="mt-3 text-sm text-gray-600 leading-relaxed">${esc(etape.contexte_historique)}</p>` : ""}
        ${realisations}${lois}${citations}
      </article>
    </li>`;
  }

  window.rendreTimeline = function (conteneur) {
    conteneur.innerHTML = `<ol class="timeline list-none m-0 p-0">
      ${window.HERITAGE.chronologie_carriere.map(carte).join("")}</ol>`;
  };
})();
