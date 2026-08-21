/* squad_config.js — the ONLY hand-curated part of the Squad landing page.
   Same philosophy as home_config.js: editorial/presentation choices only
   (which photo anchors the hero, its focal point, the short intro copy).
   Never put a mutable football fact here — those live in
   docs/assets/squad_data.js (scripts/sync_squad_page.py) and are read at
   render time by docs/assets/squad.js. */
const SQUAD_CONFIG = {
  hero: {
    image: 'assets/photos/aston-villa-fa-cup-pub.jpeg',
    imageAlt: 'Wrexham supporters celebrating a cup run',
    focusX: '50%',
    focusY: '40%',
    caption: 'Wrexham AFC supporters watching on as Jenkins’ side chase silverware.'
  },
  intro: 'This is the group Keeyvon Jenkins has built for a first season in the ' +
    'Premier League — a first-team spine forged through three promotions, ' +
    'reinforced by senior signings and academy graduates alike. Below: who’s ' +
    'in the squad, who’s carrying it right now, and how it’s trending across ' +
    'the season.'
};
