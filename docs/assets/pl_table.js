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
  season: '2027/28',
  note: 'Table after Matchday 2, per a full-standings screenshot from the Brentford (H) session (2027-08-21).',
  // Zone divider rows, keyed by the position they appear ABOVE.
  markers: {
    1: { label: '\u2605 Champion', cls: 'promo' },
    2: { label: 'UEFA Champions League', cls: 'playoff' },
    5: { label: 'UEFA Europa League', cls: 'playoff' },
    6: { label: 'UEFA Conference League', cls: 'playoff' },
    18: { label: '\u25bc Relegation Zone', cls: 'relegate' }
  },
  rows: [
  { pos:1, club:"Nott'm Forest", crest:"assets/photos/crests/english-premier-league-2026-2027.football-logos.cc/256x256/nottingham-forest.football-logos.cc.png", p:2, w:2, d:0, l:0, gf:4, ga:1, gd:3, pts:6, cls:"promo" },
  { pos:2, club:"Wrexham", crest:"assets/photos/crests/wrexham-crest.png", p:2, w:2, d:0, l:0, gf:4, ga:1, gd:3, pts:6, cls:"playoff", wrexham:true },
  { pos:3, club:"Liverpool", crest:"assets/photos/crests/english-premier-league-2026-2027.football-logos.cc/256x256/liverpool.football-logos.cc.png", p:2, w:2, d:0, l:0, gf:5, ga:3, gd:2, pts:6, cls:"playoff" },
  { pos:4, club:"Brighton", crest:"assets/photos/crests/english-premier-league-2026-2027.football-logos.cc/256x256/brighton.football-logos.cc.png", p:2, w:2, d:0, l:0, gf:4, ga:2, gd:2, pts:6, cls:"playoff" },
  { pos:5, club:"Chelsea", crest:"assets/photos/crests/english-premier-league-2026-2027.football-logos.cc/256x256/chelsea.football-logos.cc.png", p:2, w:1, d:1, l:0, gf:5, ga:2, gd:3, pts:4, cls:"playoff" },
  { pos:6, club:"Everton", crest:"assets/photos/crests/english-premier-league-2026-2027.football-logos.cc/256x256/everton.football-logos.cc.png", p:2, w:1, d:1, l:0, gf:3, ga:2, gd:1, pts:4, cls:"playoff" },
  { pos:7, club:"Sunderland", crest:"assets/photos/crests/english-premier-league-2026-2027.football-logos.cc/256x256/sunderland.football-logos.cc.png", p:2, w:1, d:1, l:0, gf:1, ga:0, gd:1, pts:4, cls:"" },
  { pos:8, club:"AFC Bournemouth", crest:"assets/photos/crests/english-premier-league-2026-2027.football-logos.cc/256x256/bournemouth.football-logos.cc.png", p:2, w:1, d:0, l:1, gf:3, ga:2, gd:1, pts:3, cls:"" },
  { pos:9, club:"Brentford", crest:"assets/photos/crests/english-premier-league-2026-2027.football-logos.cc/256x256/brentford.football-logos.cc.png", p:2, w:1, d:0, l:1, gf:3, ga:3, gd:0, pts:3, cls:"" },
  { pos:10, club:"Leeds United", crest:"assets/photos/crests/english-premier-league-2026-2027.football-logos.cc/256x256/leeds-united.football-logos.cc.png", p:2, w:1, d:0, l:1, gf:3, ga:3, gd:0, pts:3, cls:"" },
  { pos:11, club:"Aston Villa", crest:"assets/photos/crests/english-premier-league-2026-2027.football-logos.cc/256x256/aston-villa.football-logos.cc.png", p:2, w:1, d:0, l:1, gf:1, ga:2, gd:-1, pts:3, cls:"" },
  { pos:12, club:"West Ham", crest:"assets/photos/crests/england-efl-championship-2026-2027.football-logos.cc/256x256/west-ham.football-logos.cc.png", p:2, w:1, d:0, l:1, gf:2, ga:4, gd:-2, pts:3, cls:"" },
  { pos:13, club:"Man City", crest:"assets/photos/crests/english-premier-league-2026-2027.football-logos.cc/256x256/manchester-city.football-logos.cc.png", p:1, w:0, d:1, l:0, gf:1, ga:1, gd:0, pts:1, cls:"" },
  { pos:14, club:"Fulham", crest:"assets/photos/crests/english-premier-league-2026-2027.football-logos.cc/256x256/fulham.football-logos.cc.png", p:1, w:0, d:1, l:0, gf:0, ga:0, gd:0, pts:1, cls:"" },
  { pos:15, club:"Spurs", crest:"assets/photos/crests/english-premier-league-2026-2027.football-logos.cc/256x256/tottenham.football-logos.cc.png", p:2, w:0, d:1, l:1, gf:2, ga:3, gd:-1, pts:1, cls:"" },
  { pos:16, club:"Arsenal", crest:"assets/photos/crests/english-premier-league-2026-2027.football-logos.cc/256x256/arsenal.football-logos.cc.png", p:2, w:0, d:0, l:2, gf:2, ga:4, gd:-2, pts:0, cls:"" },
  { pos:17, club:"Burnley", crest:"assets/photos/crests/english-premier-league-2026-2027.football-logos.cc/256x256/burnley.football-logos.cc.png", p:2, w:0, d:0, l:2, gf:2, ga:4, gd:-2, pts:0, cls:"" },
  { pos:18, club:"Man Utd", crest:"assets/photos/crests/english-premier-league-2026-2027.football-logos.cc/256x256/manchester-united.football-logos.cc.png", p:2, w:0, d:0, l:2, gf:2, ga:4, gd:-2, pts:0, cls:"relegate" },
  { pos:19, club:"Crystal Palace", crest:"assets/photos/crests/english-premier-league-2026-2027.football-logos.cc/256x256/crystal-palace.football-logos.cc.png", p:2, w:0, d:0, l:2, gf:3, ga:6, gd:-3, pts:0, cls:"relegate" },
  { pos:20, club:"Newcastle Utd", crest:"assets/photos/crests/english-premier-league-2026-2027.football-logos.cc/256x256/newcastle.football-logos.cc.png", p:2, w:0, d:0, l:2, gf:2, ga:5, gd:-3, pts:0, cls:"relegate" }
  ]
};

