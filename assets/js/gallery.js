// gallery.js — Galerie photo (VII) : photos réelles avec certificat SHA-256,
// cartes « trace d'archive » pour les images perdues en ligne,
// et emplacement réservé aux archives familiales (rang 12).
(function () {
  "use strict";

  const esc = (s) =>
    String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

  // Explications en langue claire pour les images perdues (le détail technique
  // reste dans data/photos_catalog.json, champ note_harvest).
  const RAISONS = {
    4: "L'article commémoratif de 2019 a disparu avec l'ancien site du journal, et aucune archive n'en conserve de copie. Les archives papier de La Nation restent la piste la plus sûre.",
    5: "Le journal qui publiait ce portrait a disparu du web. Son texte intégral a pu être sauvé, mais la photographie n'y figurait pas.",
    6: "Le site qui accueillait cette interview n'existe plus, et aucune archive n'en a gardé trace.",
    9: "Aucune reproduction de cette couverture n'existe en ligne. La numérisation d'un exemplaire du livre permettrait de la restituer.",
    10: "Le récit des obsèques a été retrouvé dans les archives du web, mais sa photographie n'y a jamais été enregistrée.",
    11: "Des clichés de la campagne de 2006 existent dans les fonds des agences de presse. Leur licence reste à acquérir.",
  };
  const CREDITS_COURTS = {
    4: "La Nation Bénin",
    5: "La Tribune de la Capitale",
    6: "Hub Rural",
    9: "Éditions du Flamboyant",
    10: "24 Heures au Bénin",
    11: "Getty Images / AFP",
  };

  function cartePhoto(p) {
    return `
    <figure class="photo-carte reveal group relative overflow-hidden rounded-xl border border-[--filet] bg-white shadow-sm"
            tabindex="0" role="button" aria-label="Agrandir : ${esc(p.description_alt)}"
            data-rang="${p.rang}">
      <div class="overflow-hidden">
        <img src="${esc(p.fichier_local.replace(/^assets\//, "assets/"))}" alt="${esc(p.description_alt)}"
             loading="lazy" class="w-full h-56 object-cover object-top">
      </div>
      <figcaption class="p-4">
        <p class="text-sm leading-snug">${esc(p.description_alt)}</p>
        <p class="mt-2 text-xs text-[--encre-2]">${esc(p.credit)}</p>
        <p class="mt-2 text-[0.68rem] font-medium text-[--foret]" title="Empreinte SHA-256 : ${esc(p.sha256)}">
          ✓ Photographie authentifiée</p>
      </figcaption>
    </figure>`;
  }

  function carteTrace(p) {
    return `
    <figure class="trace-carte reveal rounded-xl p-5 flex flex-col justify-between min-h-[14rem]">
      <div>
        <span class="tampon">Trace d'archive</span>
        <p class="mt-4 font-serif text-[1.05rem] leading-snug">${esc(p.description_alt)}</p>
      </div>
      <figcaption class="mt-4">
        <p class="text-xs leading-relaxed text-[--encre-2]">${esc(RAISONS[p.rang] || "Image encore à retrouver.")}</p>
        <p class="mt-2 text-[0.68rem] uppercase tracking-wider text-gray-400">${esc(CREDITS_COURTS[p.rang] || p.credit)}</p>
      </figcaption>
    </figure>`;
  }

  function carteFamille() {
    return `
    <figure class="cadre-famille reveal rounded-xl p-8 sm:col-span-2 lg:col-span-3 text-center">
      <p class="font-serif italic text-xl md:text-2xl text-[--foret] text-balance">
        Cet emplacement attend la photographie que seule une famille peut offrir.</p>
      <p class="mt-4 max-w-xl mx-auto text-sm text-[--encre-2] leading-relaxed">
        Le portrait de référence du mémorial, choisi par les siens. Un exemplaire libre de droits
        pourra aussi être versé sur Wikimedia Commons&nbsp;: la page Wikipédia consacrée à
        Richard Adjaho n'a aujourd'hui aucune photographie.</p>
      <p class="mt-5 text-[0.68rem] uppercase tracking-[0.25em] text-[--or]">Réservé aux archives de la famille Adjaho</p>
    </figure>`;
  }

  // ---------- Lightbox ----------
  function ouvrirLightbox(p) {
    const dlg = document.getElementById("lightbox");
    dlg.querySelector("img").src = p.fichier_local;
    dlg.querySelector("img").alt = p.description_alt;
    dlg.querySelector(".lb-desc").textContent = p.description_alt;
    dlg.querySelector(".lb-credit").textContent = p.credit;
    dlg.querySelector(".lb-sha").textContent = "Empreinte SHA-256 : " + p.sha256;
    dlg.showModal();
  }

  window.rendreGalerie = function (conteneur) {
    const photos = window.PHOTOS.photos;
    const reelles = photos.filter((p) => p.fichier_local);
    const perdues = photos.filter((p) => !p.fichier_local && p.statut !== "archives_familiales");
    const famille = photos.find((p) => p.statut === "archives_familiales");

    conteneur.innerHTML = `
      <div class="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        ${reelles.map(cartePhoto).join("")}
        ${perdues.map(carteTrace).join("")}
        ${famille ? carteFamille() : ""}
      </div>`;

    conteneur.querySelectorAll(".photo-carte").forEach((el) => {
      const p = photos.find((x) => x.rang === Number(el.dataset.rang));
      const ouvrir = () => ouvrirLightbox(p);
      el.addEventListener("click", ouvrir);
      el.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") { e.preventDefault(); ouvrir(); }
      });
    });

    const dlg = document.getElementById("lightbox");
    dlg.addEventListener("click", (e) => { if (e.target === dlg) dlg.close(); });
  };
})();
