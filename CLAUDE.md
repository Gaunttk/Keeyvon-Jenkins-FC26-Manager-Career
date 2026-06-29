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
| `wrexham_squad.csv` | Source of truth for all 36 squad players (53 columns) |
| `season_log.json` | Structured record of matches, transfers, injuries, milestones |
| `docs/index.html` | Season hub (GitHub Pages root) |
| `docs/journal.html` | Match journal — "The Red Dragon Chronicles" |
| `docs/dossier.html` | Keevyon Jenkins manager profile |
| `docs/assets/style.css` | Shared design system — edit this, not inline styles |
| `docs/assets/photos/` | Player/match photos for future use |

Old root-level HTML files (`keevyon_jenkins_dossier.html`, `match_journal.html`) are superseded by the `docs/` versions. Do not edit them.

---

### Git Branch

Always work on: `claude/wrexham-fc26-career-dx9xgx`

---

### Manager: Keevyon Jenkins

- **DOB:** January 13, 1987 · Olathe, Kansas
- **Playing career:** FC Dallas (MLS) → Fulham FC (PL) → Swansea City (PL); career-ending ACL/MCL injury July 2014, retired Feb 2016
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

**Colors:** `--red: #C8102E` · `--gold: #D4A843` · `--black: #0A0A0A` · `--white: #F5F5F5`

**Fonts:** Barlow Condensed (headings/labels) · Barlow (body)

**Max-width:** 680px centered. Mobile-first.

**Journal voices:**
- `<span class="voice-badge hawks-nest">Hawks Nest</span>` — Jenkins' first-person voice (red badge)
- `<span class="voice-badge dispatch">Dispatch</span>` — third-person narrative (charcoal badge)

**Match result chip:**
```html
<div class="result-chip">
  <div class="result-score"><span class="win">2</span>–<span class="loss">1</span></div>
  <div class="result-detail"><strong>vs. Sheffield United</strong><br>EFL Championship · Matchday 1</div>
</div>
```

---

### Workflow

1. **User pushes screenshots to git from phone** — no Claude needed for this step
2. **User opens a Claude session** — reads images, updates CSV and/or generates journal entries
3. **Claude commits and pushes** to `claude/wrexham-fc26-career-dx9xgx`
4. **User pulls to PC** and opens HTML files locally in browser

GitHub Pages (when enabled on `docs/`) provides a shareable public URL. Do not rely on Pages being active — all HTML must work as local files too. The `season_log.json` fetch in index.html fails silently when opened as a file:// — this is expected.

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

### Rules

- Never fabricate stats, scores, signings, or events from screenshots not yet provided
- Never edit the old root-level HTML files
- Always commit on the designated branch
- CSV must always have exactly 53 fields per row — run a gap check after any bulk edit
- Height values like `6'1"` are stored with CSV quoting — always use the Python csv module, never manual string writes
