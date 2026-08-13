/* ─────────────────────────────────────────────────────────────────────────
   home_config.js — the ONLY hand-curated part of the homepage.

   Everything on docs/index.html that is a football *fact* comes from a
   generated/structured source:
     · SEASON_SUMMARY (inline in index.html) ← scripts/sync_season_summary.py
     · MEDIA_INDEX    (assets/media_index.js) ← scripts/generate_media_pages.py
     · PREMIER_LEAGUE_TABLE (assets/pl_table.js) ← hand-maintained standings
     · wrexham_squad.csv / youth_academy.csv → the player blocks below

   This file only stores EDITORIAL CHOICES: which article leads, which player
   is spotlighted, which photo sits behind the hero. It must never hold a
   mutable stat (points, goals, league position, form) — those would go stale
   silently. Player entries here carry only slow-moving CSV facts (position,
   age, height, OVR, squad role); refresh them when the CSV changes.

   HOW TO UPDATE EACH SESSION (optional — nothing breaks if you don't):
   · lead / supporting / writers: article ids straight out of
     media-articles.json. Any id in there works; run
     `python3 scripts/generate_media_pages.py` first if you just added one.
   · images: paths under docs/assets/photos/. Prefer the approved portraits
     over raw md*-* match screenshots for anything public-facing.
   · spotlight / academy: names must match wrexham_squad.csv / youth_academy.csv.
   ───────────────────────────────────────────────────────────────────────── */

const HOME_CONFIG = {

  /* ── Editorial hero ───────────────────────────────────────────────────── */
  lead: {
    articleId: '2026-12-20-hargreaves-greatest-promoted-seasons',
    image: 'assets/photos/keeyvon-touchline.png',
    imageAlt: 'Keeyvon Jenkins on the touchline'
  },

  /* Three supporting stories stacked beside the lead. */
  supporting: [
    { articleId: 'entry-arsenal-away-pl-2', image: 'assets/photos/leo_sauer.png', imageAlt: 'Leo Sauer' },
    { articleId: 'entry-bournemouth-yrt-final', image: 'assets/photos/faure.png', imageAlt: 'Lilian Faure' },
    { articleId: 'entry-sunderland-away-pl', image: 'assets/photos/rio_ngumoha.png', imageAlt: 'Rio Ngumoha' }
  ],

  /* ── From Our Writers ─────────────────────────────────────────────────── */
  /* The card whose author is Keeyvon Jenkins renders in the Hawk's Nest
     treatment automatically — no flag needed. */
  writers: [
    { articleId: 'entry-transferwindow-aug31', image: 'assets/photos/arthur_okonkwo.png', imageAlt: 'Arthur Okonkwo' },
    { articleId: 'entry-blackburn-facup-r5', image: 'assets/photos/yacel_amrizi.png', imageAlt: 'Yacel Amrizi' },
    { articleId: 'entry-101', image: 'assets/photos/keeyvon-jenkins.png', imageAlt: 'Keeyvon Jenkins' }
  ],

  /* ── Squad Spotlight ──────────────────────────────────────────────────── */
  /* Fields mirror wrexham_squad.csv columns: Position, Age, Height, OVR,
     Squad_Role. No season stats here on purpose — per-player goals/assists
     are not machine-readable in this repo, so the card links to season.html
     rather than restating numbers that could drift. */
  spotlight: {
    featured: {
      name: 'Yacel Amrizi', position: 'ST / LW', age: 21, height: '6\'2"',
      ovr: 74, role: 'Important',
      image: 'assets/photos/yacel_amrizi.png'
    },
    others: [
      { name: 'Toni Fruk', position: 'ST / CAM', age: 25, ovr: 79, image: 'assets/photos/toni_fruk.png' },
      { name: 'Rio Ngumoha', position: 'LM / LW', age: 17, ovr: 76, image: 'assets/photos/rio_ngumoha.png' },
      { name: 'Leo Sauer', position: 'LW / LM', age: 20, ovr: 76, image: 'assets/photos/leo_sauer.png' },
      { name: 'Arthur Okonkwo', position: 'GK', age: 24, ovr: 74, image: 'assets/photos/arthur_okonkwo.png' }
    ]
  },

  /* ── Academy / Next Generation ────────────────────────────────────────── */
  /* Fields mirror youth_academy.csv. `nationality` is the country recorded at
     the head of that player's Notes column — nothing inferred. */
  academy: {
    featured: {
      name: 'Lilian Faure', position: 'RM', age: 17, ovr: 63, potential: '70-90',
      nationality: 'France',
      image: 'assets/photos/faure.png'
    },
    others: [
      { name: 'Matthieu Brunel', position: 'ST', age: 17, ovr: 63, potential: '67-91', image: 'assets/photos/brunel.png' },
      { name: 'Fabricio Sandoval', position: 'CAM', age: 17, ovr: 62, potential: '74-80', image: 'assets/photos/sandoval.png' },
      { name: 'Ben Forster', position: 'CM', age: 15, ovr: 60, potential: '79-85', image: 'assets/photos/forster.png' }
    ]
  }
};
