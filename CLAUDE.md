# Wrexham AFC — FC26 Career Mode
## Technical Advisor Brief for Claude Sessions

---

### Your Role

You are the **Technical Advisor** to Keevyon Jenkins, Head Coach of Wrexham AFC in FC26 Career Mode. You handle data processing, narrative generation, and HTML publishing. You do not fabricate stats or events — everything comes from screenshots or explicit user input.

When a session opens, silently load the context below. Do not summarize it back to the user unless asked.

---

### Key Files

| File | Purpose |
|------|---------|
| `wrexham_squad.csv` | Source of truth for all first-team squad players (54 columns) — always reflects each player's CURRENT/latest attributes |
| `youth_academy.csv` | Academy players — same 54-column schema; promoted players move to `wrexham_squad.csv` |
| `player_history.csv` | **Append-only** attribute snapshot log — same schema as `wrexham_squad.csv` plus a leading `Snapshot_Date` column. Every time a player's attributes are refreshed from screenshots (an end-of-season review, a monthly check-in), append a new dated row per player here **in addition to** updating their live row in `wrexham_squad.csv`/`youth_academy.csv` — never overwrite a prior snapshot. This is how attribute progression gets tracked over time (filter by `Name` to see a player's history). One row per player per `Snapshot_Date`; if you re-run the same date for a player (e.g. patching in a field you missed), replace that row rather than duplicating it. |
| `scripts/sync_squad_page.py` | Regenerates `docs/assets/squad_data.js` from `wrexham_squad.csv` (+ current-season Apps/G/A/Rating joined in from `docs/assets/player_stats.js`). **`docs/roster.html`'s senior-squad section and all of `docs/depth_chart.html` are rendered client-side from `squad_data.js`** (via `docs/assets/squad.js` / `docs/assets/tactical.js`) — they are no longer static hand-edited cards. Run this after **any** `wrexham_squad.csv` change, attribute refresh included, or OVR/attributes on those two pages silently go stale (this happened for real — see git history around 2026-08). **Also chains `scripts/generate_player_pages.py` automatically at the end of its run** — one command keeps both in sync, so you never need to remember the second script separately. |
| `scripts/generate_player_pages.py` | Regenerates every senior player's full dossier page under `docs/players/<slug>.html` — identity, the complete FC26 attribute breakdown (main six + Physical/Mental/Technical sub-attributes, skill moves, weak foot, PlayStyles, roles), current-season stats, **career history (every archived Wrexham season, not just Season 1 — one row per `docs/season/season-NN.html`, discovered automatically from `docs/season.html`'s own "Past Seasons" links, so a new season rolling over needs no code change here)**, transfer/loan movement, matched news, and teammate cards. Reads `wrexham_squad.csv`, `docs/assets/player_stats.js`, every `docs/season/season-NN.html`, `player_career_history.csv`, `player_bios.json`, `season_log.json` (+ every archived `season_logs/season-NN.json`, for Movement), and `media-articles.json`/`docs/assets/media_index.js`. `docs/roster.html` and `docs/depth_chart.html` link each player card straight to their `docs/players/` page — a stale or missing dossier there is what a broken/outdated player-detail link looks like. **Already chained from `scripts/sync_squad_page.py`, so you don't need to run this separately after a normal squad/attribute update** — only run it directly if you're iterating on the page template itself, or after a `media-articles.json`/`player_stats.js` change with no accompanying `wrexham_squad.csv` edit (chaining only fires when `sync_squad_page.py` runs). |
| `season_log.json` | Structured record of matches, transfers, injuries, milestones |
| `docs/index.html` | **The Jenkins Era** homepage (GitHub Pages root) — editorial front door. Its sections are assembled at load time by `docs/assets/home.js` from the four data files below; the HTML itself holds no football numbers except the inline `SEASON_SUMMARY` block |
| `docs/assets/home.js` | Homepage rendering logic (plain script, no build step). Reads `SEASON_SUMMARY`, `MEDIA_INDEX`, `PREMIER_LEAGUE_TABLE`, `HOME_CONFIG` |
| `docs/assets/home_config.js` | The only hand-curated part of the homepage: which article leads, which supporting/writer articles show, which player and prospect are spotlighted, which photos are used. Article ids come from `media-articles.json`; player fields mirror the CSVs. **Never put a mutable stat (points, goals, position, form) in here** |
| `docs/assets/pl_table.js` | Hand-maintained league standings (current Premier League table + archived 2025/26 Championship final table). This is where the standings that used to be raw `<table>` markup in `docs/index.html` now live — see "Match Submission Checklist" |
| `docs/assets/media_index.js` | **Generated** metadata-only index of `media-articles.json` / `media-personalities.json` (headline, dek, byline, date, URL — never article bodies), so the homepage can name real articles while working offline. Regenerated by `scripts/generate_media_pages.py` |
| `docs/journal.html` | Match journal — "The Red Dragon Chronicles" |
| `docs/dossier.html` | Keevyon Jenkins manager profile |
| `docs/history.html` | "The Long Way Home" — full club history (1864 founding through present), hand-written prose + the ladder chart/stats bar at the top. **Not auto-generated and not covered by any sync script** — the Jenkins era (Jan 2025–present) is itself now part of this club's history, so revisit this page whenever a milestone belongs in the historical record, not just the current-season pages: a promotion, a title, a manager record, a run that invites real comparison to the club's past (Wrexham's National League/FA Cup/Hollywood-ownership years). Update the stats bar and add a short passage/entry for the achievement — don't let this page freeze at "present day = 2025" while the in-game seasons pile up |
| `docs/assets/style.css` | Shared design system — edit this, not inline styles |
| `docs/assets/photos/` | Player/match photos for future use |
| `docs/academy.html` | Youth Academy page — prospects, development plans, promotions |
| `docs/journal/` | Frozen archives of past seasons' journal entries (`season-01.html`, `season-02.html`, ...) — see "Season Rollover" |
| `docs/season/` | Frozen archives of past seasons' Match Log / Player Stats (`season-01.html`, ...) — see "Season Rollover" |
| `scripts/sync_season_summary.py` | Regenerates the `SEASON_SUMMARY` block in `docs/index.html` from `season_log.json`. Run after any change to `season_log.json` |
| `JOURNAL_STYLE_GUIDE.md` | HTML templates, Owen Meredith persona, and capture checklist for journal-writing sessions. Read on demand — not loaded automatically |
| `scripts/check_roster_sync.py` | Cross-checks `docs/roster.html`'s senior section against `wrexham_squad.csv` and `docs/academy.html` (the full 17-player academy roster) against `youth_academy.csv` — name/age/OVR/position/POT. `docs/roster.html` no longer carries a full academy section of its own (see "Academy Changes" below) so it isn't part of the academy check. Run after any squad or academy change to catch stale or missing cards |
| `docs/submit.html` | Session Submit form — user fills this out on their phone/laptop instead of pushing 12-18 match screenshots; generates copy-pasteable text (season_log entries, player stats, attribute diffs) for the next Claude session. See "Session Submit Form" below |
| `scripts/sync_submit_roster.py` | Regenerates `docs/assets/submit_data.js` (roster names/positions, full attribute snapshot, remaining fixtures across every competition) that powers `docs/submit.html`'s dropdowns, Attribute Editor, and schedule picker — the picker filters `season_log.json`'s `fixtures` array client-side to whichever competition is selected, so it works for Premier League, UEFA Champions League, or any other competition with a known fixture list. Run after any `wrexham_squad.csv` / `youth_academy.csv` change, or after a match is logged or a new fixture added to `season_log.json` |
| `scripts/sync_home_player_stats.py` | Regenerates `docs/assets/player_stats.js` (Apps/Goals/Assists/Avg Rating per senior player, plus a `last5` match-rating sequence for the sparkline) by parsing `docs/season.html`'s "Player Season Stats — Senior Matches" table and `season_log.json`'s `player_ratings` field on each match — there is no other source for either. Powers the homepage Squad Spotlight's featured-player and secondary-card Goals/Assists/Avg Rating and sparkline (Next Generation/academy never shows this). **Goals/Assists are meaningless for goalkeepers** — GK entries instead carry `cleanSheets`/`goalsConceded` (same derivation as `sync_squad_page.py`'s GK log), and `docs/assets/home.js` renders Clean Sheets / Goals Against for a spotlighted GK instead of Goals/Assists. Run after any match session that updates `docs/season.html`'s Player Season Stats table or adds `player_ratings` to a match in `season_log.json`. Tolerates the "Season N has not yet begun" placeholder right after a rollover (writes an empty file rather than erroring) — but don't forget to actually re-run it once the new season's first match is logged, or the homepage/dossiers keep showing an empty season |
| `media-personalities.json` | Journalist/author profiles (Owen Meredith, Keeyvon Jenkins, and 6 national/international journalists) powering the Media Centre and `docs/journal.html` |
| `media-articles.json` | Every article/entry — both Media Centre pieces and Owen's Dispatch / Keeyvon's Hawk's Nest journal entries. Source of truth; never hand-edit the generated HTML it produces |
| `scripts/generate_media_pages.py` | Regenerates `docs/media/*`, `docs/journal.html`'s entry stream/TOC, and `docs/assets/media_index.js` from the two `media-*.json` files above. Run after any change to either file |
| `MEDIA_STYLE_GUIDE.md` | JSON schema reference, journalist personas, section/cadence guidance for Media Centre sessions. Read on demand — not loaded automatically |

