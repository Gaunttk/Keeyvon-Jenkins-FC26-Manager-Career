/* ─────────────────────────────────────────────────────────────────────────
   ucl_table.js — HAND-MAINTAINED UEFA Champions League league-phase
   standings, same philosophy as pl_table.js.

   HOW TO UPDATE: rebuild CHAMPIONS_LEAGUE_TABLE from a full 36-club
   standings screenshot (Office > Standings > League, scrolled top to
   bottom). Never guess a row — if a club's row isn't visible, leave it
   alone. `crest` paths are relative to docs/ and are only filled in where
   an exact asset already exists in assets/photos/crests/; clubs without
   one render name-only, which the renderer already handles gracefully.

   Lombardia FC (pos 11) is Inter Milan's in-game reskin (EA licensing) —
   shown here under its real identity/crest per the 2027-09-14 session,
   same treatment as the Match Log. See CLAUDE.md-style convention in
   pl_table.js for the zone-marker format.
   ───────────────────────────────────────────────────────────────────────── */

const CHAMPIONS_LEAGUE_TABLE = {
  competition: 'UEFA Champions League',
  season: '2027/28',
  note: 'League Phase standings after Matchday 1, per full-standings screenshots from the Inter Milan (A) session (2027-09-14). Several clubs still show 0 played — Matchday 1 is staggered across multiple match days and not every club had played yet at the time of this screenshot.',
  markers: {
    1: { label: '→ Next Stage (Round of 16)', cls: 'promo' },
    9: { label: 'Knockout Play-offs', cls: 'playoff' },
    25: { label: 'Eliminated', cls: 'relegate' }
  },
  rows: [
    { pos:1, club:"F.C. København", crest:"", p:1, w:1, d:0, l:0, gf:3, ga:1, gd:2, pts:3, cls:"promo" },
    { pos:2, club:"FC Bayern München", crest:"assets/photos/crests/germany-bundesliga-2025-2026.football-logos.cc/256x256/bayern-munchen.football-logos.cc.png", p:1, w:1, d:0, l:0, gf:2, ga:0, gd:2, pts:3, cls:"promo" },
    { pos:3, club:"Athletic Club", crest:"", p:1, w:1, d:0, l:0, gf:2, ga:0, gd:2, pts:3, cls:"promo" },
    { pos:4, club:"Milano FC", crest:"", p:1, w:1, d:0, l:0, gf:3, ga:2, gd:1, pts:3, cls:"promo" },
    { pos:5, club:"Manchester City", crest:"assets/photos/crests/english-premier-league-2026-2027.football-logos.cc/256x256/manchester-city.football-logos.cc.png", p:1, w:1, d:0, l:0, gf:2, ga:1, gd:1, pts:3, cls:"promo" },
    { pos:6, club:"Atlético de Madrid", crest:"", p:1, w:1, d:0, l:0, gf:2, ga:1, gd:1, pts:3, cls:"promo" },
    { pos:7, club:"SK Brann", crest:"", p:1, w:0, d:1, l:0, gf:3, ga:3, gd:0, pts:1, cls:"promo" },
    { pos:8, club:"Galatasaray", crest:"assets/photos/crests/turkey-super-lig-2025-2026.football-logos.cc/256x256/galatasaray.football-logos.cc.png", p:1, w:0, d:1, l:0, gf:3, ga:3, gd:0, pts:1, cls:"promo" },
    { pos:9, club:"Arsenal", crest:"assets/photos/crests/english-premier-league-2026-2027.football-logos.cc/256x256/arsenal.football-logos.cc.png", p:1, w:0, d:1, l:0, gf:1, ga:1, gd:0, pts:1, cls:"playoff" },
    { pos:10, club:"Como", crest:"", p:1, w:0, d:1, l:0, gf:1, ga:1, gd:0, pts:1, cls:"playoff" },
    { pos:11, club:"Inter Milan", crest:"assets/photos/crests/italy-serie-a-2025-2026.football-logos.cc/256x256/inter.football-logos.cc.png", p:1, w:0, d:1, l:0, gf:0, ga:0, gd:0, pts:1, cls:"playoff", note:"Shown in-game as “Lombardia FC”" },
    { pos:12, club:"Wrexham", crest:"assets/photos/crests/wrexham-crest.png", p:1, w:0, d:1, l:0, gf:0, ga:0, gd:0, pts:1, cls:"playoff", wrexham:true },
    { pos:13, club:"Real Madrid", crest:"", p:0, w:0, d:0, l:0, gf:0, ga:0, gd:0, pts:0, cls:"playoff" },
    { pos:14, club:"FC Barcelona", crest:"", p:0, w:0, d:0, l:0, gf:0, ga:0, gd:0, pts:0, cls:"playoff" },
    { pos:15, club:"FC Porto", crest:"assets/photos/crests/portugal-primeira-liga-2025-2026.football-logos.cc/256x256/fc-porto.football-logos.cc.png", p:0, w:0, d:0, l:0, gf:0, ga:0, gd:0, pts:0, cls:"playoff" },
    { pos:16, club:"Borussia Dortmund", crest:"assets/photos/crests/germany-bundesliga-2025-2026.football-logos.cc/256x256/borussia-dortmund.football-logos.cc.png", p:0, w:0, d:0, l:0, gf:0, ga:0, gd:0, pts:0, cls:"playoff" },
    { pos:17, club:"Club Brugge", crest:"assets/photos/crests/belgium-pro-league-2025-2026.football-logos.cc/256x256/club-brugge.football-logos.cc.png", p:0, w:0, d:0, l:0, gf:0, ga:0, gd:0, pts:0, cls:"playoff" },
    { pos:18, club:"Juventus", crest:"assets/photos/crests/italy-serie-a-2025-2026.football-logos.cc/256x256/juventus.football-logos.cc.png", p:0, w:0, d:0, l:0, gf:0, ga:0, gd:0, pts:0, cls:"playoff" },
    { pos:19, club:"Frankfurt", crest:"assets/photos/crests/germany-bundesliga-2025-2026.football-logos.cc/256x256/eintracht-frankfurt.football-logos.cc.png", p:0, w:0, d:0, l:0, gf:0, ga:0, gd:0, pts:0, cls:"playoff" },
    { pos:20, club:"Feyenoord", crest:"assets/photos/crests/netherlands-eredivisie-2025-2026.football-logos.cc/256x256/feyenoord.football-logos.cc.png", p:0, w:0, d:0, l:0, gf:0, ga:0, gd:0, pts:0, cls:"playoff" },
    { pos:21, club:"AEK Athens", crest:"", p:0, w:0, d:0, l:0, gf:0, ga:0, gd:0, pts:0, cls:"playoff" },
    { pos:22, club:"Slavia Praha", crest:"", p:0, w:0, d:0, l:0, gf:0, ga:0, gd:0, pts:0, cls:"playoff" },
    { pos:23, club:"PSV", crest:"assets/photos/crests/netherlands-eredivisie-2025-2026.football-logos.cc/256x256/psv.football-logos.cc.png", p:0, w:0, d:0, l:0, gf:0, ga:0, gd:0, pts:0, cls:"playoff" },
    { pos:24, club:"RB Leipzig", crest:"assets/photos/crests/germany-bundesliga-2025-2026.football-logos.cc/256x256/rb-leipzig.football-logos.cc.png", p:0, w:0, d:0, l:0, gf:0, ga:0, gd:0, pts:0, cls:"playoff" },
    { pos:25, club:"Olympiacos FC", crest:"", p:0, w:0, d:0, l:0, gf:0, ga:0, gd:0, pts:0, cls:"relegate" },
    { pos:26, club:"Man Utd", crest:"assets/photos/crests/english-premier-league-2026-2027.football-logos.cc/256x256/manchester-united.football-logos.cc.png", p:0, w:0, d:0, l:0, gf:0, ga:0, gd:0, pts:0, cls:"relegate" },
    { pos:27, club:"Dynamo Kyiv", crest:"", p:0, w:0, d:0, l:0, gf:0, ga:0, gd:0, pts:0, cls:"relegate" },
    { pos:28, club:"FC Basel 1893", crest:"", p:0, w:0, d:0, l:0, gf:0, ga:0, gd:0, pts:0, cls:"relegate" },
    { pos:29, club:"Stade Rennais FC", crest:"assets/photos/crests/france-ligue-1-2025-2026.football-logos.cc/256x256/rennes.football-logos.cc.png", p:0, w:0, d:0, l:0, gf:0, ga:0, gd:0, pts:0, cls:"relegate" },
    { pos:30, club:"Legia Warszawa", crest:"", p:0, w:0, d:0, l:0, gf:0, ga:0, gd:0, pts:0, cls:"relegate" },
    { pos:31, club:"SL Benfica", crest:"assets/photos/crests/portugal-primeira-liga-2025-2026.football-logos.cc/256x256/benfica.football-logos.cc.png", p:1, w:0, d:0, l:1, gf:2, ga:3, gd:-1, pts:0, cls:"relegate" },
    { pos:32, club:"Paris SG", crest:"assets/photos/crests/france-ligue-1-2025-2026.football-logos.cc/256x256/paris-saint-germain.football-logos.cc.png", p:1, w:0, d:0, l:1, gf:1, ga:2, gd:-1, pts:0, cls:"relegate" },
    { pos:33, club:"Ajax", crest:"assets/photos/crests/netherlands-eredivisie-2025-2026.football-logos.cc/256x256/ajax.football-logos.cc.png", p:1, w:0, d:0, l:1, gf:1, ga:2, gd:-1, pts:0, cls:"relegate" },
    { pos:34, club:"Qarabağ FK", crest:"", p:1, w:0, d:0, l:1, gf:1, ga:3, gd:-2, pts:0, cls:"relegate" },
    { pos:35, club:"AS Monaco", crest:"assets/photos/crests/france-ligue-1-2025-2026.football-logos.cc/256x256/as-monaco.football-logos.cc.png", p:1, w:0, d:0, l:1, gf:0, ga:2, gd:-2, pts:0, cls:"relegate" },
    { pos:36, club:"Celtic", crest:"assets/photos/crests/scotland-premiership-2025-2026.football-logos.cc/256x256/celtic.football-logos.cc.png", p:1, w:0, d:0, l:1, gf:0, ga:2, gd:-2, pts:0, cls:"relegate" }
  ]
};