const PREMIER_LEAGUE_2026_27_FINAL = {
  competition: 'Premier League',
  season: '2026/27',
  note: 'Final table. Wrexham champions on 84 points \u2014 a maiden top-flight title in the club\u2019s first-ever Premier League season.',
  markers: {
    1: { label: '\u2605 CHAMPIONS \u2014 Wrexham win the Premier League, a maiden top-flight title', cls: 'promo' },
    2: { label: 'UEFA Champions League', cls: 'playoff' },
    5: { label: 'UEFA Europa League', cls: 'playoff' },
    6: { label: 'UEFA Conference League', cls: 'playoff' },
    18: { label: '\u25bc Relegation Zone', cls: 'relegate' }
  },
  rows: [
  { pos:1, club:"Wrexham", crest:"assets/photos/crests/wrexham-crest.png", p:38, w:26, d:6, l:6, gf:79, ga:24, gd:55, pts:84, cls:"promo", wrexham:true },
  { pos:2, club:"Man City", crest:"assets/photos/crests/english-premier-league-2026-2027.football-logos.cc/256x256/manchester-city.football-logos.cc.png", p:38, w:25, d:7, l:6, gf:82, ga:43, gd:39, pts:82, cls:"promo" },
  { pos:3, club:"Arsenal", crest:"assets/photos/crests/english-premier-league-2026-2027.football-logos.cc/256x256/arsenal.football-logos.cc.png", p:38, w:21, d:14, l:3, gf:74, ga:46, gd:28, pts:77, cls:"promo" },
  { pos:4, club:"Man Utd", crest:"assets/photos/crests/english-premier-league-2026-2027.football-logos.cc/256x256/manchester-united.football-logos.cc.png", p:38, w:24, d:4, l:10, gf:63, ga:40, gd:23, pts:76, cls:"promo" },
  { pos:5, club:"Liverpool", crest:"assets/photos/crests/english-premier-league-2026-2027.football-logos.cc/256x256/liverpool.football-logos.cc.png", p:38, w:20, d:10, l:8, gf:62, ga:44, gd:18, pts:70, cls:"playoff" },
  { pos:6, club:"Spurs", crest:"assets/photos/crests/english-premier-league-2026-2027.football-logos.cc/256x256/tottenham.football-logos.cc.png", p:38, w:18, d:11, l:9, gf:60, ga:45, gd:15, pts:65, cls:"playoff" },
  { pos:7, club:"Newcastle Utd", crest:"assets/photos/crests/english-premier-league-2026-2027.football-logos.cc/256x256/newcastle.football-logos.cc.png", p:38, w:13, d:14, l:11, gf:60, ga:49, gd:11, pts:53, cls:"" },
  { pos:8, club:"Chelsea", crest:"assets/photos/crests/english-premier-league-2026-2027.football-logos.cc/256x256/chelsea.football-logos.cc.png", p:38, w:14, d:9, l:15, gf:54, ga:53, gd:1, pts:51, cls:"" },
  { pos:9, club:"Crystal Palace", crest:"assets/photos/crests/english-premier-league-2026-2027.football-logos.cc/256x256/crystal-palace.football-logos.cc.png", p:38, w:14, d:7, l:17, gf:51, ga:55, gd:-4, pts:49, cls:"" },
  { pos:10, club:"West Ham", crest:"assets/photos/crests/england-efl-championship-2026-2027.football-logos.cc/256x256/west-ham.football-logos.cc.png", p:38, w:12, d:12, l:14, gf:47, ga:48, gd:-1, pts:48, cls:"" },
  { pos:11, club:"Aston Villa", crest:"assets/photos/crests/english-premier-league-2026-2027.football-logos.cc/256x256/aston-villa.football-logos.cc.png", p:38, w:12, d:11, l:15, gf:58, ga:61, gd:-3, pts:47, cls:"" },
  { pos:12, club:"AFC Bournemouth", crest:"assets/photos/crests/english-premier-league-2026-2027.football-logos.cc/256x256/bournemouth.football-logos.cc.png", p:38, w:12, d:11, l:15, gf:47, ga:55, gd:-8, pts:47, cls:"" },
  { pos:13, club:"Brighton", crest:"assets/photos/crests/english-premier-league-2026-2027.football-logos.cc/256x256/brighton.football-logos.cc.png", p:38, w:12, d:9, l:17, gf:47, ga:52, gd:-5, pts:45, cls:"" },
  { pos:14, club:"Brentford", crest:"assets/photos/crests/english-premier-league-2026-2027.football-logos.cc/256x256/brentford.football-logos.cc.png", p:38, w:12, d:8, l:18, gf:46, ga:55, gd:-9, pts:44, cls:"" },
  { pos:15, club:"Nott'm Forest", crest:"assets/photos/crests/english-premier-league-2026-2027.football-logos.cc/256x256/nottingham-forest.football-logos.cc.png", p:38, w:11, d:11, l:16, gf:44, ga:56, gd:-12, pts:44, cls:"" },
  { pos:16, club:"Sunderland", crest:"assets/photos/crests/english-premier-league-2026-2027.football-logos.cc/256x256/sunderland.football-logos.cc.png", p:38, w:12, d:8, l:18, gf:47, ga:62, gd:-15, pts:44, cls:"" },
  { pos:17, club:"Leeds United", crest:"assets/photos/crests/english-premier-league-2026-2027.football-logos.cc/256x256/leeds-united.football-logos.cc.png", p:38, w:9, d:11, l:18, gf:44, ga:64, gd:-20, pts:38, cls:"" },
  { pos:18, club:"Wolves", crest:"assets/photos/crests/england-efl-championship-2026-2027.football-logos.cc/256x256/wolves.football-logos.cc.png", p:37, w:8, d:7, l:22, gf:36, ga:67, gd:-31, pts:31, cls:"relegate" },
  { pos:19, club:"Ipswich", crest:"assets/photos/crests/english-premier-league-2026-2027.football-logos.cc/256x256/ipswich.football-logos.cc.png", p:37, w:8, d:6, l:23, gf:38, ga:67, gd:-29, pts:30, cls:"relegate" },
  { pos:20, club:"Sheffield Utd", crest:"assets/photos/crests/england-efl-championship-2026-2027.football-logos.cc/256x256/sheffield-united.football-logos.cc.png", p:38, w:6, d:4, l:28, gf:32, ga:85, gd:-53, pts:22, cls:"relegate" }
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