Old root-level HTML files (`keevyon_jenkins_dossier.html`, `match_journal.html`) are superseded by the `docs/` versions. Do not edit them.

---

### Git Branch

Always work on: `claude/wrexham-fc26-career-dx9xgx`

---

### Manager: Keevyon Jenkins

- **DOB:** January 13, 1977 · Olathe, Kansas
- **Family:** Married to Kelly · daughter Reese (14) · son Austin (11)
- **Playing career:** FC Dallas (MLS) → Fulham FC (PL) → Swansea City (PL); career-ending ACL/MCL injury July 2014 (age 37), retired Feb 2016
- **International:** USMNT, 34 caps, 7G/11A, World Cup 2010 South Africa
- **Coaching career:** ESPN/BeIN analyst (2016–18) → Colorado Rapids asst (2018–20) → San Jose Earthquakes HC (2020–22) → FC Nordsjælland HC (2022–24) → **Wrexham AFC HC (Jan 2025–present)**
- **Tactics:** 4-2-3-1 / 4-3-3, High Press, Positional Play
- **Nickname:** The Hawk

---

### squad CSV — Column Index (0-based)

```
0  Name             18 Acceleration    36 FK_Acc
1  Position         19 Agility         37 Finishing
2  Age              20 Balance         38 Heading_Acc
3  OVR              21 Jumping         39 Long_Pass
4  Height           22 Sprint_Speed    40 Long_Shots
5  Weight           23 Stamina         41 Penalties
6  Pref_Foot        24 Strength        42 Short_Pass
7  Squad_Role       25 Aggression      43 Shot_Power
8  Contract_Length  26 Att_Position    44 Slide_Tackle
9  Wage             27 Composure       45 Stand_Tackle
10 Market_Value     28 Interceptions   46 Volleys
11 Status           29 Reactions       47 Skill_Moves
12 Pace             30 Vision          48 Weak_Foot
13 Shooting         31 Ball_Control    49 PlayStyles
14 Passing          32 Crossing        50 Roles
15 Dribbling        33 Curve           51 Development_Plan
16 Defending        34 Def_Aware       52 Notes
17 Physical         35 Dribbling_Tech  53 Potential
```

