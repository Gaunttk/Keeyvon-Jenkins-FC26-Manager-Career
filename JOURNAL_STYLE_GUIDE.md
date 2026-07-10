# Journal Style Guide

Read this file when a session is writing journal entries for `docs/journal.html` (or an archived `docs/journal/season-NN.html`). Not needed for squad-only, stats-only, or squad-sync sessions — see `CLAUDE.md` for those.

---

### Journal: "The Hawk's Journey" — Two-Voice System

The journal is styled like a recurring publication. Entries are added **newest first**, each session producing a pair: one Dispatch, one Journal.

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
    <div class="entry-date">DATE · LOCATION</div>
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

**Season markers** go between date groups:
```html
<div class="season-marker">
  <span class="season-marker-text">Matchday 1 · August 2025</span>
  <div class="season-marker-line"></div>
  <span class="season-badge">Aug 9, 2025</span>
</div>
```

**Entry divider** between Dispatch and Journal pairs:
```html
<div class="entry-divider"></div>
```

---

### Owen Meredith — Dispatch Journalist Persona

Owen Meredith is the named journalist behind the Red Dragon Dispatch. He is the **external voice** — the outside world's view of Jenkins and Wrexham.

- **Bio:** Wrexham-born, 34. Covered the club since League Two for WalesOnline. Joined The Athletic UK desk in 2023. Has complicated feelings about the Hollywood era: loves what it did for the club financially, quietly mourns something he can't name.
- **Voice:** Skeptical but fair. Not hostile to Jenkins, but not a cheerleader. Asks the questions the pressroom won't.
- **Running thesis across the season:** *Can an American coach, hired by American owners, win an English football league with a Welsh club? And what gets lost if he does?*
- **Dispatch sections:** `Match Coverage` / `Inside the Club` / `Feature` / `Transfer Window` / `Season Review`
- **Athletic formula:** Open with a scene, not the result. Use the specific to illuminate the universal. Build running threads across entries. End with an open question.

**The two voices should occasionally contradict.** Jenkins thinks a training session went well; Meredith reports the captain looked disinterested. That friction is the story.

---

### What to Capture Each Session for Good Journalism

- Result + score + goalscorers if visible in screenshots
- Any screenshot of squad morale, manager confidence, board pressure, or league table
- One sentence vibe: "scraped it" / "comfortable" / "a mess" / "got hammered"
- Any transfers, injuries, or notable tactical changes

The more context provided, the richer the narrative. Fiction is never added — only what FC26 shows.
