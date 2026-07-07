// gallery.js — Galerie photo (VII) : photos réelles avec certificat SHA-256,
// cartes « trace d'archive » pour les images perdues en ligne,
// et emplacement réservé aux archives familiales (rang 12).
(function () {
  "use strict";

  const esc = (s) =>
    String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

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
        <p class="mt-2 font-mono text-[0.62rem] text-gray-400" title="Empreinte SHA-256 complète : ${esc(p.sha256)}">
          <span class="text-[--foret]">✓ authentifiée</span> · sha-256 ${esc((p.sha256 || "").slice(0, 16))}…</p>
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
        <p class="text-xs leading-relaxed text-[--encre-2]">${esc(p.note_harvest || "Image à retrouver.")}</p>
        <p class="mt-2 text-[0.68rem] uppercase tracking-wider text-gray-400">${esc(p.credit)}</p>
      </figcaption>
    </figure>`;
  }

  function carteFamille(p) {
    return `
    <figure class="cadre-famille reveal rounded-xl p-8 sm:col-span-2 lg:col-span-3 text-center">
      <p class="font-serif italic text-xl md:text-2xl text-[--foret] text-balance">
        Cet emplacement attend la photographie que seule une famille peut offrir.</p>
      <p class="mt-4 max-w-xl mx-auto text-sm text-[--encre-2] leading-relaxed">
        ${esc(p.description_alt)}. ${esc(p.credit)}</p>
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
    dlg.querySelector(".lb-sha").textContent = "SHA-256 : " + p.sha256;
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
        ${famille ? carteFamille(famille) : ""}
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