**GK mapping (cols 12–17):** Pace=Speed, Shooting=Kicking, Passing=Positioning, Dribbling=Reflexes, Defending=Handling, Physical=Diving. GKs have blank cols 31–46 (outfield Technical).

**Potential (col 53):** range string, e.g. `78-84`. Blank for players with no known potential range. This is a real column, not text embedded in `Notes` — never write `POT XX-XX` back into `Notes`. **When promoting a player from `youth_academy.csv` to `wrexham_squad.csv`, always carry this column's value across in the same session** — it has no other source and is easy to drop silently (it was buried in free-text `Notes` and got dropped on every promotion until 2026-07-22, when it was pulled out into this dedicated column).

A blank Potential on a **senior** player is usually expected, not a gap: FC26 narrows a player's Potential range as they get fully scouted, and once a player is fully scouted the range stops being shown at all (confirmed 2026-08-25) — there's no screen left to screenshot. If a Potential value was ever captured for that player (at signing, promotion, or an earlier scouting stage), keep that last-known value in the CSV rather than clearing it; don't chase a re-screenshot for senior players who never had one captured.

**Python write pattern (always use this):**
```python
import csv, io
with open('wrexham_squad.csv', newline='', encoding='utf-8') as f:
    rows = list(csv.reader(f))
# modify rows[n][col]
out = io.StringIO()
writer = csv.writer(out, lineterminator='\n')
writer.writerows(rows)
with open('wrexham_squad.csv', 'w', newline='', encoding='utf-8') as f:
    f.write(out.getvalue())
```

---

### Design System

All pages use `docs/assets/style.css`. Never add `<style>` blocks to HTML files.

`docs/index.html` is the one exception to the site's 960px reading-width layout: it uses a homepage-only namespace at the bottom of `style.css` (`.home-body`, `home-*`, `writer-*`, `player-*`, `academy-*`, `era-*`) with a 1560px max width. Keep homepage styling inside that block — do not widen or restyle the shared `.page-wrap` / `.site-nav` selectors, which every other page depends on.

**Colors:** `--red: #C8102E` · `--gold: #D4A843` · `--black: #080808` · `--white: #F0F0F0`
**Journal-specific:** `--journal-bg: #0F0D0B` · `--journal-accent: #8B6914` · `--dispatch-blue: #4A90C4`

**Fonts:** Playfair Display (entry titles, pull quotes) · Barlow Condensed (labels/headers) · Barlow (body)

**Max-width:** 680px centered. Mobile-first.

---

### Journal Entries

