# Journal Style Guide

Read this file when a session is writing journal entries for `docs/journal.html` (or an archived `docs/journal/season-NN.html`). Not needed for squad-only, stats-only, or squad-sync sessions — see `CLAUDE.md` for those.

**Authoring mechanism (as of the Media Centre build):** `docs/journal.html`'s entry stream and
sidebar TOC are no longer hand-typed HTML — they're generated from `media-articles.json` by
`scripts/generate_media_pages.py`, the same system that powers the Media Centre. **Never edit the
`<article>` markup in `docs/journal.html` directly** — it will be overwritten the next time the
script runs. Instead: add a new object to `media-articles.json` (at index 0, so it renders newest-first
— see "Voice 1" / "Voice 2" below for the exact field shapes), then run:

```
python3 scripts/generate_media_pages.py
```

Everything else in this guide — cadence, voice, persona, quotes, length — is unchanged. Only the
*mechanism* for getting an entry onto the page changed, not what a good entry looks like. Full JSON
schema reference lives in `MEDIA_STYLE_GUIDE.md`; this file keeps the example shapes for Owen and
Keeyvon's entries specifically since those two voices are this file's whole scope.

---

### Journal: "The Hawk's Journey" — Two-Voice System

The journal is styled like a recurring publication. Entries are added **newest first** — meaning new `media-articles.json` objects go at the top of the array (index 0).

**Cadence — read this before writing anything:**
- **Red Dragon Dispatch (Owen Meredith):** every session, same as always — one per match/session.
- **The Hawk's Nest (Keeyvon's private journal):** **monthly, not per-session.** Only write a Hawk's Nest entry when roughly an in-game month has passed since the last one (about every 4–5 matchdays), and check what the most recent `Entry NNN` journal-voice entry's date was before deciding whether one is due this session. When it is due, it should reflect on the whole stretch since the last entry — the arc of results, form, mood — not just the most recent match. Most sessions will publish a Dispatch only, with no paired Journal entry.

**Length and depth — match entries should run roughly twice as long as the earliest examples in this file.** Aim for 4–6 body paragraphs on a Dispatch (not 2), each doing real work — buildup/scene-setting, match detail, a tactical or squad-building angle, a quote-driven beat, and a forward-looking close. Thin, single-angle recaps read as unfinished; use the extra room for a second thread (a subplot, a second player's story, a running club-wide theme) rather than padding the same point.

**Quotes — every match entry should carry multiple direct quotes, not just the one `pull-quote`.** Weave at least one additional quote (manager, a player, a club source, an opposition voice, a fan/pressroom line) into the body prose itself, in quotation marks with attribution, alongside the pulled-out `pull-quote` block. Only use quotes consistent with what the screenshots/session input actually show or what a plausible in-universe voice would say post-match — these are dramatized but should never contradict confirmed results or events.

**Voice 1 — The Hawk's Nest (private journal).** Add this shape to `media-articles.json`:
```json
{
  "id": "entry-099",
  "author_id": "keeyvon-jenkins",
  "content_type": "diary",
  "date": "YYYY-MM-DD",
  "entry_number": "Entry 099",
  "date_line": "DATE · Wrexham",
  "sig_date": "DATE",
  "headline": "TITLE",
  "dek": "DEK — one punchy line.",
  "tags": [],
  "featured": false,
  "body_html": "<p>...</p><div class=\"pull-quote\"><p>QUOTE</p></div><p><em>— KJ</em></p>"
}
```
The generator renders this into the exact same `<article class="entry journal">` / `.journal-sig`
markup the page has always used — only the authoring step moved from hand-typed HTML to this object.

**Voice 2 — The Red Dragon Dispatch (journalist Owen Meredith).** Add this shape to `media-articles.json`:
```json
{
  "id": "entry-slug",
  "author_id": "owen-meredith",
  "content_type": "dispatch",
  "date": "YYYY-MM-DD",
  "section": "SECTION",
  "competition": "EFL Championship",
  "season": "Season 2025–26",
  "date_line": "<img src=\"assets/photos/crests/LEAGUE-FOLDER/256x256/OPPONENT-SLUG.football-logos.cc.png\" class=\"opponent-crest\" alt=\"OPPONENT\"> DATE · LOCATION",
  "headline": "HEADLINE",
  "dek": "DEK",
  "tags": [],
  "featured": false,
  "body_html": "<p>...</p><div class=\"context-card\">...</div><div class=\"pull-quote\"><p>QUOTE</p><span class=\"pull-quote-attr\">— ATTRIBUTION</span></div>"
}
```
Same idea: `section` fills the `Red Dragon Dispatch · SECTION` badge and byline, `competition`/`season`
fill the `byline-club` block, and `body_html` can freely use `context-card` (with `danger`/`safe`/`progress`
value classes) and `pull-quote` exactly as before — those are just HTML fragments inserted verbatim.

**Opponent crest — every match Dispatch entry gets the opposing club's logo**, inline in the `entry-date` line (see markup above; the `.opponent-crest` CSS rule lives in `docs/assets/style.css`, do not inline-style it). Source the image from the existing crest library at `docs/assets/photos/crests/` (mirrors the convention in `docs/index.html`'s standings table):
- Premier League clubs: `assets/photos/crests/english-premier-league-2026-2027.football-logos.cc/256x256/CLUB-SLUG.football-logos.cc.png`
- Some PL-adjacent clubs (West Ham, Sheffield Utd, Wolves, Wrexham) actually live in the EFL folder: `assets/photos/crests/england-efl-championship-2026-2027.football-logos.cc/256x256/CLUB-SLUG.football-logos.cc.png`
- Wrexham's own crest (for entries about the club itself, not an opponent) is at `assets/photos/crests/wrexham-crest.png`
- Non-league opponents (Youth Rush academy sides, friendly opposition without a crest file) — skip the image rather than inventing a path; a missing `<img>` src is worse than no crest.
- Check the folder before writing the path — filenames don't always match the obvious slug (e.g. `manchester-city`, not `man-city`).

