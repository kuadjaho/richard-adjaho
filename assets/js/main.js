// main.js — Orchestration : rendu des sections, bibliothèque, chiffres,
// données ouvertes, IntersectionObserver et barre de lecture.
(function () {
  "use strict";

  const esc = (s) =>
    String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

  // ---------- II. En chiffres ----------
  function rendreChiffres(conteneur) {
    const h = window.HERITAGE;
    const pages = h.bibliographie.reduce((n, o) => n + (o.pages || 0), 0);
    const tuiles = [
      { valeur: "40", unite: "ans", label: "de vie publique, de 1968 à 2009" },
      { valeur: String(h.chronologie_carriere.length), unite: "", label: "périodes d'une vie d'État" },
      { valeur: String(h.bibliographie.length), unite: "", label: "ouvrages publiés à Cotonou" },
      { valeur: String(pages), unite: "", label: "pages écrites sur les finances publiques et la décentralisation" },
      { valeur: "3", unite: "", label: "corps d'inspection, jusqu'à Inspecteur général des Finances" },
      { valeur: "n° 24", unite: "/ 26", label: "sur le bulletin de la présidentielle de 2006" },
    ];
    conteneur.innerHTML = tuiles
      .map(
        (t, i) => `
      <div class="reveal text-center md:text-left" style="--reveal-delay: ${i * 70}ms">
        <p class="text-3xl md:text-4xl font-semibold text-[--foret]" style="font-variant-numeric: proportional-nums">
          ${esc(t.valeur)}<span class="text-lg text-[--or] ml-1">${esc(t.unite)}</span></p>
        <p class="mt-1 text-xs text-[--encre-2] leading-snug">${esc(t.label)}</p>
      </div>`
      )
      .join("");
  }

  // ---------- VI. La Bibliothèque ----------
  function rendreBibliotheque(conteneur) {
    // Couvertures réelles disponibles (catalogue photos rangs 3 et 8)
    const couvs = {};
    for (const p of window.PHOTOS.photos) {
      if (!p.fichier_local) continue;
      if (p.description_alt.includes("Bonne gouvernance")) couvs["Bonne gouvernance au Bénin : ma contribution"] = p.fichier_local;
      if (p.description_alt.includes("Décentralisation au Bénin, en Afrique")) couvs["Décentralisation au Bénin, en Afrique et ailleurs dans le monde : État sommaire et enjeux"] = p.fichier_local;
    }

    conteneur.innerHTML = window.HERITAGE.bibliographie
      .map((o, i) => {
        const src = couvs[o.titre];
        const couverture = src
          ? window.pictureHTML(src, "Couverture de " + o.titre, "couv-reelle w-full", 'loading="lazy"')
          : `<div class="couv-typo" role="img" aria-label="Couverture typographique reconstituée : ${esc(o.titre)}">
               <p class="text-[0.6rem] uppercase tracking-widest text-[--encre-2]">Richard Adjaho</p>
               <p class="couv-titre">${esc(o.titre.split(":")[0])}</p>
               <p class="text-[0.55rem] text-[--encre-2]">${esc(o.editeur)}<br>${esc(o.annee)}</p>
             </div>`;
        return `
      <article class="reveal grid grid-cols-[7rem_1fr] gap-5 items-start" style="--reveal-delay: ${(i % 3) * 90}ms">
        <div>${couverture}</div>
        <div>
          <p class="text-xs font-semibold text-[--or]">${esc(o.annee)}</p>
          <h4 class="mt-1 font-serif font-bold leading-snug">${esc(o.titre)}</h4>
          <p class="mt-1 text-xs text-[--encre-2]">${esc(o.editeur)}${o.lieu ? ", " + esc(o.lieu) : ""} · ${o.pages || "?"} p.${o.isbn ? " · ISBN " + esc(o.isbn) : ""}${o.co_auteur ? " · avec " + esc(o.co_auteur) : ""}</p>
          <p class="mt-3 text-sm leading-relaxed text-gray-600">${esc(o.resume_analytique.split(" NB :")[0])}</p>
          <p class="mt-3 flex flex-wrap gap-1.5">
            ${o.piliers_gouvernance.map((p) => `<span class="text-[0.62rem] font-medium px-2 py-0.5 rounded-full bg-[--sable] text-[--foret]">${esc(p)}</span>`).join("")}</p>
        </div>
      </article>`;
      })
      .join("");
  }

  // ---------- VIII. Données ouvertes ----------
  function rendreDonnees() {
    const pre = document.getElementById("json-brut");
    pre.textContent = JSON.stringify(window.HERITAGE, null, 2);

    const notes = document.getElementById("notes-methodo");
    notes.innerHTML = window.HERITAGE.notes_methodologiques
      .map((n) => `<li class="text-sm leading-relaxed text-gray-600">${esc(n)}</li>`)
      .join("");

    document.getElementById("btn-copier").addEventListener("click", async (e) => {
      await navigator.clipboard.writeText(JSON.stringify(window.HERITAGE, null, 2));
      e.target.textContent = "Copié ✓";
      setTimeout(() => (e.target.textContent = "Copier le JSON"), 2000);
    });
    const telecharger = (nom, objet) => {
      const a = document.createElement("a");
      a.href = URL.createObjectURL(new Blob([JSON.stringify(objet, null, 2)], { type: "application/json" }));
      a.download = nom;
      a.click();
      URL.revokeObjectURL(a.href);
    };
    document.getElementById("btn-dl-heritage").addEventListener("click", () =>
      telecharger("richard_adjaho_heritage.json", window.HERITAGE));
    document.getElementById("btn-dl-photos").addEventListener("click", () =>
      telecharger("photos_catalog.json", window.PHOTOS));
  }

  // ---------- Révélation au défilement ----------
  function observerReveals() {
    const reduits = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const cibles = [...document.querySelectorAll(".reveal")];
    const reveler = (el) => el.classList.add("est-visible");

    if (reduits || !("IntersectionObserver" in window)) {
      cibles.forEach(reveler);
      return;
    }

    // 1. Tout ce qui est déjà dans le viewport apparaît immédiatement,
    //    sans délai en cascade (pas d'écran vide au chargement).
    for (const el of cibles) {
      const r = el.getBoundingClientRect();
      if (r.top < window.innerHeight && r.bottom > 0) {
        el.style.setProperty("--reveal-delay", "0ms");
        reveler(el);
      }
    }

    const obs = new IntersectionObserver(
      (entrees) => {
        for (const e of entrees) {
          if (e.isIntersecting) {
            reveler(e.target);
            obs.unobserve(e.target);
          }
        }
      },
      { rootMargin: "0px 0px -10% 0px", threshold: 0.05 }
    );
    cibles.forEach((el) => { if (!el.classList.contains("est-visible")) obs.observe(el); });

    // 2. Saut d'ancre : la section visée se révèle instantanément,
    //    sans attendre la fin du défilement doux.
    const revelerCible = (hash) => {
      if (!hash || hash === "#") return;
      const section = document.querySelector(hash);
      if (!section) return;
      section.querySelectorAll(".reveal").forEach((el) => {
        el.style.setProperty("--reveal-delay", "0ms");
        reveler(el);
      });
    };
    document.querySelectorAll('a[href^="#"]').forEach((a) =>
      a.addEventListener("click", () => revelerCible(a.getAttribute("href"))));
    window.addEventListener("hashchange", () => revelerCible(location.hash));
    if (location.hash) revelerCible(location.hash);
  }

  // ---------- Barre de progression de lecture ----------
  function barreLecture() {
    const barre = document.querySelector(".barre-lecture");
    const maj = () => {
      const h = document.documentElement;
      const pct = (h.scrollTop / (h.scrollHeight - h.clientHeight)) * 100;
      barre.style.width = pct + "%";
    };
    document.addEventListener("scroll", maj, { passive: true });
    maj();
  }

  // ---------- Démarrage ----------
  document.addEventListener("DOMContentLoaded", () => {
    rendreChiffres(document.getElementById("chiffres"));
    window.rendreTimeline(document.getElementById("chronologie-conteneur"));
    window.rendreTemoin(document.getElementById("temoin-conteneur"));
    window.rendreHommages(document.getElementById("hommages-conteneur"));
    rendreBibliotheque(document.getElementById("bibliotheque-conteneur"));
    window.rendreGalerie(document.getElementById("galerie-conteneur"));
    rendreDonnees();
    observerReveals();
    barreLecture();
  });
})();
