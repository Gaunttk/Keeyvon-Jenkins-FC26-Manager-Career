/* ─────────────────────────────────────────────────────────────────────────
   pl_table.js — HAND-MAINTAINED league standings for the homepage.

   These are the same confirmed figures that used to live as raw <table>
   markup inside docs/index.html. They were moved here (not re-derived, not
   re-guessed) so the homepage can render BOTH a compact title-race snapshot
   and the full table from one single copy of the data.

   HOW TO UPDATE (per CLAUDE.md, "Match Submission Checklist"):
   Rebuild PREMIER_LEAGUE_TABLE from a full league-table screenshot covering
   all 20 clubs. Never guess a row. If a club's row is not visible in the
   screenshots for a session, leave it alone and flag it with a comment
   rather than inventing movement — see the Leeds United note below.

   `cls` drives the zone striping only: 'promo' | 'playoff' | 'relegate' | ''.
   `crest` paths are relative to docs/.
   ───────────────────────────────────────────────────────────────────────── */

const PREMIER_LEAGUE_TABLE = {
  competition: 'Premier League',
  season: '2026/27',
  // Zone divider rows, keyed by the position they appear ABOVE.
  markers: {
    1: { label: 'Champion', cls: 'promo' },
    2: { label: 'UEFA Champions League', cls: 'playoff' },
    5: { label: 'UEFA Europa League', cls: 'playoff' },
    6: { label: 'UEFA Conference League', cls: 'playoff' },
    18: { label: '\u25bc Relegation Zone', cls: 'relegate' }
  },
  rows: [
  { pos:1, club:"Man City", crest:"assets/photos/crests/english-premier-league-2026-2027.football-logos.cc/256x256/manchester-city.football-logos.cc.png", p:36, w:25, d:6, l:5, gf:78, ga:38, gd:40, pts:81, cls:"promo" },
  { pos:2, club:"Wrexham", crest:"assets/photos/crests/wrexham-crest.png", p:36, w:24, d:6, l:6, gf:74, ga:22, gd:52, pts:78, cls:"promo", wrexham:true },
  { pos:3, club:"Man Utd", crest:"assets/photos/crests/english-premier-league-2026-2027.football-logos.cc/256x256/manchester-united.football-logos.cc.png", p:36, w:24, d:3, l:9, gf:62, ga:37, gd:25, pts:75, cls:"promo" },
  { pos:4, club:"Arsenal", crest:"assets/photos/crests/english-premier-league-2026-2027.football-logos.cc/256x256/arsenal.football-logos.cc.png", p:35, w:19, d:13, l:3, gf:68, ga:44, gd:24, pts:70, cls:"promo" },
  { pos:5, club:"Liverpool", crest:"assets/photos/crests/english-premier-league-2026-2027.football-logos.cc/256x256/liverpool.football-logos.cc.png", p:35, w:19, d:9, l:7, gf:59, ga:40, gd:19, pts:66, cls:"playoff" },
  { pos:6, club:"Spurs", crest:"assets/photos/crests/english-premier-league-2026-2027.football-logos.cc/256x256/tottenham.football-logos.cc.png", p:36, w:18, d:9, l:9, gf:58, ga:43, gd:15, pts:63, cls:"playoff" },
  { pos:7, club:"Newcastle Utd", crest:"assets/photos/crests/english-premier-league-2026-2027.football-logos.cc/256x256/newcastle.football-logos.cc.png", p:36, w:12, d:13, l:11, gf:56, ga:48, gd:8, pts:49, cls:"" },
  { pos:8, club:"Chelsea", crest:"assets/photos/crests/english-premier-league-2026-2027.football-logos.cc/256x256/chelsea.football-logos.cc.png", p:36, w:13, d:8, l:15, gf:51, ga:51, gd:0, pts:47, cls:"" },
  { pos:9, club:"Aston Villa", crest:"assets/photos/crests/english-premier-league-2026-2027.football-logos.cc/256x256/aston-villa.football-logos.cc.png", p:36, w:12, d:10, l:14, gf:55, ga:57, gd:-2, pts:46, cls:"" },
  { pos:10, club:"Crystal Palace", crest:"assets/photos/crests/english-premier-league-2026-2027.football-logos.cc/256x256/crystal-palace.football-logos.cc.png", p:36, w:13, d:7, l:16, gf:48, ga:52, gd:-4, pts:46, cls:"" },
  { pos:11, club:"AFC Bournemouth", crest:"assets/photos/crests/english-premier-league-2026-2027.football-logos.cc/256x256/bournemouth.football-logos.cc.png", p:36, w:12, d:9, l:15, gf:44, ga:52, gd:-8, pts:45, cls:"" },
  { pos:12, club:"Brighton", crest:"assets/photos/crests/english-premier-league-2026-2027.football-logos.cc/256x256/brighton.football-logos.cc.png", p:36, w:12, d:7, l:17, gf:45, ga:50, gd:-5, pts:43, cls:"" },
  { pos:13, club:"Nott'm Forest", crest:"assets/photos/crests/english-premier-league-2026-2027.football-logos.cc/256x256/nottingham-forest.football-logos.cc.png", p:36, w:11, d:10, l:15, gf:43, ga:52, gd:-9, pts:43, cls:"" },
  { pos:14, club:"Sunderland", crest:"assets/photos/crests/english-premier-league-2026-2027.football-logos.cc/256x256/sunderland.football-logos.cc.png", p:36, w:12, d:7, l:17, gf:45, ga:59, gd:-14, pts:43, cls:"" },
  { pos:15, club:"West Ham", crest:"assets/photos/crests/england-efl-championship-2026-2027.football-logos.cc/256x256/west-ham.football-logos.cc.png", p:36, w:10, d:12, l:14, gf:41, ga:46, gd:-5, pts:42, cls:"" },
  { pos:16, club:"Brentford", crest:"assets/photos/crests/english-premier-league-2026-2027.football-logos.cc/256x256/brentford.football-logos.cc.png", p:36, w:11, d:7, l:18, gf:41, ga:54, gd:-13, pts:40, cls:"" },
  { pos:17, club:"Leeds United", crest:"assets/photos/crests/english-premier-league-2026-2027.football-logos.cc/256x256/leeds-united.football-logos.cc.png", p:36, w:9, d:10, l:17, gf:43, ga:61, gd:-18, pts:37, cls:"" },
  { pos:18, club:"Wolves", crest:"assets/photos/crests/england-efl-championship-2026-2027.football-logos.cc/256x256/wolves.football-logos.cc.png", p:36, w:8, d:7, l:21, gf:35, ga:64, gd:-29, pts:31, cls:"relegate" },
  { pos:19, club:"Ipswich", crest:"assets/photos/crests/english-premier-league-2026-2027.football-logos.cc/256x256/ipswich.football-logos.cc.png", p:36, w:8, d:5, l:23, gf:37, ga:66, gd:-29, pts:29, cls:"relegate" },
  { pos:20, club:"Sheffield Utd", crest:"assets/photos/crests/england-efl-championship-2026-2027.football-logos.cc/256x256/sheffield-united.football-logos.cc.png", p:36, w:6, d:4, l:26, gf:31, ga:78, gd:-47, pts:22, cls:"relegate" }
  ]
};

