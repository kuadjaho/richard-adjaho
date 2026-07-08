// temoignages.js — Le Témoin (IV) et Les Hommages (V).
// Scénarise le témoignage de Constant Agbidinoukoun en récit long-format,
// puis les autres voix de presse en mosaïque éditoriale datée 2009 → 2019.
(function () {
  "use strict";

  const esc = (s) =>
    String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

  // Rassemble toutes les citations d'un auteur dispersées dans la chronologie.
  function citationsDe(nomAuteur) {
    const out = [];
    for (const etape of window.HERITAGE.chronologie_carriere) {
      for (const c of etape.citations_presse) {
        if ((c.auteur || "").includes(nomAuteur)) out.push({ ...c, periode: etape.periode, poste: etape.poste });
      }
    }
    return out;
  }

  // ---------- IV. Le Témoin : Constant Agbidinoukoun ----------
  window.rendreTemoin = function (conteneur) {
    const h = window.HERITAGE;
    const hommage = h.archives_hommages.find((a) => (a.auteur || "").includes("Agbidinoukoun"));
    const citations = citationsDe("Agbidinoukoun");
    const citationMinistre = citationsDe("Richard Adjaho")[0]; // parole rapportée
    const citTerritoire = citations.find((c) => c.texte.includes("convivialité"));
    const citHeritageAdmin = h.chronologie_carriere
      .find((e) => e.type_periode === "posthume")
      .citations_presse.find((c) => (c.auteur || "").includes("Agbidinoukoun"));
    const sourceCourte = (hommage.source || "").split(" (")[0];

    conteneur.innerHTML = `
      <header class="reveal max-w-3xl">
        <p class="text-xs font-semibold uppercase tracking-[0.2em] text-[--encre-2]">
          ${esc(sourceCourte)} · ${esc(window.dateFR(hommage.date_publication))}</p>
        <h3 class="mt-2 font-serif text-2xl md:text-3xl font-bold leading-tight">
          Constant Agbidinoukoun, attaché de presse du ministère de l'Intérieur,
          dix ans après&nbsp;: le témoignage</h3>
      </header>

      <blockquote class="citation-grande reveal mt-10 max-w-4xl">
        Je n'ai jamais travaillé autant dans ma vie de fonctionnaire. Sa rigueur est
        implacable&nbsp;; sa détermination pour réussir tout ce qu'il entreprend est totale.</blockquote>
      <p class="reveal mt-3 text-sm text-[--encre-2]">— ${esc(hommage.auteur)},
        <cite>${esc(sourceCourte)}</cite>, ${esc(window.dateFR(hommage.date_publication))}</p>

      <div class="mt-12 grid gap-10 lg:grid-cols-2">
        <article class="reveal">
          <h4 class="font-serif font-bold text-lg text-[--foret]">Sur le terrain des médiations</h4>
          <p class="lettrine mt-4 text-[0.95rem] leading-relaxed text-gray-700">
            Ministre de l'Intérieur du premier gouvernement élu du Renouveau démocratique,
            de 1991 à 1993, Richard Adjaho sillonne le pays pour préparer le découpage
            territorial et le choix des chefs-lieux des futurs départements. Il arbitre les
            querelles entre Dassa, Savè et Savalou, entre Kétou et Pobè, entre Adjohoun,
            Bonou et Dangbo. Son attaché de presse se souvient de ces tournées de
            conciliation&nbsp;:</p>
          ${citTerritoire ? `
          <figure class="mt-5 border-l-2 border-[--or] pl-5">
            <blockquote class="font-serif italic leading-relaxed text-gray-700">« ${esc(citTerritoire.texte)} »</blockquote>
            <figcaption class="mt-2 text-xs text-[--encre-2]">— ${esc(citTerritoire.auteur)}</figcaption>
          </figure>` : ""}
        </article>

        <article class="reveal" style="--reveal-delay: 120ms">
          <h4 class="font-serif font-bold text-lg text-[--foret]">L'exigence, dès 1989</h4>
          <p class="mt-4 text-[0.95rem] leading-relaxed text-gray-700">
            Avant même la Conférence nationale, alors que le pays traverse la crise de 1989
            et ses sept mois de salaires, pensions et bourses impayés, le directeur général
            du Commerce réunit journalistes et communicateurs pour appeler à la non-violence.
            Sa consigne est restée dans les mémoires&nbsp;:</p>
          ${citationMinistre ? `
          <figure class="mt-5 border-l-2 border-[--or] pl-5">
            <blockquote class="font-serif italic leading-relaxed text-gray-700">« ${esc(citationMinistre.texte)} »</blockquote>
            <figcaption class="mt-2 text-xs text-[--encre-2]">— Richard Adjaho, parole rapportée par Constant&nbsp;Agbidinoukoun</figcaption>
          </figure>` : ""}
        </article>

        <article class="reveal">
          <h4 class="font-serif font-bold text-lg text-[--foret]">1993, la sortie sur un principe</h4>
          <p class="mt-4 text-[0.95rem] leading-relaxed text-gray-700">
            Il quitte le gouvernement en 1993&nbsp;: une prise de parts dans une institution
            publique, contractée sur mauvais conseil, se révèle incompatible avec la
            Constitution. L'homme se retire, puis revient servir le pays comme ambassadeur
            du Bénin à Paris.</p>
        </article>

        <article class="reveal" style="--reveal-delay: 120ms">
          <h4 class="font-serif font-bold text-lg text-[--foret]">Ce qu'il laisse à l'administration</h4>
          ${citHeritageAdmin ? `
          <figure class="mt-4 border-l-2 border-[--or] pl-5">
            <blockquote class="font-serif italic leading-relaxed text-gray-700">« ${esc(citHeritageAdmin.texte)} »</blockquote>
            <figcaption class="mt-2 text-xs text-[--encre-2]">— ${esc(citHeritageAdmin.auteur)}, <cite>${esc((citHeritageAdmin.source || "").split(" (")[0])}</cite></figcaption>
          </figure>` : ""}
          <p class="mt-4 text-[0.95rem] leading-relaxed text-gray-700">
            Époux d'Agnès Avognon Adjaho, nommée en 2019 ambassadrice du Bénin en Italie et
            près le Saint-Siège, il laisse quatre enfants, et cette phrase de son témoin&nbsp;:
            <em>«&nbsp;On ne s'ennuie jamais en compagnie du ministre Richard Adjaho&nbsp;!&nbsp;»</em></p>
        </article>
      </div>`;
  };

  // ---------- V. Les Hommages : mosaïque éditoriale ----------
  window.rendreHommages = function (conteneur) {
    const autres = window.HERITAGE.archives_hommages
      .filter((a) => !(a.auteur || "").includes("Agbidinoukoun"))
      .sort((a, b) => (a.date_publication || "").localeCompare(b.date_publication || ""));

    conteneur.innerHTML = autres
      .map((a, i) => {
        const perdu = (a.extrait_citation || "").startsWith("(ARTICLE PERDU");
        return `
      <article class="reveal break-inside-avoid mb-6 rounded-xl border border-[--filet] bg-white/70 p-6 shadow-sm"
               style="--reveal-delay: ${(i % 3) * 90}ms">
        <p class="text-[0.68rem] font-semibold uppercase tracking-[0.18em] text-[--or]">
          ${esc((a.source || "").split(" (")[0])} · ${esc(window.dateFR(a.date_publication))}</p>
        <h4 class="mt-2 font-serif font-bold leading-snug">${esc(a.titre_article)}</h4>
        ${a.auteur ? `<p class="mt-1 text-xs text-[--encre-2]">par ${esc(a.auteur)}</p>` : ""}
        ${perdu
          ? `<p class="mt-4 text-sm italic text-gray-500 leading-relaxed">Article perdu en ligne&nbsp;:
             le journal a quitté le web et aucune archive n'a été retrouvée.
             Il est référencé ici pour que la trace ne s'efface pas deux fois.</p>`
          : `<blockquote class="mt-4 font-serif italic text-[0.95rem] leading-relaxed text-gray-700">
             ${a.extrait_citation.trimStart().startsWith("«")
               ? esc(a.extrait_citation)
               : `«&nbsp;${esc(a.extrait_citation)}&nbsp;»`}</blockquote>`}
        ${a.url_origine && !perdu
          ? `<a href="${esc(a.url_origine)}" target="_blank" rel="noopener"
               class="mt-4 inline-block text-xs text-[--foret] underline decoration-dotted underline-offset-2">source ↗</a>`
          : ""}
      </article>`;
      })
      .join("");
  };
})();
