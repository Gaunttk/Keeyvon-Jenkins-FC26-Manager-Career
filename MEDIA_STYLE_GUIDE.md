# Media Centre Style Guide

Read this file when a session is writing Media Centre coverage (a national/international
journalist's take on a milestone) or touching `media-personalities.json` / `media-articles.json`
directly. Not needed for squad-only, stats-only, or squad-sync sessions — see `CLAUDE.md` for those.
For Owen Meredith's per-match Dispatch and Keeyvon's Hawk's Nest diary, see `JOURNAL_STYLE_GUIDE.md`
— those two voices still live in `docs/journal.html`, just rendered from the same JSON now.

---

### How This System Works

`media-personalities.json` and `media-articles.json` (both at repo root) are the source of truth.
**Never hand-edit any HTML under `docs/media/` or the entry stream/TOC in `docs/journal.html`** —
both are generated. After changing either JSON file, run:

```
python3 scripts/generate_media_pages.py
```

This regenerates:
- `docs/journal.html`'s entry stream and sidebar TOC (from `content_type: "dispatch"` / `"diary"` articles)
- `docs/media/index.html`, `docs/media/journalists.html`, `docs/media/archive.html`
- `docs/media/articles/<id>.html` for every other `content_type`

The script fails loudly (non-zero exit) if an article's `author_id` doesn't resolve to a
profile, or if the marker comments it needs in `journal.html` are missing — don't remove
`<!-- MEDIA:JOURNAL:ENTRIES:START/END -->` or `<!-- MEDIA:JOURNAL:TOC:START/END -->`.

**Article order in `media-articles.json` is the render order for `docs/journal.html`** (dispatch/diary
entries render top-to-bottom in array order, not re-sorted by date — some sessions interleave a cup
match and a league match out of strict date order deliberately). **Always add new dispatch/diary
entries at the top of the array (index 0)**, same as the old "newest first" convention for hand-typed
`journal.html` entries. Media Centre articles (feature/tactical/tv-debate/international/press-conference/
breaking) don't affect journal order, but insert them near the top too for readability of the JSON file.

---

### Cadence: Milestones Only

Owen Meredith writes every match/session, same as always. **The other six journalists do not.**
They appear only when something crosses a real threshold — a table position, a cup round, a
transfer, a manager milestone, a comparison worth making. Most sessions should add zero Media
Centre articles. Rough guide for what counts as milestone-worthy:

- A significant league table movement (top of the table, into/out of European places, promotion/relegation confirmed)
- A cup semi-final or final
- A notable transfer (fee, profile of player, or narrative significance)
- A managerial milestone (anniversary, a landmark win total, a contract situation)
- A result significant enough to invite historical comparison (a first top-flight win, a derby, beating a "big six" club)
- A running storyline reaching a natural checkpoint (e.g. Darren Cole revisiting a prediction he made earlier in the season)

When in doubt, don't add one. An empty Media Centre section for a while is correct, not broken —
the `docs/media/index.html` generator renders "More coverage coming as the season develops." for
any section with nothing in it yet, which is the honest state until a real milestone happens.

---

### JSON Schema Reference

**`media-personalities.json`** — array of profile objects:

| Field | Notes |
|---|---|
| `id` | kebab-case, stable forever (used in URLs and cross-references) |
| `name`, `outlet`, `role` | |
| `is_press` | `false` only for Keeyvon Jenkins (his diary isn't journalism) |
| `bio`, `voice`, `specialties[]`, `relationship_with_wrexham` | public-facing profile text |
| `accent_color` | a CSS var, e.g. `var(--hargreaves-accent)` — see palette below |
| `headshot` | `null` until a real image lands in `docs/assets/journalists/`; then a relative path from `docs/` |

**`media-articles.json`** — array of article objects. Common fields on every entry:
`id`, `author_id`, `content_type`, `date` (ISO `YYYY-MM-DD`), `headline`, `dek`, `tags[]`,
`featured` (bool), `body_html` (a hand-authored HTML fragment — see "Writing body_html" below).

`content_type` determines which fields are required and where the piece renders:

- **`dispatch`** (Owen Meredith, renders into `journal.html`): also needs `section` (one of
  Match Coverage / Inside the Club / Feature / Transfer Window / Season Review — same as
  `JOURNAL_STYLE_GUIDE.md` always used), `competition`, `season`, `date_line` (the literal
  header text, e.g. `December 19, 2026 · Neutral Venue`, optionally prefixed with an
  `<img class="opponent-crest" ...>` tag exactly as before).
- **`diary`** (Keeyvon Jenkins, renders into `journal.html`): also needs `entry_number`
  (e.g. `"Entry 099"`), `sig_date` (e.g. `"December 20, 2026"`), `date_line`.
- **`feature` / `tactical` / `tv-debate` / `international` / `press-conference` / `breaking`**
  (Media Centre): also needs `section` (one of the six Media Centre sections — Featured Columns,
  Match Coverage, Tactical Analysis, Television Debate, International Reaction, Press Conferences),
  `outlet`, `competition`, `season`. Optional: `related_match: {date, opponent}` to link a piece
  to the match/event that prompted it.

Optional on any dispatch/diary entry: `marker: {text, date_label}` — renders a season-marker
divider immediately before that entry (competition/round changes). Only set this on the *first*
entry of a new marker group, exactly like the old hand-typed `<div class="season-marker">` did.

**Writing `body_html`:** this is a raw HTML fragment inserted verbatim — not markdown. Reuse the
same inline classes Owen's Dispatches always have: `<p>`, `<div class="pull-quote"><p>...</p>
<span class="pull-quote-attr">— Name</span></div>`, and `<div class="context-card">...</div>` for
boxed stat summaries (see any existing entry in `media-articles.json` for the exact pattern).
Never invent a fact, score, or quote that isn't grounded in `season_log.json` / prior session
input — Media Centre pieces interpret and contextualize results that are already on the record,
they don't create new ones.

---

### Accent Color Palette

Each journalist has a CSS variable in `docs/assets/style.css`'s `:root`, deliberately not matching
the real outlet's actual branding (per the "avoid copying real outlet branding directly" rule):

| Journalist | Outlet | Variable |
|---|---|---|
| Owen Meredith | Red Dragon Dispatch | `var(--dispatch-blue)` (pre-existing) |
| Keeyvon Jenkins | The Hawk's Nest | `var(--journal-accent)` (pre-existing) |
| Oliver Hargreaves | Sky Sports | `var(--hargreaves-accent)` — slate blue-grey |
| Rebecca Holt | BBC Sport | `var(--holt-accent)` — muted green |
| James McAllister | The Athletic | `var(--mcallister-accent)` — muted purple |
| Marco Bellini | Gazzetta dello Sport | `var(--bellini-accent)` — terracotta |
| Tara Bennett | ESPN FC | `var(--bennett-accent)` — teal |
| Darren Cole | Sky Sports (pundit) | `var(--cole-accent)` — brick red-brown |

---

### Journalist Personas

Condensed public bios live in `media-personalities.json`; this section is the writer's-room
guidance for staying in voice session to session.

**Oliver Hargreaves (Sky Sports)** — Authoritative, historical, never sensational. Only appears
for genuine milestones. His job is to answer "why does this matter, historically" — always with
a real comparison (another club, another manager, another era), never just hype. Ends pieces on
a measured, non-committal note about the future ("this doesn't guarantee X, but it has already
earned Y").

**Rebecca Holt (BBC Sport)** — Objective, fast, plain-spoken. Breaking news and confirmations:
transfers, official announcements, results as they land. No opinion, no color commentary — the
driest, most factual voice in the Media Centre. Good for the "Press Conferences" and breaking-news
side of a milestone (e.g., the club's official statement on a departure) rather than analysis.

**James McAllister (The Athletic)** — Dense, data-informed, tactically literate. Writes about
*how* something happened, not just that it did: a formation tweak, a recruitment pattern, a
development-pathway story. Genuinely admires the club's process rather than the results alone.
Good home for "Tactical Analysis" pieces — a back-line reshuffle, an academy-to-first-team
pipeline story, a transfer-market rationale.

**Marco Bellini (Gazzetta dello Sport)** — Romantic, literary, prone to grand continental
comparisons. Writes Wrexham's story as myth more than results service — good for "International
Reaction" after a European-adjacent moment (a continental opponent in a friendly/cup draw, transfer
interest from an Italian club, a big European name commenting on Wrexham). Leans into the fairytale
angle harder than any domestic writer would allow themselves to.

**Tara Bennett (ESPN FC)** — Warm, U.S.-audience-facing, tracks Keeyvon Jenkins' own story as much
as the club's. Good for "International Reaction" pieces with an explicitly American angle — U.S.
players/coaches in the league, Jenkins' USMNT background resurfacing, American ownership/investment
storylines. Sympathetic but not blind to setbacks.

**Darren Cole (Sky Sports pundit)** — Blunt, combative, built for a TV-debate quote format rather
than flowing prose (short paragraphs, direct claims, a clear position). The necessary skeptic —
questions sustainability, revisits his own past predictions, is willing to be proven wrong on air.
Every few appearances, have him acknowledge (grudgingly) when results have contradicted him — that
tension is the point, same as the Hawk's Nest/Dispatch friction in `JOURNAL_STYLE_GUIDE.md`.

**Cross-linking:** when a milestone produces both a Dispatch entry in `journal.html` and a Media
Centre piece the same session, it's fine (not required) for the Dispatch to mention the outside
coverage in passing ("Sky Sports called it...") — mirrors how the real Media Centre philosophy
wants coverage to feel like one ecosystem, not siloed pages. Don't force it every time.