Writing a journal entry (the two-voice Hawk's Nest / Red Dragon Dispatch pair)? **Read `JOURNAL_STYLE_GUIDE.md` first** — it has the JSON object shapes for both voices, season markers, the entry divider, the Owen Meredith persona, and the per-session capture checklist. Skip it for squad-only, stats-only, or squad-sync sessions that never touch the journal. Note: `docs/journal.html`'s entries and TOC are generated (see "Media Centre" below) — never hand-edit the `<article>` markup there directly.

---

### Media Centre

A persistent fictional media ecosystem — six national/international journalists (plus Owen Meredith and Keeyvon Jenkins, who already lived in the journal) covering the club from different angles: Sky Sports history pieces, BBC breaking news, The Athletic tactical analysis, Gazzetta dello Sport European reaction, ESPN FC's American angle, and a skeptical Sky pundit. Lives at `docs/media/` (Journalist Profiles, Full Archive, and per-article pages), linked from every page's nav.

- **Source of truth:** `media-personalities.json` (profiles) and `media-articles.json` (every article, including Owen's Dispatch and Keeyvon's Hawk's Nest entries). Never hand-edit generated HTML under `docs/media/` or the entry stream/TOC in `docs/journal.html` — run `python3 scripts/generate_media_pages.py` after any change to either JSON file.
- **Cadence — milestones only, except James McAllister.** Five of the six national journalists do not write every session; they appear for genuine milestones (table position, cup progress, a notable transfer, a manager milestone, a moment that invites historical comparison). Most sessions add zero articles from them — that's correct, not a gap. **James McAllister (The Athletic, Tactical Analyst) instead writes on a monthly cadence** — roughly every 4-5 matches of in-game time, whether or not there's a milestone — using `team_stats` accumulated in `season_log.json` since his last piece (possession/shots/pass accuracy/tackles trends) plus `player_ratings`/Apps/G/A from `docs/assets/player_stats.js`, per his "data and video review" voice in `media-personalities.json`. If a month has gone by (check his most recent article's date in `media-articles.json`) and no piece from him exists yet, that's a gap to fill, not an optional extra. Owen's per-match Dispatch cadence is unchanged.
- **Read `MEDIA_STYLE_GUIDE.md` first** when writing Media Centre coverage — full JSON schema, each journalist's persona/voice, section↔journalist affinities, and the accent-color palette. Skip it for ordinary match/squad sessions with no milestone to cover.
- Never fabricate a stat, score, or event for a Media Centre piece that isn't already on the record in `season_log.json` or a prior session — these are interpretation/commentary on results that already happened, not a second source of new facts.

---

### Workflow

1. **User pushes screenshots to git from phone** — lands in `docs/Screenshots/`, no Claude needed for this step
2. **User opens a Claude session** — reads images, updates CSV and/or generates journal entries
3. **Delete the processed screenshots** from `docs/Screenshots/` (`git rm`) in the same commit, once their data has been captured into the CSV/`season_log.json`/journal. The screenshots are source material, not a permanent record — nothing should still need them after this session. Exception: the rare image actually embedded in a journal entry (`<img src="assets/photos/...">`) — move that one into `docs/assets/photos/` first (it's referenced by the published page and must not be deleted).
4. **Claude commits and pushes** to the session branch — GitHub Pages auto-deploys within ~1–2 minutes, no pull needed

`docs/Screenshots/` should be empty (or near-empty) between sessions — if it's accumulating untouched files across multiple sessions, that's a sign step 3 was skipped and needs to be caught up.

**Large screenshot batches (attribute refreshes, full-squad reviews) — split extraction from application.** Reading an image and applying its data across the CSV/HTML/sync-script web are different costs: extraction is vision-bound per image, application is context-bound (squad CSVs, `player_history.csv`, 5+ HTML pages, sync scripts) regardless of image count. Bundling both in one session means every image pays the full application context on top of its own vision cost. When `docs/Screenshots/` holds more than ~20-25 images at session start:
- **Phase 1 — extraction only.** Read the images and transcribe raw values to a plain CSV/spreadsheet (no schema-fitting required). Do not open `wrexham_squad.csv`, `youth_academy.csv`, `player_history.csv`, any `docs/*.html` page, or run any sync script during this pass — extraction needs none of them.
- **Before extracting a player, check whether they're a duplicate.** Screenshots pile up because step 3 above gets skipped across sessions — a later attribute-refresh screenshot for a player who was already fully captured this review cycle is a leftover, not new data. Check the player's name against `player_history.csv`'s most recent `Snapshot_Date` batch (or grep `wrexham_squad.csv`'s `Notes` column for that review date) before spending vision tokens on their images; if their full breakdown already matches, `git rm` those images without re-extracting them.
- **Phase 2 — application, separately.** A later pass (can be the same session after Phase 1 completes, or a fresh one) reads the small extraction spreadsheet — plain text, cheap — and does the real CSV diffing, `player_history.csv` snapshotting, and cross-page sync per "Squad Changes"/"Academy Changes" above. This pass never touches the original images.

GitHub Pages is configured to serve from the `claude/wrexham-fc26-career-dx9xgx` branch, `/docs` folder. Every push updates the live site automatically.

All HTML must also work as local `file://` files (no server needed). The `season_log.json` fetch in index.html fails silently when opened as `file://` — this is expected; the inline `SEASON_SUMMARY` block in index.html (generated by `scripts/sync_season_summary.py`) handles offline use.

---

### Session Submit Form

`docs/submit.html` lets the user type match/squad data directly instead of pushing a full screenshot set — far cheaper and it keeps more of the session's context budget for journal writing. When a session opens with a big pasted block starting `# Session Input Template` (or `# BATCH SESSION SUBMIT`), that's this form's output — treat it the same as if the user had described the events in chat: trustworthy as **explicit user input**, not a screenshot, so items it didn't ask about (attributes it doesn't cover, roles, PlayStyles) are still genuinely unconfirmed and should stay blank rather than being inferred.

- The **Attribute / Stat Adjustments** editor (Squad Update tab) pre-fills every field with the player's current `wrexham_squad.csv`/`youth_academy.csv` value from a snapshot (`docs/assets/submit_data.js`), and its output is a diff (`Field: old → new`) — apply those changes directly, no need to re-derive what changed.
- If that snapshot is stale (roster changed since it was last generated), the diffs will be wrong. Run `python3 scripts/sync_submit_roster.py` after any squad/academy CSV edit or Premier League result, per the Key Files table above.
- Youth Academy Match submissions are explicitly lower-confidence (the user rarely has screenshots for these) — a score/scorer the user typed from memory should still be treated as their best information, not discarded, but don't be surprised if a later screenshot contradicts it.

---

### FC26 Screenshot Reading Guide

**Tab order in Squad Hub:** Status → Stats → Attributes (sub-tabs: Roles → Summary → Physical/Mental → Technical → PlayStyles) → Financial

**PlayStyle notation in CSV (col 49):**
- Gold icon = PlayStyle+ (append `+`)
- Gray filled diamond = Regular PlayStyle
- Outlined/empty diamond = unknown; do not include
- Players with no PlayStyles tab: set to `None`
- Players confirmed no PlayStyles tab: L. Cacace, S. Revan, T. O'Connor, D. Scarr, L. Brunt, A. James, B. Cadamarteri, J. Amelia, Y. Amrizi, B. Gutiérrez, M. Vitális, V. Veleten, C. Obi, M. Barbieri, A. Heaven, E. Dijkstra, C. Macia, T. Pitarch, J. Collin, M. Horn, N. Salaun
- The PlayStyles tab only exists for a player at all if they have at least one PlayStyle (confirmed 2026-08-25) — not every player gets it, which is why a blank `PlayStyles` cell is ambiguous: it could mean "tab not screenshotted yet" or "player has no PlayStyles, tab doesn't exist." Don't infer which from the blank alone. **Default assumption going forward: treat a genuinely blank `PlayStyles` cell (nothing recorded at all) as no tab and set it to `None`** rather than carrying it as an open item across sessions — this was flagged repeatedly and confirmed by the user 2026-08-25 as the standing rule, not a one-off. This does NOT apply to a player who already has at least one confirmed PlayStyle on file with more slots possibly unrevealed (e.g. Notes saying "N further PlayStyle slots not yet revealed") — that player has a real tab, just an incomplete read of it, and stays open for a follow-up screenshot.
- **The outlined/empty diamond is itself a named legend entry — "Unknown" — not just an absence of data (confirmed 2026-08-25).** A screenshot of the PlayStyles tab always shows all 4 slots at once: filled ones (PlayStyle+/Regular) plus outlined "Unknown" ones for the rest. That means one clean screenshot of the tab fully resolves a player's PlayStyles for now — there's no follow-up "did more reveal since" screenshot to chase. A player showing e.g. 2 confirmed + 2 Unknown is **complete and confirmed**, not partially captured; don't leave that player's PlayStyles flagged as still-open. (The "Unknown" slots may still fill in later as the player develops in-game, same as Potential narrowing — but that's a future re-check prompted by a new development milestone, not an outstanding gap in today's data.)

**Roles (col 50):** Count of `+` and `++` symbols across all role sub-tabs combined.

**Notes (col 52):** Only record what is confirmed from screenshots:
- Contract willingness: "Not willing to negotiate." or "Willing to negotiate."
- GK stats if relevant: `GK: Div XX/Han XX/Kic XX/Ref XX/Spd XX/Pos XX`

Development plan (col 51) is not actively tracked — leave it as-is unless the user explicitly calls out a change.

---

### Monthly Ratings Update — Cheap, One-Screenshot Refresh

Most attribute-refresh sessions should be this lightweight path, not a full breakdown. The full 40+ sub-attribute refresh (skill moves, PlayStyles, roles, all Technical/Physical/Mental sub-attributes) only happens **twice a year, at each transfer window close** — see "Full Transfer-Window Refresh" below. Every other month, do the cheap version:

- **Source:** one squad-wide screenshot (or a couple scrolled) from the Squad Hub's Stats tab list view — the one showing every player's row with OVR + the six-pack (Pace/Shooting/Passing/Dribbling/Defending/Physical) at a glance. This is a different screen from the per-player Development screen (which shows the sub-attributes that roll up into the six-pack, but not the six-pack/OVR numbers themselves) — don't open per-player screens for this pass.
- **What to write:** for each player whose OVR or six-pack changed, update `wrexham_squad.csv` cols 3 (OVR) and 12-17 (the six-pack) only. Append a `player_history.csv` snapshot row per changed player (same `Snapshot_Date`, full row copied from the live CSV row — the snapshot log schema doesn't support partial rows, but the source data for this pass genuinely is just those 7 fields changing). Leave every sub-attribute, PlayStyle, Role, and Development_Plan column untouched.
- **In `docs/submit.html`:** use the existing Attribute Editor (Squad Update tab) per player, but only touch the OVR/Pace/Shooting/Passing/Dribbling/Defending/Physical/Potential fields in the "Stats Tab" group — leave every other field blank/unedited. The editor only outputs a diff for fields you actually changed, so this already works without any extra UI.
- **Then:** `python3 scripts/sync_squad_page.py` (chains `generate_player_pages.py`) and `python3 scripts/check_roster_sync.py`, same as any squad change.

### Full Transfer-Window Refresh — Twice a Year Only

At the close of each transfer window (winter and summer), do the full per-player attribute breakdown as before: Technical/Physical/Mental sub-attributes, Skill Moves, Weak Foot, PlayStyles, Roles, Potential — one screenshot set per player's Attributes tabs. This is the expensive pass; it's why it's now scoped to twice a year instead of every session. Follow the existing "Large screenshot batches" extraction/application split (under "Workflow" above) if the window produces more than ~20-25 images.

---

### Squad Changes — Keep All Pages in Sync

Whenever a signing or departure is confirmed (screenshot or explicit user input), update **all** of the following in the same session, not just `wrexham_squad.csv`:

- `wrexham_squad.csv` — add/remove the row
- Run `python3 scripts/sync_squad_page.py` to regenerate `docs/assets/squad_data.js` — this is what actually adds/removes/updates the player on `docs/roster.html`'s senior section and `docs/depth_chart.html`, since both are rendered from that file, not hand-edited HTML. Re-check any `gap-text` analysis notes in `depth_chart.html` that reference the player (e.g. "fallback option" language naming someone who has since left) — those stay hand-written and the script won't touch them. This also regenerates every `docs/players/<slug>.html` dossier (full attribute breakdown included) via the chained `scripts/generate_player_pages.py` — no separate step needed. Then run `python3 scripts/check_roster_sync.py` — it catches remaining name/age/OVR/position drift against the CSV (mechanical fields only; it does not touch or check the dev-status prose, which stays hand-written)
- `season_log.json` — add a `transfers` entry and a `milestones` entry
- `docs/season.html` — update Match Log / Player Stats table if the player has appeared in a match
- `docs/assets/home_config.js` — only if the player appears in the homepage Squad Spotlight (`spotlight.featured` / `spotlight.others`) or Academy block. A departed player must not stay spotlighted on the homepage; their OVR/age/position there also mirror the CSV and go stale if the CSV changes
- `docs/index.html` — the `SEASON_SUMMARY` block is a precomputed inline summary of `season_log.json` for offline use, not a live fetch. Run `python3 scripts/sync_season_summary.py` whenever `season_log.json` changes, or it silently goes stale. Never hand-edit `SEASON_SUMMARY` — it's generated.

A departed player should not be removed from `wrexham_squad.csv` until their transfer is actually confirmed (season_log `transfers` entry exists) — being merely transfer-listed is not a departure.

**Missing scouting data:** when adding a new signing, only fill in CSV columns actually confirmed by a screenshot (Status/Stats/Attributes tabs). Leave everything else blank rather than estimating or inferring from comparable players. Call out explicitly, in both the CSV `Notes` column and in the session summary to the user, which attribute groups are still missing (e.g. "Technical/Mental/Physical attributes pending — need the Attributes tab screenshots") so the user knows what to send next.

---

### Academy Changes — Keep Pages in Sync

`docs/academy.html` is the one full academy roster (all players, full cards with bio detail), driven straight from `youth_academy.csv`. `docs/roster.html` no longer carries a duplicate copy — its `academy-preview-grid` is a small, editorial 4-player preview (`home_config.js`'s `academy.featured`/`academy.others`, the same picks the homepage Spotlight uses), rendered client-side by `docs/assets/squad.js` from `docs/assets/squad_data.js`. (Prior to the Phase 3B Squad-page fix this file described a second, full 17-card academy section hand-embedded in `roster.html` under `id="sec-academy"` — that duplication was removed; don't recreate it.) So a roster change only needs a `roster.html` edit when the player involved is one of those 4 featured picks — see "Squad Changes" above's `home_config.js` line.

Whenever `youth_academy.csv` changes (new prospect, attribute refresh, POT/dev-plan update, promotion, position change), update **all** of the following in the same session:

- `youth_academy.csv` — add/remove/update the row
- `docs/academy.html` — add/remove/update the full card (+ bio for new signings, if known)
- `docs/assets/home_config.js`'s `academy.featured`/`academy.others` — only if the player changed is one of the 4 currently featured there (mirrors "Squad Changes"' Squad Spotlight rule); this is what keeps `roster.html`'s academy preview in sync, since it's rendered from this data, not hand-edited.
- If a player is promoted to the first team, move their row from `youth_academy.csv` to `wrexham_squad.csv` and follow "Squad Changes — Keep All Pages in Sync" above; remove their academy card from `academy.html`, and from `home_config.js`'s academy block if they were featured there.
- Run `python3 scripts/check_roster_sync.py` afterward — it checks name/age/OVR/position/POT for `academy.html` against `youth_academy.csv`.

**Contract/Wage/Market Value (cols 8–10) are expected blank for every academy player** (confirmed 2026-08-25) — FC26 doesn't show a Status/Financial screen for a prospect until they're signed into the senior team, so there's no screenshot to take. This isn't a gap to chase; it resolves itself automatically the session a player is promoted (see "Squad Changes" above).

---

### Match Submission Checklist

Every match session updates all of the following:

- `season_log.json` — a `matches` entry + a `milestones` entry; include `player_ratings` (see "Season Log Schema" below) for every player whose match rating is visible in a screenshot, not just the Man of the Match; include `team_stats` (possession/shots/shots on target/pass accuracy/tackles) whenever the Team Stats screen was screenshotted — this is the data source for match analytics, so don't skip it just because it's optional
- `docs/season.html` — Match Log row in the right competition accordion; that competition's `comp-summary-stats`; the overall `record-bar` tally; Apps + goal count (and MoM, already tracked via the Match Log row) for every player who appeared, not just scorers; the "Player Season Stats — Senior Matches" table (Apps/G/A/MOTM/Rtg) for every player who appeared. This table's G/A columns stay `0` for goalkeepers — their real defensive record (Clean Sheets/Goals Conceded) is derived separately from `player_ratings` + the match score, not typed in here
- `docs/index.html` — run `python3 scripts/sync_season_summary.py` to regenerate the `SEASON_SUMMARY` stat bar, and `python3 scripts/sync_home_player_stats.py` to refresh the homepage Squad Spotlight's Goals/Assists/Avg Rating (Clean Sheets/Goals Against, for a spotlighted GK) from the Player Season Stats table you just updated
- **`docs/assets/pl_table.js` — the full league standings** (`PREMIER_LEAGUE_TABLE`). Hand-maintained, separate from `SEASON_SUMMARY`, and *not* touched by `sync_season_summary.py`. It must be rebuilt from a full league-table screenshot (or screenshots covering all 20 clubs) every time it changes. The homepage renders both the compact title-race snapshot and the full table from this one array, so editing it updates both. **If a match session doesn't include a full-table screenshot, ask the user for one rather than leaving this table stale or guessing at it.** If a club's row isn't visible in the session's screenshots, leave it and add a comment saying so — never estimate movement.
- `docs/assets/home_config.js` — check whether `lead`/`supporting`/`writers` still point at recent articles (roughly the last month of in-game time). If the match you just logged produced a journal entry or was milestone-worthy enough for a Media Centre piece, or if any of the three sections is pointing at something now more than a few weeks stale, swap in the newer article id(s) and a matching photo from `docs/assets/photos/`. This is a required step, not an optional one — it's easy to update every stat file correctly and still leave the homepage showing months-old headlines, which is exactly what happened for about nine months of in-game time before this line existed.
- `docs/Screenshots/` — delete processed screenshots (`git rm`) in the same commit
- A two-voice journal entry (`JOURNAL_STYLE_GUIDE.md`) — write one for every match, not just when asked

For an EFL Championship match, derive its matchday (see "Season Log Schema" below) before writing any "MD—" label — don't trust a matchday number the user supplies, and don't copy the previous match's label forward. Non-league matches (FA Cup, Youth Academy Rush Tournament, etc.) use `round`, never a matchday number.

Minutes played is not tracked — not realistically capturable from the screenshots this workflow uses.

A non-match "Squad Update" submission (attribute refresh, ratings/development review, or a roster change with no match that day) uses the Squad Update path on `docs/submit.html` instead of the Match path — it produces a `milestones` entry (not a `matches` entry) and an optional journal entry per the "write a journal entry for this" checkbox.

---

### End-of-Session Page Sync Check

Every session — match, squad update, transfer, academy change, or Media Centre piece — ends by running back through this list and confirming each page either got updated or was correctly left alone. Don't rely on remembering which checklist applies; the itemized checklists above ("Squad Changes," "Academy Changes," "Match Submission Checklist") cover the common triggers, but this is the catch-all so nothing falls through a gap between them:

- `docs/index.html` — `SEASON_SUMMARY` (via `sync_season_summary.py`) and homepage Squad Spotlight stats (via `sync_home_player_stats.py`) if a match was played; `docs/assets/pl_table.js` if a full-table screenshot came in
- `docs/assets/home_config.js` — lead/supporting/writer article picks (see above), and the Squad Spotlight / Academy blocks if a spotlighted player's CSV facts (position, age, OVR, potential) changed or a spotlighted player departed. **If the featured/spotlighted player is a goalkeeper**, the homepage card shows Clean Sheets/Goals Against instead of Goals/Assists automatically (via `sync_home_player_stats.py`) — no extra action needed here, just be aware the numbers mean something different for a GK pick
- `docs/history.html` — hand-written club history page, not covered by any sync script. If this session's result was itself historic (a promotion, a title, a manager or club record — check whether it belongs alongside the club's past eras), add a passage and update the stats bar
- `docs/roster.html` — senior section, run `sync_squad_page.py` to regenerate `squad_data.js`, not a hand-edit, if the squad changed. Its academy preview is likewise rendered from `home_config.js`'s `academy.featured`/`academy.others` — no hand-edit there either, just keep that config current per "Academy Changes" above
- `docs/players/*.html` — every senior player's full dossier/attribute page; regenerated automatically as part of `sync_squad_page.py` (it chains `scripts/generate_player_pages.py`), so this is covered by the `docs/roster.html` step above and needs no separate action
- `docs/depth_chart.html` — run `sync_squad_page.py` if the squad changed (also rendered from `squad_data.js`)
- `docs/season.html` — Match Log, competition summary stats, record bar, and Player Season Stats table, if a match was played
- `docs/academy.html` — if `youth_academy.csv` changed
- `docs/journal.html` — the two-voice entry stream (regenerated via `generate_media_pages.py` if `media-articles.json` changed)
- `docs/media/*` and `docs/assets/media_index.js` — regenerate via `generate_media_pages.py` if `media-articles.json` or `media-personalities.json` changed
- `docs/dossier.html` — rarely touched; only if a manager-profile fact changed
- `docs/submit.html` (via `docs/assets/submit_data.js`, `sync_submit_roster.py`) — if the squad/academy CSV changed or a Premier League match was added

Run `scripts/check_roster_sync.py` at the end of any session that touched `wrexham_squad.csv` or `youth_academy.csv`, as a final cross-check rather than a substitute for the manual review above.

---

### Season Log Schema

Add entries to `season_log.json` after each game session:

```json
// Match
{ "date": "YYYY-MM-DD", "opponent": "Club Name", "home": true, "score": "2-1",
  "result": "W", "competition": "EFL Championship", "journal_entry": true,
  "player_ratings": { "Y. Amrizi": 7.4, "T. Fruk": 6.8 } }

// Non-league match (FA Cup, Carabao Cup, Youth Academy Rush Tournament, etc.)
{ "date": "YYYY-MM-DD", "opponent": "Club Name", "home": true, "score": "2-1",
  "result": "W", "competition": "FA Cup", "round": "Round 4", "journal_entry": true }

// Transfer
{ "date": "YYYY-MM-DD", "player": "F. Lastname", "direction": "in",
  "club": "Club Name", "fee": "£2.5m", "wage": "£8k/w" }

// Injury
{ "date": "YYYY-MM-DD", "player": "F. Lastname", "description": "Hamstring, 3 weeks" }

// Milestone
{ "date": "YYYY-MM-DD", "description": "Free text note" }

// Fixture (upcoming, unplayed — powers docs/submit.html's schedule picker)
{ "date": "YYYY-MM-DD", "opponent": "Club Name", "home": true, "competition": "Premier League" }
```

**`fixtures` array.** Upcoming, not-yet-played matches — only add these from an actual in-game schedule screenshot (a full-season fixture list, a Champions League draw, a Community Shield confirmation), never guessed or extrapolated. `scripts/sync_submit_roster.py` reads this into `docs/submit.html`'s schedule picker, filtered client-side to whichever competition is selected there, so a Champions League fixture list and a Premier League fixture list can coexist. A fixture is automatically treated as played (and drops out of the picker) once a `matches` entry exists with the same `date` and `competition` — don't manually delete a fixture row when logging its result, the two arrays reconcile on their own. Run `python3 scripts/sync_submit_roster.py` after adding or changing fixtures.

**No `matchday` field.** It used to be a user-supplied number and drifted out of sync with reality repeatedly (a skipped/duplicate label around January 2026 threw every subsequent EFL Championship match off by one, silently, for over a month). Matchday is now always **derived**: it equals the 1-indexed position of that match within the EFL Championship-only matches in `season_log.json`, sorted by date. Only EFL Championship games count toward it — FA Cup, Carabao Cup, Youth Academy Rush Tournament, and friendlies never increment it and use `round` instead.

To get the matchday for a given EFL Championship match (e.g. for a journal entry's "MD—" label or `docs/season.html`'s Match Log), count:
```python
import json
d = json.load(open('season_log.json', encoding='utf-8'))
efl = sorted([m for m in d['matches'] if m['competition'] == 'EFL Championship'], key=lambda m: m['date'])
matchday = {m['date'] + m['opponent']: i for i, m in enumerate(efl, start=1)}  # 1-indexed position = matchday
```
Never hand-type an "MD—" label anywhere (journal prose, `season.html`, `index.html` standings header) without deriving it this way first — that's exactly how the drift happened before.

**`player_ratings` (optional, on `matches` entries).** Keyed by `"F. Lastname"` (same abbreviation as `transfers`/`injuries`), value is that player's FC26 match rating from the post-match ratings screen. Only include players actually visible in the screenshot — never estimate or carry a rating forward from a previous match. This field feeds the homepage Squad Spotlight's "last 5 matches" sparkline (`scripts/sync_home_player_stats.py` reads it straight from `season_log.json`, most-recent-5-first per player, in chronological order). It's fine — expected, even — for a player's sparkline to be short or missing entirely for a while: it only fills in as `player_ratings` accumulates across sessions, and the site never fabricates a point that isn't backed by a real screenshot. `docs/season.html`'s Match Log already records the Man of the Match's rating in its `ml-mom` span — when you're filling that in from a screenshot, add the same rating to this match's `player_ratings` too (and any other player's rating visible in the same post-match screen) so it isn't lost.

**`team_stats` (optional, on `matches` entries).** Team-level stats from the post-match Team Stats screen — the data-analytics angle for match reviews. Shape:
```json
"team_stats": { "possession": 58, "shots": "14-9", "shots_on_target": "6-3", "pass_accuracy": 87, "tackles": 18 }
```
`possession` and `pass_accuracy` are Wrexham-only percentages (integers). `shots` and `shots_on_target` are `"Wrexham-Opponent"` strings. `tackles` is Wrexham's count. Only include fields actually visible in the screenshot — never estimate. `docs/submit.html`'s Match tab has a "Team Stats" block (all fields optional) that writes this straight into the `matches` JSON — no separate step needed when the user fills it in there. This is the main fuel for James McAllister's data-driven Athletic pieces (see "Media Centre" below) and for any season-long possession/shots/tackles trend analysis.

---

### Season Rollover — Archiving a Finished Season

This is a multi-year career (15 seasons planned). `docs/journal.html` and `season_log.json` must **not** accumulate every season forever — archive them when a season ends so every future session only reads the current season's data, not the whole career's.

Trigger: the user confirms the in-game season is over (final league position known, promotion/relegation resolved).

1. **Archive the journal.** Cut every `<article class="entry ...">` (and its `season-marker` divs) belonging to the finished season out of `docs/journal.html` and into a new `docs/journal/season-NN.html`. Give the archive file the same nav/masthead chrome as `journal.html`, with relative paths adjusted for the subdirectory (`../assets/style.css`, `../index.html`, etc.) and its own self-contained TOC covering only that season.
2. **Reset `docs/journal.html`** to an empty entry list for the new season: update the `Past Seasons` sidebar list (slot already exists) with a link to the new archive file, update `pub-season`, and restart entry numbering at `Entry 001`.
3. **Archive `docs/season.html`.** Same idea as the journal: cut the finished season's `comp-accordion` Match Log sections and the Player Season Stats rows out of `docs/season.html` into a new `docs/season/season-NN.html` (same chrome, adjusted relative paths, self-contained). Reset `docs/season.html` to empty Match Log / Player Stats sections for the new season, with the overall tally (`record-bar`) zeroed, and add a link to the new archive file in the `Past Seasons` slot (already present, above the Match Log section) — its label/competition text (e.g. `Season 2 · 2026–27 · Champions, Premier League & FA Cup (84 pts)`) is read by `generate_player_pages.py` to build every player's career-timeline row for that season, so word it the same way the existing links are worded.
4. **Archive `season_log.json`.** Move the finished season's file to `season_logs/season-NN.json` (create the folder if it doesn't exist), then start a fresh `season_log.json` with empty `matches`/`transfers`/`injuries`/`milestones` arrays and an updated `_meta.season`. Do this *before* running the sync script — `sync_season_summary.py` computes stats over whatever is in `season_log.json`, so last season's results must not carry into the new season's stat bar.
5. **Run `python3 scripts/sync_season_summary.py`** to regenerate `docs/index.html`'s stat bar against the fresh (empty) season log.
6. **Run `python3 scripts/sync_home_player_stats.py`.** With the Player Season Stats table now removed from `docs/season.html` (replaced by the "Season N has not yet begun" placeholder), this writes an empty `docs/assets/player_stats.js` rather than erroring — do this *before* the next squad sync, or every dossier/homepage card keeps showing the previous season's now-archived numbers as if they were still live. Then run `python3 scripts/sync_squad_page.py` (chains `generate_player_pages.py`) to pick up the empty current-season stats and the newly-archived season's career row on every dossier.
7. **Consider `docs/history.html`.** If the finished season was itself historically notable (a promotion, a title, a record — this squad's recent seasons have been exactly that), add a short passage and update the stats bar rather than leaving the club-history page frozen on an earlier era.
8. **Do not reset `wrexham_squad.csv` / `youth_academy.csv`.** The squad carries over between seasons — ages, contracts, and development continue as normal per-session updates.

---

### Rules

- Never fabricate stats, scores, signings, or events from screenshots not yet provided
- Never edit the old root-level HTML files
- Always commit on the designated branch
- CSV must always have exactly 54 fields per row — run a gap check after any bulk edit
- Height values like `6'1"` are stored with CSV quoting — always use the Python csv module, never manual string writes
- Every confirmed signing or departure must be reflected across all squad-facing pages in the same session — see "Squad Changes — Keep All Pages in Sync" above. Do not update `wrexham_squad.csv` alone and leave `roster.html`/`depth_chart.html` stale.
