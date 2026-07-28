# Journal Style Guide

Read this file when a session is writing journal entries for `docs/journal.html` (or an archived `docs/journal/season-NN.html`). Not needed for squad-only, stats-only, or squad-sync sessions — see `CLAUDE.md` for those.

---

### Journal: "The Hawk's Journey" — Two-Voice System

The journal is styled like a recurring publication. Entries are added **newest first**.

**Cadence — read this before writing anything:**
- **Red Dragon Dispatch (Owen Meredith):** every session, same as always — one per match/session.
- **The Hawk's Nest (Keeyvon's private journal):** **monthly, not per-session.** Only write a Hawk's Nest entry when roughly an in-game month has passed since the last one (about every 4–5 matchdays), and check what the most recent `Entry NNN` journal-voice entry's date was before deciding whether one is due this session. When it is due, it should reflect on the whole stretch since the last entry — the arc of results, form, mood — not just the most recent match. Most sessions will publish a Dispatch only, with no paired Journal entry.

**Length and depth — match entries should run roughly twice as long as the earliest examples in this file.** Aim for 4–6 body paragraphs on a Dispatch (not 2), each doing real work — buildup/scene-setting, match detail, a tactical or squad-building angle, a quote-driven beat, and a forward-looking close. Thin, single-angle recaps read as unfinished; use the extra room for a second thread (a subplot, a second player's story, a running club-wide theme) rather than padding the same point.

**Quotes — every match entry should carry multiple direct quotes, not just the one `pull-quote`.** Weave at least one additional quote (manager, a player, a club source, an opposition voice, a fan/pressroom line) into the body prose itself, in quotation marks with attribution, alongside the pulled-out `pull-quote` block. Only use quotes consistent with what the screenshots/session input actually show or what a plausible in-universe voice would say post-match — these are dramatized but should never contradict confirmed results or events.

**Voice 1 — The Hawk's Nest (private journal):**
```html
<article class="entry journal">
  <div class="entry-header">
    <div class="entry-type-badge journal-badge">The Hawk's Nest · Private Journal</div>
    <div class="entry-number">Entry 003</div>
    <div class="entry-date">DATE · Wrexham</div>
    <h2 class="entry-title">TITLE</h2>
    <p class="entry-dek">DEK — one punchy line.</p>
  </div>
  <div class="entry-body">
    <p>...</p>
    <div class="pull-quote"><p>QUOTE</p></div>
    <p><em>— KJ</em></p>
  </div>
  <div class="journal-sig">
    <div class="sig-initials">KJ</div>
    <div class="sig-text">
      <strong>Keeyvon Jenkins</strong>
      Head Coach · Wrexham AFC · DATE
    </div>
  </div>
</article>
```

**Voice 2 — The Red Dragon Dispatch (journalist Owen Meredith):**
```html
<article class="entry dispatch">
  <div class="entry-header">
    <div class="entry-type-badge dispatch-badge">Red Dragon Dispatch · SECTION</div>
    <div class="entry-date"><img src="assets/photos/crests/LEAGUE-FOLDER/256x256/OPPONENT-SLUG.football-logos.cc.png" class="opponent-crest" alt="OPPONENT"> DATE · LOCATION</div>
    <h2 class="entry-title dispatch-title">HEADLINE</h2>
    <p class="entry-dek">DEK</p>
  </div>
  <div class="entry-body">
    <p>...</p>
    <div class="context-card">
      <div class="context-card-label">LABEL</div>
      <div class="context-card-row">
        <span class="context-card-key">KEY</span>
        <span class="context-card-val danger|safe|progress">VALUE</span>
      </div>
    </div>
    <div class="pull-quote">
      <p>QUOTE</p>
      <span class="pull-quote-attr">— ATTRIBUTION</span>
    </div>
  </div>
  <div class="dispatch-byline">
    <div class="byline-left">
      <strong>Owen Meredith · The Red Dragon Dispatch</strong>
      SECTION LABEL
    </div>
    <div class="byline-club">
      <strong>EFL Championship</strong>
      Season 2025–26
    </div>
  </div>
</article>
```

**Opponent crest — every match Dispatch entry gets the opposing club's logo**, inline in the `entry-date` line (see markup above; the `.opponent-crest` CSS rule lives in `docs/assets/style.css`, do not inline-style it). Source the image from the existing crest library at `docs/assets/photos/crests/` (mirrors the convention in `docs/index.html`'s standings table):
- Premier League clubs: `assets/photos/crests/english-premier-league-2026-2027.football-logos.cc/256x256/CLUB-SLUG.football-logos.cc.png`
- Some PL-adjacent clubs (West Ham, Sheffield Utd, Wolves, Wrexham) actually live in the EFL folder: `assets/photos/crests/england-efl-championship-2026-2027.football-logos.cc/256x256/CLUB-SLUG.football-logos.cc.png`
- Wrexham's own crest (for entries about the club itself, not an opponent) is at `assets/photos/crests/wrexham-crest.png`
- Non-league opponents (Youth Rush academy sides, friendly opposition without a crest file) — skip the image rather than inventing a path; a missing `<img>` src is worse than no crest.
- Check the folder before writing the path — filenames don't always match the obvious slug (e.g. `manchester-city`, not `man-city`).

**Season markers** go between date groups:
```html
<div class="season-marker">
  <span class="season-marker-text">Matchday 1 · August 2025</span>
  <div class="season-marker-line"></div>
  <span class="season-badge">Aug 9, 2025</span>
</div>
```

**Entry divider** — only needed on the (now less common) sessions where both a Dispatch and a Hawk's Nest entry are published together (the monthly cadence hit). On ordinary sessions there's just a single Dispatch entry with no divider:
```html
<div class="entry-divider"></div>
```

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
