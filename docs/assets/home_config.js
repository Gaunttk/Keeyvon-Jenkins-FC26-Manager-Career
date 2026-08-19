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

   HERO LAYOUT/FOCUS (lead only — see docs/assets/style.css's "Editorial hero"
   block and home.js's renderHero() for how these are consumed). Missing any
   of these is always safe: no `lead` composition fields at all renders as
   subject-center, 50%/50%, full default headline width — never broken.

   · layout: 'subject-right' | 'subject-left' | 'subject-center' (default
     when omitted or unrecognized).
     - subject-right: headline column on the left (~55-58% wide), photo
       subject sits toward the right, gradient darkest on the left fading
       through the middle and substantially clear over the subject.
     - subject-left: mirrored — headline on the right, subject left,
       gradient darkest on the right.
     - subject-center: for team celebrations / stadium / wide action scenes
       where the whole frame matters and there's no single off-center
       subject to protect. Wider lower text block (~62%), restrained
       bottom-only scrim, subject stays nearer center.
     Pick whichever matches the new hero photo's actual composition — don't
     force subject-right onto an image where the subject is on the left.

   Examples:
     lead: { layout: 'subject-right', focusX: '76%', focusY: '42%', ... }   // portrait, subject right
     lead: { layout: 'subject-left',  focusX: '25%', focusY: '45%', ... }   // portrait, subject left
     lead: { layout: 'subject-center', focusX: '50%', focusY: '45%', ... }  // team/action, centered

   · focusX / focusY: CSS object-position values (e.g. '76%', '38%') for the
     hero <img> — the subject's face/action point. IMPORTANT CAVEAT:
     object-fit: cover only gives real horizontal pan room when the source
     image is proportionally wider (relative to its height) than the hero
     box. A tall, centered portrait has ~zero horizontal crop slack in our
     landscape hero box, so focusX alone won't move the subject sideways for
     that shape — it matters far more for landscape action shots / group
     photos / stadium scenes. focusY reliably matters for any portrait.
     To actually reposition a subject within a tall portrait source, crop a
     hero-specific image (e.g. a "-hero.png" variant alongside the original)
     so the subject already sits at the desired horizontal fraction before
     it ever reaches object-fit: cover — see lead.image below for the
     current example. focusX/focusY still tune the result from there.
   · mobileFocusX / mobileFocusY: optional override of focusX/focusY used
     only in the ≤760px stacked mobile layout (see style.css), for when the
     desktop focal point produces a bad crop in the shorter 16:10 mobile
     box. Omit to just reuse focusX/focusY on mobile too.
   · headlineWidth: optional override of the copy column's width (e.g.
     '52%') if a layout's default (~55% for subject-right/left, ~62% for
     subject-center) doesn't suit a particular headline length. Rarely
     needed — natural wrapping handles most cases.
   These are presentation choices only — never put a stat or score here.
   ───────────────────────────────────────────────────────────────────────── */

const HOME_CONFIG = {

  /* ── Editorial hero ───────────────────────────────────────────────────── */
  lead: {
    articleId: '2026-12-20-hargreaves-greatest-promoted-seasons',
    /* A hero-specific crop of assets/photos/keeyvon-jenkins.png (used as-is
       elsewhere, e.g. the writer-card thumbnail) — cropped tighter so his
       face already sits ~74% across the frame before object-fit: cover
       ever touches it; see the focusX caveat above for why that's necessary
       for a tall portrait source. Do not repoint this at the original
       full-body portrait — it will re-center behind the headline. */
    image: 'assets/photos/keeyvon-jenkins-hero.png',
    imageAlt: 'Keeyvon Jenkins pitchside at the Racecourse',
    layout: 'subject-right',
    focusX: '74%',
    focusY: '48%'
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
  /* Fields mirror wrexham_squad.csv columns: Position, Age, Height, OVR.
     Season Goals/Assists/Avg Rating and the last-5-match sparkline are NOT
     set here — they're looked up at render time from
     assets/player_stats.js (scripts/sync_home_player_stats.py) by name, so
     they never go stale. */
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
