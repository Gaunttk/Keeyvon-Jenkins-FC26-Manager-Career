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
| `wrexham_squad.csv` | Source of truth for all first-team squad players (53 columns) |
| `youth_academy.csv` | Academy players — same 53-column schema; promoted players move to `wrexham_squad.csv` |
| `season_log.json` | Structured record of matches, transfers, injuries, milestones |
| `docs/index.html` | Season hub (GitHub Pages root) |
| `docs/journal.html` | Match journal — "The Red Dragon Chronicles" |
| `docs/dossier.html` | Keevyon Jenkins manager profile |
| `docs/assets/style.css` | Shared design system — edit this, not inline styles |
| `docs/assets/photos/` | Player/match photos for future use |
| `docs/academy.html` | Youth Academy page — prospects, development plans, promotions |
| `docs/journal/` | Frozen archives of past seasons' journal entries (`season-01.html`, `season-02.html`, ...) — see "Season Rollover" |
| `scripts/sync_season_summary.py` | Regenerates the `SEASON_SUMMARY` block in `docs/index.html` from `season_log.json`. Run after any change to `season_log.json` |
| `JOURNAL_STYLE_GUIDE.md` | HTML templates, Owen Meredith persona, and capture checklist for journal-writing sessions. Read on demand — not loaded automatically |
| `scripts/check_roster_sync.py` | Cross-checks `docs/roster.html` cards against `wrexham_squad.csv` (name/age/OVR/position). Run after any squad change to catch stale or missing cards |

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
17 Physical         35 Dribbling_Tech
```

**GK mapping (cols 12–17):** Pace=Speed, Shooting=Kicking, Passing=Positioning, Dribbling=Reflexes, Defending=Handling, Physical=Diving. GKs have blank cols 31–46 (outfield Technical).

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

**Colors:** `--red: #C8102E` · `--gold: #D4A843` · `--black: #080808` · `--white: #F0F0F0`
**Journal-specific:** `--journal-bg: #0F0D0B` · `--journal-accent: #8B6914` · `--dispatch-blue: #4A90C4`

**Fonts:** Playfair Display (entry titles, pull quotes) · Barlow Condensed (labels/headers) · Barlow (body)

**Max-width:** 680px centered. Mobile-first.

---

### Journal Entries