const CHAMPIONSHIP_2025_26_FINAL = {
  competition: 'EFL Championship',
  season: '2025/26',
  note: 'Final table. Wrexham champions on 112 points, promoted to the Premier League.',
  markers: {
    1: { label: '\u2605 CHAMPIONS \u2014 title won, promoted to the Premier League', cls: 'promo' },
    2: { label: '\u25b2 Automatic Promotion', cls: 'playoff' },
    3: { label: '\u2191 Promotion Play-offs \u00b7 3rd\u20136th', cls: 'playoff' },
    22: { label: '\u25bc Relegated', cls: 'relegate' }
  },
  rows: [
  { pos:1, club:"Wrexham", crest:"assets/photos/crests/wrexham-crest.png", p:46, w:36, d:4, l:6, gf:111, ga:47, gd:64, pts:112, cls:"promo", wrexham:true },
  { pos:2, club:"Ipswich", crest:"assets/photos/crests/england-efl-championship-2026-2027.football-logos.cc/ipswich-town-logo-footylogos.png", p:46, w:22, d:15, l:9, gf:65, ga:42, gd:23, pts:81, cls:"promo" },
  { pos:3, club:"Swansea City", crest:"assets/photos/crests/swansea-city-white-crest.png", p:46, w:21, d:16, l:9, gf:61, ga:42, gd:19, pts:79, cls:"playoff" },
  { pos:4, club:"Southampton", crest:"assets/photos/crests/southampton.png", p:46, w:20, d:16, l:10, gf:74, ga:55, gd:19, pts:76, cls:"playoff" },
  { pos:5, club:"Sheffield Utd", crest:"assets/photos/crests/england-efl-championship-2026-2027.football-logos.cc/sheffield-united-logo-footylogos.png", p:46, w:22, d:10, l:14, gf:69, ga:51, gd:18, pts:76, cls:"playoff" },
  { pos:6, club:"Coventry City", crest:"assets/photos/crests/coventry-city.png", p:46, w:19, d:18, l:9, gf:69, ga:53, gd:16, pts:75, cls:"playoff" },
  { pos:7, club:"Hull City", crest:"assets/photos/crests/hull-city.png", p:46, w:20, d:15, l:11, gf:66, ga:51, gd:15, pts:75, cls:"" },
  { pos:8, club:"Bristol City", crest:"assets/photos/crests/england-efl-championship-2026-2027.football-logos.cc/bristol-city-logo-footylogos.png", p:46, w:18, d:18, l:10, gf:62, ga:52, gd:10, pts:72, cls:"" },
  { pos:9, club:"Leicester City", crest:"assets/photos/crests/leicester-city.png", p:46, w:18, d:17, l:11, gf:67, ga:54, gd:13, pts:71, cls:"" },
  { pos:10, club:"Preston", crest:"assets/photos/crests/preston-north-end.png", p:46, w:17, d:17, l:12, gf:65, ga:54, gd:11, pts:68, cls:"" },
  { pos:11, club:"Middlesbrough", crest:"assets/photos/crests/middlesbrough.png", p:46, w:16, d:19, l:11, gf:58, ga:56, gd:2, pts:67, cls:"" },
  { pos:12, club:"Millwall", crest:"assets/photos/crests/millwall.png", p:46, w:16, d:15, l:15, gf:56, ga:52, gd:4, pts:63, cls:"" },
  { pos:13, club:"Birmingham City", crest:"assets/photos/crests/birmingham-city.png", p:46, w:15, d:15, l:16, gf:57, ga:56, gd:1, pts:60, cls:"" },
  { pos:14, club:"West Brom", crest:"assets/photos/crests/west-brom.png", p:46, w:15, d:14, l:17, gf:52, ga:68, gd:-16, pts:59, cls:"" },
  { pos:15, club:"Watford", crest:"assets/photos/crests/england-efl-championship-2026-2027.football-logos.cc/watford-logo-footylogos.png", p:46, w:12, d:17, l:17, gf:47, ga:49, gd:-2, pts:53, cls:"" },
  { pos:16, club:"QPR", crest:"assets/photos/crests/queens-park-rangers.png", p:46, w:13, d:13, l:20, gf:49, ga:62, gd:-13, pts:52, cls:"" },
  { pos:17, club:"Stoke City", crest:"assets/photos/crests/stoke-city.png", p:46, w:12, d:15, l:19, gf:44, ga:53, gd:-9, pts:51, cls:"" },
  { pos:18, club:"Norwich", crest:"assets/photos/crests/norwich-city.png", p:46, w:11, d:17, l:18, gf:46, ga:57, gd:-11, pts:50, cls:"" },
  { pos:19, club:"Blackburn Rovers", crest:"assets/photos/crests/blackburn-rovers.png", p:46, w:9, d:18, l:19, gf:48, ga:68, gd:-20, pts:45, cls:"" },
  { pos:20, club:"Sheffield Wed", crest:"assets/photos/crests/sheffield-wednesday.png", p:46, w:9, d:16, l:21, gf:43, ga:68, gd:-25, pts:43, cls:"" },
  { pos:21, club:"Portsmouth", crest:"assets/photos/crests/england-efl-championship-2026-2027.football-logos.cc/portsmouth-logo-footylogos.png", p:46, w:9, d:16, l:21, gf:37, ga:64, gd:-27, pts:43, cls:"" },
  { pos:22, club:"Derby County", crest:"assets/photos/crests/derby-county-white.png", p:46, w:7, d:20, l:19, gf:42, ga:61, gd:-19, pts:41, cls:"relegate" },
  { pos:23, club:"Charlton Ath", crest:"assets/photos/crests/england-efl-championship-2026-2027.football-logos.cc/charlton-athletic-logo-footylogos.png", p:46, w:9, d:11, l:26, gf:43, ga:72, gd:-29, pts:38, cls:"relegate" },
  { pos:24, club:"Oxford United", crest:"assets/photos/crests/oxford-united.png", p:46, w:5, d:10, l:31, gf:40, ga:84, gd:-44, pts:25, cls:"relegate" }
  ]
};
