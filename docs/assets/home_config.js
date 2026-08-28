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

   HOW TO UPDATE EACH SESSION (required — see CLAUDE.md's "Match Submission
   Checklist" and "End-of-Session Page Sync Check"; nothing errors if you
   skip it, but the homepage silently goes stale, which is exactly what
   happened for months before this was made a checklist item):
   · lead / supporting / writers: article ids straight out of
     media-articles.json. Any id in there works; run
     `python3 scripts/generate_media_pages.py` first if you just added one.
   · images: paths under docs/assets/photos/. Prefer the approved portraits
     over raw md*-* match screenshots for anything public-facing.
   · spotlight / academy: names must match wrexham_squad.csv / youth_academy.csv.

   HERO LAYOUT/FOCUS (lead only — see docs/assets/style.css's "Editorial hero"
   block and home.js's renderHero() for how these are consumed):
   · layout: 'subject-right' (default) | 'subject-left' | 'wide'.
     - subject-right: headline column on the left (~55-58% wide), photo
       subject sits toward the right, gradient darkest on the left.
     - subject-left: mirrored — headline on the right, subject left,
       gradient darkest on the right.
     - wide: for team celebrations / stadium scenes where the whole frame
       matters. Wider lower-left text block, subject stays nearer center.
     Pick whichever matches the new hero photo's actual composition — don't
     force subject-right onto an image where the subject is on the left.
   · focusX / focusY: CSS object-position values (e.g. '76%', '38%') for the
     hero <img>. Aim it at the subject's face/action point. Note: object-fit
     cover only gives real horizontal pan room when the image is wider
     (relative to its height) than the hero box — a tall, centered portrait
     like the current Jenkins photo has ~zero horizontal crop slack in a
     landscape hero box, so focusX will do little for that specific shape;
     it matters far more for landscape action shots / group photos / stadium
     scenes. focusY is the one that reliably matters for any portrait.
   · headlineWidth: optional override of the copy column's width (e.g.
     '52%') if a layout's default (~55% for subject-right/left, ~62% for
     wide) doesn't suit a particular headline length. Rarely needed —
     natural wrapping handles most cases.
   These are presentation choices only — never put a stat or score here.
   ───────────────────────────────────────────────────────────────────────── */

const HOME_CONFIG = {

  /* ── Editorial hero ───────────────────────────────────────────────────── */
  lead: {
    articleId: '2027-05-23-hargreaves-pl-champions',
    image: 'assets/photos/md38-leeds-pl-trophy.jpg',
    imageAlt: 'Wrexham players celebrate with the Premier League trophy at the Racecourse Ground',
    layout: 'wide',
    focusX: '50%',
    focusY: '45%'
  },

  /* Three supporting stories stacked beside the lead. */
  supporting: [
    { articleId: '2027-08-25-meredith-tine-signing', image: 'assets/photos/wrexham-crest.png', imageAlt: 'Wrexham AFC crest' },
    { articleId: '2027-08-07-meredith-community-shield-man-city', image: 'assets/photos/wrexham-crest.png', imageAlt: 'Wrexham AFC crest' },
    { articleId: '2027-05-15-hargreaves-first-trophy', image: 'assets/photos/toni_fruk.png', imageAlt: 'Toni Fruk' }
  ],

  /* ── From Our Writers ─────────────────────────────────────────────────── */
  /* The card whose author is Keeyvon Jenkins renders in the Hawk's Nest
     treatment automatically — no flag needed. */
  writers: [
    { articleId: 'entry-001', image: 'assets/photos/keeyvon-jenkins.png', imageAlt: 'Keeyvon Jenkins' },
    { articleId: '2027-05-23-bennett-jenkins-american-champion', image: 'assets/photos/keeyvon-touchline.png', imageAlt: 'Keeyvon Jenkins on the touchline' },
    { articleId: '2027-05-23-cole-title-debate', image: 'assets/photos/damian_bobadilla.png', imageAlt: 'Damián Bobadilla' }
  ],

  /* ── Squad Spotlight ──────────────────────────────────────────────────── */
  /* Fields mirror wrexham_squad.csv columns: Position, Age, Height, OVR.
     Season Goals/Assists/Avg Rating and the last-5-match sparkline are NOT
     set here — they're looked up at render time from
     assets/player_stats.js (scripts/sync_home_player_stats.py) by name, so
     they never go stale. */
  spotlight: {
    featured: {
      name: 'Yacel Amrizi', position: 'ST / LW', age: 23, height: '6\'2"',
      ovr: 76, role: 'Important',
      image: 'assets/photos/yacel_amrizi.png'
    },
    others: [
      { name: 'Toni Fruk', position: 'ST / CAM / CM', age: 26, ovr: 81, image: 'assets/photos/toni_fruk.png' },
      { name: 'Rio Ngumoha', position: 'LM / LW', age: 18, ovr: 79, image: 'assets/photos/rio_ngumoha.png' },
      { name: 'Leo Sauer', position: 'LW / LM', age: 21, ovr: 80, image: 'assets/photos/leo_sauer.png' },
      { name: 'Arthur Okonkwo', position: 'GK', age: 25, ovr: 76, image: 'assets/photos/arthur_okonkwo.png' }
    ]
  },

  /* ── Academy / Next Generation ────────────────────────────────────────── */
  /* Fields mirror youth_academy.csv. `nationality` is the country recorded at
     the head of that player's Notes column — nothing inferred. */
  academy: {
    featured: {
      name: 'Jules Collin', position: 'RW', age: 17, ovr: 62, potential: '81-87',
      nationality: 'France',
      image: 'assets/photos/collin.png'
    },
    others: [
      { name: 'Victor Cardoso', position: 'RB', age: 14, ovr: 50, potential: '77-85', image: 'assets/photos/cardoso.png' },
      { name: 'Stephane Bertrand', position: 'RW', age: 16, ovr: 60, potential: '91-94', image: 'assets/photos/bertrand.png' },
      { name: 'Ben Forster', position: 'CM', age: 16, ovr: 62, potential: '79-85', image: 'assets/photos/forster.png' }
    ]
  }
};