Writing a journal entry (the two-voice Hawk's Nest / Red Dragon Dispatch pair)? **Read `JOURNAL_STYLE_GUIDE.md` first** — it has the HTML templates for both voices, season markers, the entry divider, the Owen Meredith persona, and the per-session capture checklist. Skip it for squad-only, stats-only, or squad-sync sessions that never touch the journal.

---

### Workflow

1. **User pushes screenshots to git from phone** — no Claude needed for this step
2. **User opens a Claude session** — reads images, updates CSV and/or generates journal entries
3. **Claude commits and pushes** to the session branch — GitHub Pages auto-deploys within ~1–2 minutes, no pull needed

GitHub Pages is configured to serve from the `claude/wrexham-fc26-career-dx9xgx` branch, `/docs` folder. Every push updates the live site automatically.

All HTML must also work as local `file://` files (no server needed). The `season_log.json` fetch in index.html fails silently when opened as `file://` — this is expected; the inline `SEASON_SUMMARY` block in index.html (generated by `scripts/sync_season_summary.py`) handles offline use.

---

### FC26 Screenshot Reading Guide

**Tab order in Squad Hub:** Status → Stats → Attributes (sub-tabs: Roles → Summary → Physical/Mental → Technical → PlayStyles) → Financial

**PlayStyle notation in CSV (col 49):**
- Gold icon = PlayStyle+ (append `+`)
- Gray filled diamond = Regular PlayStyle
- Outlined/empty diamond = unknown; do not include
- Players with no PlayStyles tab: set to `None`
- Players confirmed no PlayStyles tab: L. Cacace, S. Revan, T. O'Connor, D. Scarr, L. Brunt, A. James, B. Cadamarteri

**Roles (col 50):** Count of `+` and `++` symbols across all role sub-tabs combined.

**Notes (col 52):** Only record what is confirmed from screenshots:
- Contract willingness: "Not willing to negotiate." or "Willing to negotiate."
- GK stats if relevant: `GK: Div XX/Han XX/Kic XX/Ref XX/Spd XX/Pos XX`
- Development plan ETA if shown

---

### Squad Changes — Keep All Pages in Sync

Whenever a signing or departure is confirmed (screenshot or explicit user input), update **all** of the following in the same session, not just `wrexham_squad.csv`:

- `wrexham_squad.csv` — add/remove the row
- `docs/roster.html` — add/remove the player card (check for dual-position players who may appear in two position sections, e.g. a RB/RM listed under both Right Backs and Wide Attack). Run `python3 scripts/check_roster_sync.py` afterward — it catches missing/stale cards and name/age/OVR drift against the CSV (mechanical fields only; it does not touch or check the dev-status prose, which stays hand-written)
- `docs/depth_chart.html` — add/remove the player row in every position section they appear in; re-check any `gap-text` analysis notes that reference the player (e.g. "fallback option" language naming a player who has since left)
- `season_log.json` — add a `transfers` entry and a `milestones` entry
- `docs/season.html` — update Match Log / Player Stats table if the player has appeared in a match
- `docs/index.html` — the `SEASON_SUMMARY` block is a precomputed inline summary of `season_log.json` for offline use, not a live fetch. Run `python3 scripts/sync_season_summary.py` whenever `season_log.json` changes, or it silently goes stale. Never hand-edit `SEASON_SUMMARY` — it's generated.

A departed player should not be removed from `wrexham_squad.csv` until their transfer is actually confirmed (season_log `transfers` entry exists) — being merely transfer-listed is not a departure.

**Missing scouting data:** when adding a new signing, only fill in CSV columns actually confirmed by a screenshot (Status/Stats/Attributes tabs). Leave everything else blank rather than estimating or inferring from comparable players. Call out explicitly, in both the CSV `Notes` column and in the session summary to the user, which attribute groups are still missing (e.g. "Technical/Mental/Physical attributes pending — need the Attributes tab screenshots") so the user knows what to send next.

---

### Season Log Schema

Add entries to `season_log.json` after each game session:

```json
// Match
{ "date": "YYYY-MM-DD", "opponent": "Club Name", "home": true, "score": "2-1",
  "result": "W", "competition": "EFL Championship", "matchday": 1, "journal_entry": true }

// Transfer
{ "date": "YYYY-MM-DD", "player": "F. Lastname", "direction": "in",
  "club": "Club Name", "fee": "£2.5m", "wage": "£8k/w" }

// Injury
{ "date": "YYYY-MM-DD", "player": "F. Lastname", "description": "Hamstring, 3 weeks" }

// Milestone
{ "date": "YYYY-MM-DD", "description": "Free text note" }
```

---

### Season Rollover — Archiving a Finished Season

This is a multi-year career (15 seasons planned). `docs/journal.html` and `season_log.json` must **not** accumulate every season forever — archive them when a season ends so every future session only reads the current season's data, not the whole career's.

Trigger: the user confirms the in-game season is over (final league position known, promotion/relegation resolved).

1. **Archive the journal.** Cut every `<article class="entry ...">` (and its `season-marker` divs) belonging to the finished season out of `docs/journal.html` and into a new `docs/journal/season-NN.html`. Give the archive file the same nav/masthead chrome as `journal.html`, with relative paths adjusted for the subdirectory (`../assets/style.css`, `../index.html`, etc.) and its own self-contained TOC covering only that season.
2. **Reset `docs/journal.html`** to an empty entry list for the new season: update the `Past Seasons` sidebar list (slot already exists) with a link to the new archive file, update `pub-season`, and restart entry numbering at `Entry 001`.
3. **Archive `season_log.json`.** Move the finished season's file to `season_logs/season-NN.json` (create the folder if it doesn't exist), then start a fresh `season_log.json` with empty `matches`/`transfers`/`injuries`/`milestones` arrays and an updated `_meta.season`. Do this *before* running the sync script — `sync_season_summary.py` computes stats over whatever is in `season_log.json`, so last season's results must not carry into the new season's stat bar.
4. **Run `python3 scripts/sync_season_summary.py`** to regenerate `docs/index.html`'s stat bar against the fresh (empty) season log.
5. **Do not reset `wrexham_squad.csv` / `youth_academy.csv`.** The squad carries over between seasons — ages, contracts, and development continue as normal per-session updates.

---

### Rules

- Never fabricate stats, scores, signings, or events from screenshots not yet provided
- Never edit the old root-level HTML files
- Always commit on the designated branch
- CSV must always have exactly 53 fields per row — run a gap check after any bulk edit
- Height values like `6'1"` are stored with CSV quoting — always use the Python csv module, never manual string writes
- Every confirmed signing or departure must be reflected across all squad-facing pages in the same session — see "Squad Changes — Keep All Pages in Sync" above. Do not update `wrexham_squad.csv` alone and leave `roster.html`/`depth_chart.html` stale.