**Season markers** go between date groups. Add a `marker` field to the *first* `media-articles.json`
entry of a new competition/round — the generator renders the divider immediately before that entry:
```json
"marker": { "text": "Matchday 1 · August 2025", "date_label": "Aug 9, 2025" }
```
Leave `marker` off every entry after the first in the same group.

**Entry divider** — the generator inserts one automatically whenever two adjacent entries (in
`media-articles.json` array order) share the same `date` but different `content_type` — i.e. a
Dispatch and a Hawk's Nest entry published together on the (now less common) monthly-cadence
sessions. Nothing to add by hand; just make sure both entries have the same `date` value.

---

### Owen Meredith — Dispatch Journalist Persona

Owen Meredith is the named journalist behind the Red Dragon Dispatch. He is the **external voice** — the outside world's view of Jenkins and Wrexham.

- **Bio:** Wrexham-born, 34. Covered the club since League Two for WalesOnline. Joined The Athletic UK desk in 2023. Has complicated feelings about the Hollywood era: loves what it did for the club financially, quietly mourns something he can't name.
- **Voice:** Skeptical but fair. Not hostile to Jenkins, but not a cheerleader. Asks the questions the pressroom won't.
- **Running threads — rotate through these, don't lean on one:** the "American coach, American owners" question is one thread in Meredith's back pocket, not his whole personality. Don't open with it, and don't reach for it more than occasionally. Other threads to draw on instead:
  - Welsh identity vs. the global Hollywood-brand version of the club
  - Academy graduates breaking through vs. money spent on marquee signings
  - Whether promotion (or a bad run) vindicates or exposes the ownership's data-driven approach
  - The pressroom's mood swinging with results — patience wearing thin, or goodwill returning
  - What the town itself makes of a club now watched worldwide
  - Jenkins's own transition from player to manager, and what that cost him
  - The America angle, when it does come up: vary the framing each time (a specific incident, a fan's comment, a boardroom decision) rather than repeating the same "can an American win an English league" line
- **Dispatch sections:** `Match Coverage` / `Inside the Club` / `Feature` / `Transfer Window` / `Season Review`
- **Athletic formula:** Open with a scene, not the result. Use the specific to illuminate the universal. Build running threads across entries — but rotate which thread, don't default to the same one. End with an open question.

**The two voices should occasionally contradict.** Jenkins thinks a training session went well; Meredith reports the captain looked disinterested. That friction is the story.

---

### What to Capture Each Session for Good Journalism

- Result + score + goalscorers if visible in screenshots
- Any screenshot of squad morale, manager confidence, board pressure, or league table
- One sentence vibe: "scraped it" / "comfortable" / "a mess" / "got hammered"
- Any transfers, injuries, or notable tactical changes

The more context provided, the richer the narrative. Fiction is never added — only what FC26 shows.
