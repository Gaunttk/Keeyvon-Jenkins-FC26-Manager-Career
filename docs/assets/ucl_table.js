/* ─────────────────────────────────────────────────────────────────────────
   ucl_table.js — HAND-MAINTAINED UEFA Champions League league-phase
   standings, same philosophy as pl_table.js.

   HOW TO UPDATE: rebuild CHAMPIONS_LEAGUE_TABLE from a full 36-club
   standings screenshot (Office > Standings > League, scrolled top to
   bottom). Never guess a row — if a club's row isn't visible, leave it
   alone. `crest` paths are relative to docs/ and are only filled in where
   an exact asset already exists in assets/photos/crests/; clubs without
   one render name-only, which the renderer already handles gracefully.

   Lombardia FC (pos 11 as of MD2) is Inter Milan's in-game reskin (EA
   licensing) — shown here under its real identity/crest per the
   2027-09-14 session, same treatment as the Match Log. See CLAUDE.md-style
   convention in pl_table.js for the zone-marker format.
   ───────────────────────────────────────────────────────────────────────── */

const CHAMPIONS_LEAGUE_TABLE = {
  competition: 'UEFA Champions League',
  season: '2027/28',
  note: 'League Phase standings after Matchday 3, per the Office > Standings screen from the Slavia Praha (A) session (2027-10-20). Positions 15–36 are omitted this update — not visible in this session’s screenshots (the only MD3 shot covering that range was a pre-match broadcast graphic still showing MD2 totals, so it was not used here to avoid mixing matchdays). They’ll be filled back in once a post-MD3 screenshot covers that range.',
  markers: {
    1: { label: '→ Next Stage (Round of 16)', cls: 'promo' },
    9: { label: 'Knockout Play-offs', cls: 'playoff' },
    25: { label: 'Eliminated', cls: 'relegate' }
  },
  rows: [
    { pos:1, club:"Borussia Dortmund", crest:"assets/photos/crests/germany-bundesliga-2025-2026.football-logos.cc/256x256/borussia-dortmund.football-logos.cc.png", p:3, w:2, d:1, l:0, gf:8, ga:3, gd:5, pts:7, cls:"promo" },
    { pos:2, club:"FC Barcelona", crest:"", p:3, w:2, d:1, l:0, gf:6, ga:1, gd:5, pts:7, cls:"promo" },
    { pos:3, club:"FC Bayern München", crest:"assets/photos/crests/germany-bundesliga-2025-2026.football-logos.cc/256x256/bayern-munchen.football-logos.cc.png", p:3, w:2, d:1, l:0, gf:6, ga:2, gd:4, pts:7, cls:"promo" },
    { pos:4, club:"Arsenal", crest:"assets/photos/crests/english-premier-league-2026-2027.football-logos.cc/256x256/arsenal.football-logos.cc.png", p:3, w:2, d:1, l:0, gf:6, ga:2, gd:4, pts:7, cls:"promo" },
    { pos:5, club:"Real Madrid", crest:"", p:3, w:2, d:1, l:0, gf:7, ga:4, gd:3, pts:7, cls:"promo" },
    { pos:6, club:"Milano FC", crest:"", p:3, w:2, d:1, l:0, gf:7, ga:4, gd:3, pts:7, cls:"promo" },
    { pos:7, club:"AEK Athens", crest:"", p:3, w:2, d:1, l:0, gf:6, ga:3, gd:3, pts:7, cls:"promo" },
    { pos:8, club:"Wrexham", crest:"assets/photos/crests/wrexham-crest.png", p:3, w:2, d:1, l:0, gf:5, ga:2, gd:3, pts:7, cls:"promo", wrexham:true },
    { pos:9, club:"Feyenoord", crest:"assets/photos/crests/netherlands-eredivisie-2025-2026.football-logos.cc/256x256/feyenoord.football-logos.cc.png", p:3, w:2, d:1, l:0, gf:5, ga:2, gd:3, pts:7, cls:"playoff" },
    { pos:10, club:"Manchester City", crest:"assets/photos/crests/english-premier-league-2026-2027.football-logos.cc/256x256/manchester-city.football-logos.cc.png", p:3, w:2, d:1, l:0, gf:6, ga:4, gd:2, pts:7, cls:"playoff" },
    { pos:11, club:"Galatasaray", crest:"assets/photos/crests/turkey-super-lig-2025-2026.football-logos.cc/256x256/galatasaray.football-logos.cc.png", p:3, w:2, d:1, l:0, gf:6, ga:4, gd:2, pts:7, cls:"playoff" },
    { pos:12, club:"Athletic Club", crest:"", p:3, w:2, d:0, l:1, gf:5, ga:2, gd:3, pts:6, cls:"playoff" },
    { pos:13, club:"F.C. København", crest:"", p:3, w:2, d:0, l:1, gf:6, ga:4, gd:2, pts:6, cls:"playoff" },
    { pos:14, club:"Atlético de Madrid", crest:"", p:3, w:2, d:0, l:1, gf:5, ga:3, gd:2, pts:6, cls:"playoff" }
  ]
};
