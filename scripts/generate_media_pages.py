"""Regenerate the Media Centre pages (docs/media/*) and docs/journal.html's
entry stream from media-personalities.json / media-articles.json.

Run this after any edit to either JSON file:
    python3 scripts/generate_media_pages.py

Source of truth: media-personalities.json (journalist/author profiles) and
media-articles.json (every article/entry, both Media Centre pieces and the
journal's Dispatch/Diary entries). This script never edits the JSON files —
only derived HTML under docs/.

Media Centre architecture (Phase 2 — the newsroom redesign):
  docs/media/index.html   — JS-rendered newsroom front page (lead, latest
                             feed, categories, Press Corps, Hawk's Nest,
                             publications, archive teaser). Mirrors
                             docs/index.html's own pattern: this script only
                             emits the static shell + empty containers;
                             docs/assets/media.js fills them in at load time
                             from docs/assets/media_index.js, so the page
                             keeps working offline (file://) and never
                             duplicates article bodies into HTML.
  docs/media/archive.html — full, server-rendered listing of every article
                             (always works with JS off), progressively
                             enhanced with category/author/season filters
                             and a text search over already-rendered rows.
  docs/media/journalists.html — server-rendered Press Corps profile page.
  docs/media/articles/*.html  — server-rendered article pages (need the full
                             body_html, which never goes into media_index.js).

Two small presentational fields, `image` / `image_alt`, are supported (but
optional) on media-articles.json entries — the article's hero photo, an
editorial choice exactly like docs/assets/home_config.js's image picks, never
a fabricated football fact. An article with neither renders with graceful
fallbacks (a journalist-initials avatar, no hero image slot) rather than a
broken layout — see "Empty / Missing Data States" in the Phase 2 brief.
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
JOURNAL_HTML = DOCS / "journal.html"
MEDIA_DIR = DOCS / "media"
ARTICLES_DIR = MEDIA_DIR / "articles"

JOURNAL_CONTENT_TYPES = {"dispatch", "diary"}

MARK_ENTRIES_START = "<!-- MEDIA:JOURNAL:ENTRIES:START -->"
MARK_ENTRIES_END = "<!-- MEDIA:JOURNAL:ENTRIES:END -->"
MARK_TOC_START = "<!-- MEDIA:JOURNAL:TOC:START -->"
MARK_TOC_END = "<!-- MEDIA:JOURNAL:TOC:END -->"


def load_data():
    people = json.loads((ROOT / "media-personalities.json").read_text(encoding="utf-8"))
    articles = json.loads((ROOT / "media-articles.json").read_text(encoding="utf-8"))
    people_by_id = {p["id"]: p for p in people}
    for a in articles:
        if a["author_id"] not in people_by_id:
            raise SystemExit(f"Article {a['id']!r} has unknown author_id {a['author_id']!r}")
    return people, people_by_id, articles


def replace_between(html_text, start_marker, end_marker, new_inner):
    pattern = re.compile(re.escape(start_marker) + r".*?" + re.escape(end_marker), re.DOTALL)
    if not pattern.search(html_text):
        raise SystemExit(f"Could not find marker pair {start_marker!r} / {end_marker!r}")
    return pattern.sub(start_marker + "\n" + new_inner + "\n" + end_marker, html_text, count=1)


def attr(s):
    """Escape a string for safe use inside an HTML attribute."""
    return html.escape(str(s or ""), quote=True)


# ---------------------------------------------------------------------------
# journal.html regeneration (unchanged by Phase 2 — journal.html is out of
# scope for the Media Centre redesign)
# ---------------------------------------------------------------------------

def render_dispatch_entry(a):
    return (
        f'<article class="entry dispatch" id="{a["id"]}">\n'
        f'  <div class="entry-header">\n'
        f'    <div class="entry-type-badge dispatch-badge">Red Dragon Dispatch · {a["section"]}</div>\n'
        f'    <div class="entry-date">{a["date_line"]}</div>\n'
        f'    <h2 class="entry-title dispatch-title">{a["headline"]}</h2>\n'
        f'    <p class="entry-dek">{a["dek"]}</p>\n'
        f'  </div>\n'
        f'  <div class="entry-body">\n'
        f'    {a["body_html"]}\n'
        f'  </div>\n'
        f'  <div class="dispatch-byline">\n'
        f'    <div class="byline-left">\n'
        f'      <strong>Owen Meredith · The Red Dragon Dispatch</strong>\n'
        f'      {a["section"]}\n'
        f'    </div>\n'
        f'    <div class="byline-club">\n'
        f'      <strong>{a["competition"]}</strong>\n'
        f'      {a["season"]}\n'
        f'    </div>\n'
        f'  </div>\n'
        f'</article>'
    )


def render_diary_entry(a):
    return (
        f'<article class="entry journal" id="{a["id"]}">\n'
        f'  <div class="entry-header">\n'
        f'    <div class="entry-type-badge journal-badge">The Hawk\'s Nest · Private Journal</div>\n'
        f'    <div class="entry-number">{a["entry_number"]}</div>\n'
        f'    <div class="entry-date">{a["date_line"]}</div>\n'
        f'    <h2 class="entry-title">{a["headline"]}</h2>\n'
        f'    <p class="entry-dek">{a["dek"]}</p>\n'
        f'  </div>\n'
        f'  <div class="entry-body">\n'
        f'    {a["body_html"]}\n'
        f'  </div>\n'
        f'  <div class="journal-sig">\n'
        f'    <div class="sig-initials">KJ</div>\n'
        f'    <div class="sig-text">\n'
        f'      <strong>Keeyvon Jenkins</strong>\n'
        f'      Head Coach · Wrexham AFC · {a["sig_date"]}\n'
        f'    </div>\n'
        f'  </div>\n'
        f'</article>'
    )


def render_marker(marker):
    return (
        f'<div class="season-marker">\n'
        f'  <span class="season-marker-text">{marker["text"]}</span>\n'
        f'  <div class="season-marker-line"></div>\n'
        f'  <span class="season-badge">{marker["date_label"]}</span>\n'
        f'</div>'
    )


def build_journal_stream(journal_articles):
    """journal_articles: dispatch/diary entries, newest first (already sorted)."""
    blocks = []
    prev = None
    for a in journal_articles:
        if a.get("marker"):
            blocks.append(render_marker(a["marker"]))
        elif prev is not None and prev["date"] == a["date"] and prev["content_type"] != a["content_type"]:
            blocks.append('<div class="entry-divider"></div>')
        blocks.append(render_dispatch_entry(a) if a["content_type"] == "dispatch" else render_diary_entry(a))
        prev = a
    return "\n\n".join(blocks)


def build_journal_toc(journal_articles):
    items = []
    for a in journal_articles:
        num_label = "Dispatch" if a["content_type"] == "dispatch" else a["entry_number"]
        date_label = _format_toc_date(a["date"])
        items.append(
            f'  <a href="#{a["id"]}" class="toc-item">\n'
            f'    <span class="toc-num">{num_label}</span>\n'
            f'    <span class="toc-title">{a["headline"]}</span>\n'
            f'    <span class="toc-date">{date_label}</span>\n'
            f'  </a>'
        )
    return "\n".join(items)


_MONTH_ABBR = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def _format_toc_date(iso_date):
    y, m, d = iso_date.split("-")
    return f"{_MONTH_ABBR[int(m) - 1]} {int(d)}, {y}"


def regenerate_journal_html(articles):
    # Preserve media-articles.json's own ordering (newest-first, same convention as the
    # old hand-typed journal.html) rather than re-sorting by date — entries from the same
    # real-world session are sometimes interleaved by narrative/competition rather than
    # strict chronological order, and that curated order lives in the array position.
    journal_articles = [a for a in articles if a["content_type"] in JOURNAL_CONTENT_TYPES]

    html_text = JOURNAL_HTML.read_text(encoding="utf-8")
    html_text = replace_between(html_text, MARK_ENTRIES_START, MARK_ENTRIES_END, build_journal_stream(journal_articles))
    html_text = replace_between(html_text, MARK_TOC_START, MARK_TOC_END, build_journal_toc(journal_articles))
    JOURNAL_HTML.write_text(html_text, encoding="utf-8")
    print(f"Regenerated {JOURNAL_HTML.relative_to(ROOT)} ({len(journal_articles)} entries)")


# ---------------------------------------------------------------------------
# Shared metadata: categories, seasons, related-article scoring
# ---------------------------------------------------------------------------

def derive_category(a):
    """Map an article's content_type/section onto a small, maintainable
    category taxonomy driven entirely by the real data already on each
    article — never a hand-typed per-article label. New articles inherit a
    category automatically the moment they're added to media-articles.json."""
    ct = a["content_type"]
    section = a.get("section") or ""
    text = ((a.get("headline") or "") + " " + (a.get("dek") or "")).lower()

    if ct == "diary":
        return ("hawks-nest", "Hawk's Nest")
    if ct == "dispatch":
        if section == "Transfer Window":
            return ("transfers", "Transfers")
        return ("match-reports", "Match Reports")
    if ct == "feature":
        return ("history", "History")
    if ct == "tactical":
        if "academy" in text or "youth rush" in text:
            return ("academy", "Academy")
        return ("analysis", "Analysis")
    if ct == "tv-debate":
        return ("opinion", "Opinion")
    if ct == "press-conference":
        return ("transfers", "Transfers")
    return ("coverage", "Coverage")


def derive_season(iso_date):
    """FC26 seasons run roughly August–May; anything from July onward counts
    toward the season that *starts* that year. Derived from the date rather
    than trusting the free-text `season` field (which has drifted between
    'Season 2026–27' / 'Season 2026&ndash;27' / '2026–27' in the data)."""
    y, m, _d = (int(x) for x in iso_date.split("-"))
    start_year = y if m >= 7 else y - 1
    return f"{start_year}/{str(start_year + 1)[-2:]}"


def related_articles(a, pool, limit=3):
    """Deterministic, metadata-based relationship scoring — see "Related
    Stories" in the Phase 2 brief. Never fabricates a relationship; ties
    break toward the most recent article so results stay stable as new
    articles are added."""
    tags = set(a.get("tags") or [])
    cat_slug = derive_category(a)[0]

    def score(o):
        s = 0
        if tags and (tags & set(o.get("tags") or [])):
            s += 4
        if o["author_id"] == a["author_id"]:
            s += 2
        if o.get("section") and o.get("section") == a.get("section"):
            s += 2
        if derive_category(o)[0] == cat_slug:
            s += 1
        return s

    candidates = [o for o in pool if o["id"] != a["id"]]
    candidates.sort(key=lambda o: o["date"], reverse=True)
    candidates.sort(key=score, reverse=True)
    return [o for o in candidates if score(o) > 0][:limit]


# ---------------------------------------------------------------------------
# Shared page chrome — the approved Jenkins Era masthead/nav and footer,
# reused verbatim (same markup/classes as docs/index.html) so Media Centre
# pages visibly belong to the same site. See style.css's "MEDIA CENTRE" block
# for how `.home-body` tokens (`--h-*`) get inherited here.
# ---------------------------------------------------------------------------

def home_nav(depth):
    prefix = "../" * depth
    return f"""<header class="home-header">
  <div class="home-header-inner">
    <a class="home-brand" href="{prefix}index.html">
      <img class="home-brand-crest" src="{prefix}assets/photos/wrexham-crest.png" alt="Wrexham AFC crest">
      <span class="home-brand-text">
        <span class="home-brand-title">The Jenkins Era</span>
        <span class="home-brand-sub">Wrexham AFC &middot; The Keevyon Jenkins Years</span>
      </span>
    </a>
    <div class="home-header-meta">
      <span class="home-header-season">Season 2026&ndash;27</span>
      <span class="home-header-comp">Premier League</span>
    </div>
  </div>

  <nav class="home-primary-nav" aria-label="Primary">
    <div class="home-primary-nav-inner">
      <a href="{prefix}index.html" class="home-nav-link">Home</a>
      <a href="{prefix}media/index.html" class="home-nav-link is-active" aria-current="page">News</a>
      <a href="{prefix}season.html" class="home-nav-link">Matches</a>
      <a href="{prefix}roster.html" class="home-nav-link">Squad</a>
      <a href="{prefix}academy.html" class="home-nav-link">Academy</a>
      <a href="{prefix}history.html" class="home-nav-link">The Jenkins Era</a>
      <a href="{prefix}season.html#player-stats" class="home-nav-link">Stats</a>
    </div>
  </nav>

  <nav class="home-utility-nav" aria-label="Secondary">
    <div class="home-utility-nav-inner">
      <a href="{prefix}depth_chart.html">Depth Chart</a>
      <a href="{prefix}dossier.html">Manager Profile</a>
      <a href="{prefix}history.html">Season Archive</a>
      <a href="{prefix}journal.html">Journal</a>
      <a href="{prefix}season_preview.html">Season Preview</a>
      <a href="{prefix}submit.html" class="home-utility-submit">Submit Data</a>
    </div>
  </nav>
</header>"""


def home_footer(depth):
    prefix = "../" * depth
    return f"""<footer class="home-footer">
  <div class="home-footer-inner">
    <div class="home-footer-brand">
      <img class="home-footer-crest" src="{prefix}assets/photos/wrexham-crest.png" alt="">
      <div>
        <span class="home-footer-title">The Jenkins Era</span>
        <span class="home-footer-sub">Wrexham AFC &middot; The Keevyon Jenkins Years</span>
      </div>
    </div>
    <nav class="home-footer-links" aria-label="Footer">
      <a href="{prefix}media/index.html">Media Centre</a>
      <a href="{prefix}journal.html">Journal</a>
      <a href="{prefix}season.html">Season</a>
      <a href="{prefix}roster.html">Squad</a>
      <a href="{prefix}depth_chart.html">Depth Chart</a>
      <a href="{prefix}academy.html">Academy</a>
      <a href="{prefix}history.html">History</a>
      <a href="{prefix}dossier.html">Manager Profile</a>
      <a href="{prefix}season_preview.html">Season Preview</a>
      <a href="{prefix}submit.html">Submit Data</a>
    </nav>
    <p class="home-footer-disclosure">An FC26 career-mode history project documenting the fictional managerial
      career of Keevyon Jenkins at Wrexham AFC. Not affiliated with, endorsed by, or connected to Wrexham AFC,
      the Premier League, the EFL, EA Sports, or any broadcaster or publication. Journalists, articles and
      match events on this site are fictional.</p>
  </div>
</footer>"""


def page_shell(depth, title, description, body_class, shell_class, main_html, extra_scripts=""):
    prefix = "../" * depth
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{attr(description)}">
<link rel="stylesheet" href="{prefix}assets/style.css">
<link rel="manifest" href="{prefix}manifest.json">
<meta name="theme-color" content="#C8102E">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="WRXM FC26">
<link rel="apple-touch-icon" href="{prefix}assets/icons/icon-192.png">
<script>
if ('serviceWorker' in navigator) {{
  window.addEventListener('load', () => {{
    navigator.serviceWorker.register('/Keeyvon-Jenkins-FC26-Manager-Career/sw.js');
  }});
}}
</script>
</head>
<body class="home-body {body_class}">

{home_nav(depth)}

<main class="{shell_class}" id="mc-main">
{main_html}
</main>

{home_footer(depth)}
{extra_scripts}
</body>
</html>
"""


def person_avatar(person, depth, img_cls, mono_cls):
    initials = "".join(w[0] for w in person["name"].split()[:2]).upper()
    if person.get("headshot"):
        prefix = "../" * depth
        return f'<img class="{img_cls}" src="{prefix}{person["headshot"]}" alt="{attr(person["name"])}">'
    return f'<div class="{mono_cls}" style="background:{person["accent_color"]}">{initials}</div>'


# ---------------------------------------------------------------------------
# docs/assets/media_index.js — metadata-only snapshot for the homepage AND
# the Media Centre's own client-rendered sections (index.html's lead/feed/
# Press Corps/Hawk's Nest/publications all read this at load time).
# ---------------------------------------------------------------------------

def render_media_index_js(people, people_by_id, articles):
    """Emit a small generated JS index of article *metadata* (never bodies).

    Both docs/index.html and docs/media/index.html work as local file://
    pages, so neither can fetch media-articles.json at runtime. This gives
    them headline/dek/byline/category/image/URL for any article, keyed by
    the same ids used in media-articles.json.

    Paths in `url`, `image` and `headshot` are relative to docs/.
    """
    def url_for(a):
        if a["content_type"] in JOURNAL_CONTENT_TYPES:
            return f'journal.html#{a["id"]}'
        return f'media/articles/{a["id"]}.html'

    media_articles = [a for a in articles if a["content_type"] not in JOURNAL_CONTENT_TYPES]
    press_articles = [a for a in media_articles if people_by_id[a["author_id"]]["is_press"]]

    # Coverage categories, counted off the real data — never a fixed list.
    cat_counts = {}
    cat_order = []
    for a in media_articles:
        slug, label = derive_category(a)
        if slug not in cat_counts:
            cat_counts[slug] = 0
            cat_order.append((slug, label))
        cat_counts[slug] += 1
    categories = [{"slug": slug, "label": label, "count": cat_counts[slug]} for slug, label in cat_order]

    # Publications ("Voices Across Football") — grouped by outlet, press only.
    pubs = {}
    pub_order = []
    for a in sorted(press_articles, key=lambda a: a["date"]):
        outlet = a.get("outlet") or people_by_id[a["author_id"]]["outlet"]
        if outlet not in pubs:
            pubs[outlet] = {"name": outlet, "count": 0, "latest_id": None, "latest_date": None}
            pub_order.append(outlet)
        pubs[outlet]["count"] += 1
        pubs[outlet]["latest_id"] = a["id"]
        pubs[outlet]["latest_date"] = a["date"]
    publications = sorted((pubs[o] for o in pub_order), key=lambda p: p["latest_date"], reverse=True)

    seasons = sorted({derive_season(a["date"]) for a in articles}, reverse=True)

    payload = {
        "people": {
            p["id"]: {
                "name": p["name"],
                "outlet": p["outlet"],
                "role": p["role"],
                "is_press": p["is_press"],
                "accent_color": p["accent_color"],
                "headshot": p.get("headshot"),
                "bio": p.get("bio"),
            }
            for p in people
        },
        "people_order": [p["id"] for p in people],
        "articles": {
            a["id"]: {
                "id": a["id"],
                "headline": a["headline"],
                "dek": a.get("dek", ""),
                "date": a["date"],
                "date_label": _format_toc_date(a["date"]),
                "author_id": a["author_id"],
                "outlet": a.get("outlet") or people_by_id[a["author_id"]]["outlet"],
                "section": a.get("section"),
                "content_type": a["content_type"],
                "entry_number": a.get("entry_number"),
                "category": derive_category(a)[0],
                "category_label": derive_category(a)[1],
                "season": derive_season(a["date"]),
                "tags": a.get("tags", []),
                "featured": bool(a.get("featured")),
                "image": a.get("image"),
                "image_alt": a.get("image_alt"),
                "url": url_for(a),
            }
            for a in articles
        },
        "recent_ids": [a["id"] for a in sorted(articles, key=lambda a: a["date"], reverse=True)],
        "categories": categories,
        "publications": publications,
        "seasons": seasons,
    }

    blob = json.dumps(payload, ensure_ascii=False, indent=1)
    out = (
        "/* GENERATED FILE — do not edit by hand.\n"
        "   Rebuild with: python3 scripts/generate_media_pages.py\n"
        "   Metadata-only index of media-articles.json / media-personalities.json,\n"
        "   used by docs/index.html and docs/media/index.html (neither can fetch\n"
        "   JSON over file://). Article bodies deliberately live only in\n"
        "   media-articles.json. */\n"
        f"const MEDIA_INDEX = {blob};\n"
    )
    path = DOCS / "assets" / "media_index.js"
    path.write_text(out, encoding="utf-8")
    print(f"Wrote docs/assets/media_index.js ({len(payload['articles'])} articles, {len(people)} people)")


# ---------------------------------------------------------------------------
# docs/media/index.html — JS-rendered newsroom front page (static shell only)
# ---------------------------------------------------------------------------

def render_media_index(people, people_by_id, articles):
    main = """<div class="mc-intro">
  <div class="mc-intro-row">
    <div class="mc-intro-main">
      <div class="mc-intro-eyebrow"><span class="mc-live-dot" aria-hidden="true"></span>Season 2026&ndash;27 &middot; Live Coverage</div>
      <h1 class="mc-intro-title">Media <span>Centre</span></h1>
      <p class="mc-intro-sub">Reporting, analysis and opinion from across the football world documenting the Keevyon Jenkins era at Wrexham &mdash; Sky Sports, BBC Sport, The Athletic, Gazzetta dello Sport, ESPN FC, BBC Radio Wales, and the Racecourse's own Red Dragon Dispatch.</p>
    </div>
    <div class="mc-intro-stats" id="mc-intro-stats"></div>
  </div>
</div>

<section class="mc-section" aria-label="Lead stories">
  <div class="mc-lead-grid" id="mc-lead-grid"></div>
</section>

<section class="mc-section" aria-label="Coverage categories">
  <div class="mc-section-head"><h2>Coverage</h2></div>
  <div class="mc-cat-grid" id="mc-cat-grid"></div>
</section>

<section class="mc-section" aria-label="Latest from the newsroom">
  <div class="mc-section-head">
    <h2>Latest From the Newsroom</h2>
    <a class="mc-section-link" href="archive.html">Full archive &rarr;</a>
  </div>
  <div class="mc-filter-bar" id="mc-filter-bar" role="group" aria-label="Filter the newsroom feed by category"></div>
  <div class="mc-feed" id="mc-feed"></div>
  <div class="mc-feed-more"><a href="archive.html">View Full Archive &rarr;</a></div>
</section>

<section class="mc-section" aria-label="The Press Corps">
  <div class="mc-section-head">
    <h2>The Press Corps</h2>
    <a class="mc-section-link" href="journalists.html">All profiles &rarr;</a>
  </div>
  <div class="press-corps-grid" id="press-corps-grid"></div>
</section>

<section class="mc-section" aria-label="The Hawk's Nest">
  <div class="hawk-section">
    <div class="hawk-head">
      <h2>The Hawk&rsquo;s Nest</h2>
      <span class="hawk-tag">Private Journal &middot; Keeyvon Jenkins</span>
    </div>
    <p class="hawk-note">Not journalism &mdash; the manager's own record of the season, kept for himself.</p>
    <div class="hawk-entries" id="hawk-entries"></div>
    <a class="mc-section-link" href="../journal.html" style="display:inline-block;margin-top:18px;">Read the full journal &rarr;</a>
  </div>
</section>

<section class="mc-section" aria-label="Voices across football">
  <div class="mc-section-head"><h2>Voices Across Football</h2></div>
  <div class="mc-pub-grid" id="mc-pub-grid"></div>
</section>

<section class="mc-section" aria-label="Media archive">
  <div class="mc-section-head">
    <h2>Media Archive</h2>
    <a class="mc-section-link" href="archive.html">Browse all &rarr;</a>
  </div>
  <div class="mc-archive-teaser" id="mc-archive-teaser"></div>
</section>

<noscript>
  <p class="mc-empty">This page assembles its lead stories and feed from the project's own data files with a
    small script. With JavaScript off, browse directly: <a href="archive.html">Full Archive</a>,
    <a href="journalists.html">Journalist Profiles</a>.</p>
</noscript>"""
    html_out = page_shell(
        1, "Media Centre | The Jenkins Era",
        "The newsroom behind The Jenkins Era — reporting, analysis and opinion on Keevyon Jenkins' Wrexham from a fictional football press corps.",
        "mc-body", "mc-shell", main,
        extra_scripts='<script src="../assets/media_index.js"></script>\n<script src="../assets/media.js"></script>',
    )
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    (MEDIA_DIR / "index.html").write_text(html_out, encoding="utf-8")
    media_articles = [a for a in articles if a["content_type"] not in JOURNAL_CONTENT_TYPES]
    print(f"Wrote docs/media/index.html ({len(media_articles)} Media Centre articles)")


# ---------------------------------------------------------------------------
# docs/media/journalists.html — Press Corps profiles (server-rendered)
# ---------------------------------------------------------------------------

def render_journalists_page(people, people_by_id, articles):
    non_journal = sorted(
        (a for a in articles if a["content_type"] not in JOURNAL_CONTENT_TYPES),
        key=lambda a: a["date"], reverse=True,
    )
    by_author = {}
    for a in non_journal:
        by_author.setdefault(a["author_id"], []).append(a)
    diary_count = len([a for a in articles if a["content_type"] == "diary"])

    cards = []
    for p in people:
        arts = by_author.get(p["id"], [])
        n = len(arts) if p["is_press"] else diary_count
        avatar = person_avatar(p, 1, "press-avatar", "press-avatar-mono")
        specialties = ", ".join(p["specialties"])
        outlet_line = p["outlet"] if p["is_press"] else "The Hawk's Nest (Private Journal)"
        noun = "article" if p["is_press"] else "entry"
        noun_plural = "articles" if p["is_press"] else "entries"
        latest_line = (
            f'<p class="press-card-bio"><strong style="color:var(--white)">Latest:</strong> {arts[0]["headline"]}</p>'
            if arts else ""
        )
        cards.append(f"""<a class="press-card" id="{attr(p['id'])}" href="archive.html?author={attr(p['id'])}" style="border-top-color:{p['accent_color']}">
  <div class="press-card-top">
    {avatar}
    <div>
      <div class="press-card-name">{p['name']}</div>
      <div class="press-card-role">{p['role']} &middot; {outlet_line}</div>
    </div>
  </div>
  <p class="press-card-bio">{p['bio']}</p>
  <p class="press-card-bio"><strong style="color:var(--white)">Covers:</strong> {specialties}</p>
  <p class="press-card-bio"><strong style="color:var(--white)">On Wrexham:</strong> {p['relationship_with_wrexham']}</p>
  {latest_line}
  <div class="press-card-foot">
    <span class="press-card-count"><strong>{n}</strong> {noun if n == 1 else noun_plural}</span>
    <span class="press-card-cta">View coverage &rarr;</span>
  </div>
</a>""")

    main = f"""<div class="mc-intro">
  <h1 class="mc-intro-title">The Press <span>Corps</span></h1>
  <p class="mc-intro-sub">Every recurring voice covering Keeyvon Jenkins' Wrexham, fictional to a person, each with their own outlet, beat, and opinion of the club &mdash; plus Jenkins' own private journal, included here so it can share the same profile system without being mistaken for journalism.</p>
</div>
<section class="mc-section" aria-label="Journalist profiles">
  <div class="press-corps-grid">
{chr(10).join(cards)}
  </div>
</section>"""
    html_out = page_shell(
        1, "The Press Corps | Media Centre",
        "Every journalist and voice covering Wrexham AFC in The Jenkins Era's fictional media ecosystem.",
        "mc-body", "mc-shell", main,
    )
    (MEDIA_DIR / "journalists.html").write_text(html_out, encoding="utf-8")
    print(f"Wrote docs/media/journalists.html ({len(people)} profiles)")


# ---------------------------------------------------------------------------
# docs/media/archive.html — full archive, server-rendered + JS filters/search
# ---------------------------------------------------------------------------

def render_archive_page(people, people_by_id, articles):
    all_sorted = sorted(articles, key=lambda a: a["date"], reverse=True)

    cat_counts = {}
    cat_order = []
    for a in all_sorted:
        slug, label = derive_category(a)
        if slug not in cat_counts:
            cat_counts[slug] = 0
            cat_order.append((slug, label))
        cat_counts[slug] += 1

    seasons = sorted({derive_season(a["date"]) for a in all_sorted}, reverse=True)

    def filter_group(group_id, label, items):
        buttons = [f'<button type="button" class="mc-filter-btn is-active" data-value="all" aria-pressed="true">All</button>']
        for value, btn_label in items:
            buttons.append(
                f'<button type="button" class="mc-filter-btn" data-value="{attr(value)}" aria-pressed="false">{btn_label}</button>'
            )
        return f"""<div class="mc-archive-group" id="{group_id}">
      <span class="mc-archive-group-label">{label}</span>
      {"".join(buttons)}
    </div>"""

    cat_group = filter_group("mc-archive-cat-group", "Category", [(slug, f"{lbl} ({cat_counts[slug]})") for slug, lbl in cat_order])
    author_group = filter_group("mc-archive-author-group", "Journalist", [(p["id"], p["name"]) for p in people])
    season_group = filter_group("mc-archive-season-group", "Season", [(s, s) for s in seasons]) if len(seasons) > 1 else ""

    rows = []
    for a in all_sorted:
        person = people_by_id[a["author_id"]]
        if a["content_type"] in JOURNAL_CONTENT_TYPES:
            href = f'../journal.html#{a["id"]}'
        else:
            href = f'articles/{a["id"]}.html'
        outlet = a.get("outlet") or person["outlet"]
        slug, label = derive_category(a)
        search_blob = " ".join([
            a["headline"], a.get("dek", ""), person["name"], outlet, label,
        ]).lower()
        rows.append(f"""<a class="mc-archive-row" data-author="{attr(person['id'])}" data-category="{attr(slug)}" data-season="{attr(derive_season(a['date']))}" data-search="{attr(search_blob)}" href="{href}">
  <span class="mc-archive-row-date">{_format_toc_date(a['date'])}</span>
  <span class="mc-archive-row-title">{a['headline']}</span>
  <span class="mc-archive-row-meta">{person['name']} &middot; {outlet}</span>
</a>""")

    main = f"""<div class="mc-intro">
  <h1 class="mc-intro-title">Media <span>Archive</span></h1>
  <p class="mc-intro-sub">Every article and journal entry published so far, filterable by category, journalist and season &mdash; the historical record of how Wrexham's rise was reported at the time.</p>
</div>
<div class="mc-archive-controls">
  {cat_group}
  {author_group}
  {season_group}
  <input type="search" id="mc-archive-search" class="mc-search" placeholder="Search headlines, authors, outlets&hellip;" aria-label="Search the archive">
</div>
<div class="mc-archive-list">
{chr(10).join(rows)}
</div>
<p class="mc-archive-empty" id="mc-archive-empty" style="display:none;">No coverage matches these filters yet.</p>
<script>
(function () {{
  var rows = Array.prototype.slice.call(document.querySelectorAll('.mc-archive-row'));
  var state = {{ category: 'all', author: 'all', season: 'all', q: '' }};

  function apply() {{
    var any = false;
    rows.forEach(function (r) {{
      var show = (state.category === 'all' || r.dataset.category === state.category) &&
        (state.author === 'all' || r.dataset.author === state.author) &&
        (state.season === 'all' || r.dataset.season === state.season) &&
        (!state.q || r.dataset.search.indexOf(state.q) !== -1);
      r.style.display = show ? '' : 'none';
      if (show) any = true;
    }});
    var empty = document.getElementById('mc-archive-empty');
    if (empty) empty.style.display = any ? 'none' : '';
  }}

  function wireGroup(groupId, key) {{
    var group = document.getElementById(groupId);
    if (!group) return;
    var btns = Array.prototype.slice.call(group.querySelectorAll('.mc-filter-btn'));
    btns.forEach(function (b) {{
      b.addEventListener('click', function () {{
        btns.forEach(function (x) {{ x.classList.remove('is-active'); x.setAttribute('aria-pressed', 'false'); }});
        b.classList.add('is-active');
        b.setAttribute('aria-pressed', 'true');
        state[key] = b.dataset.value;
        apply();
      }});
    }});
  }}
  wireGroup('mc-archive-cat-group', 'category');
  wireGroup('mc-archive-author-group', 'author');
  wireGroup('mc-archive-season-group', 'season');

  var search = document.getElementById('mc-archive-search');
  if (search) {{
    search.addEventListener('input', function () {{
      state.q = search.value.trim().toLowerCase();
      apply();
    }});
  }}

  try {{
    var params = new URLSearchParams(window.location.search);
    ['author', 'category', 'season'].forEach(function (key) {{
      var val = params.get(key);
      if (!val) return;
      var btn = document.querySelector('#mc-archive-' + key + '-group .mc-filter-btn[data-value="' + val + '"]');
      if (btn) btn.click();
    }});
  }} catch (e) {{ /* URLSearchParams unsupported — filters still work manually */ }}
}})();
</script>"""
    html_out = page_shell(
        1, "Media Archive | Media Centre",
        "Every article and journal entry published this career, filterable by category, journalist and season.",
        "mc-body", "mc-shell", main,
    )
    (MEDIA_DIR / "archive.html").write_text(html_out, encoding="utf-8")
    print(f"Wrote docs/media/archive.html ({len(all_sorted)} entries)")


# ---------------------------------------------------------------------------
# docs/media/articles/*.html — individual article pages
# ---------------------------------------------------------------------------

def render_article_pages(people, people_by_id, articles):
    media_articles = [a for a in articles if a["content_type"] not in JOURNAL_CONTENT_TYPES]
    ARTICLES_DIR.mkdir(parents=True, exist_ok=True)

    for a in media_articles:
        person = people_by_id[a["author_id"]]
        outlet = a.get("outlet") or person["outlet"]
        slug, cat_label = derive_category(a)

        # Image roles (all optional, all backward-compatible):
        #   image        — the "card" role: feed/lead/related-story thumbnails.
        #                  Existing articles only ever set this one field.
        #   hero_image   — dedicated large article-page photo. Falls back to
        #                  `image` when absent, so older records still render
        #                  a hero exactly as before.
        #   hero_focus_x/hero_focus_y — optional object-position for the
        #                  hero, same focal-point convention as home_config.js
        #                  and the Media Centre lead card (--mc-focus-x/-y).
        #   inline_images — optional list of {src, alt, caption?} supporting
        #                  photos rendered inside the body column (never the
        #                  breakout-width hero slot). No current article uses
        #                  this; it's the smallest hook for a future one to.
        hero_src = a.get("hero_image") or a.get("image")
        hero_html = ""
        if hero_src:
            hero_alt = attr(a.get("hero_image_alt") or a.get("image_alt") or a["headline"])
            focus_vars = []
            if a.get("hero_focus_x"):
                focus_vars.append(f"--mc-focus-x:{a['hero_focus_x']}")
            if a.get("hero_focus_y"):
                focus_vars.append(f"--mc-focus-y:{a['hero_focus_y']}")
            style_attr = f' style="{attr(";".join(focus_vars))}"' if focus_vars else ""
            hero_html = f"""<figure class="article-hero"{style_attr}>
    <img src="../../{hero_src}" alt="{hero_alt}">
  </figure>"""

        inline_html = ""
        for img in a.get("inline_images") or []:
            if not img.get("src"):
                continue
            cap = f'<figcaption>{img["caption"]}</figcaption>' if img.get("caption") else ""
            inline_html += (
                f'<figure class="article-inline-figure">'
                f'<img src="../../{img["src"]}" alt="{attr(img.get("alt") or a["headline"])}">{cap}</figure>'
            )

        byline_avatar = person_avatar(person, 2, "article-byline-face", "article-byline-face-mono")
        related = related_articles(a, media_articles)
        related_html = ""
        if related:
            # Photographic card when the related story carries a "card" image
            # (the common case, since only 7 of today's articles have one);
            # graceful text-only fallback otherwise — never a broken layout.
            cards = []
            for r in related:
                rp = people_by_id[r["author_id"]]
                media = f'<div class="article-related-media"><img src="../../{r["image"]}" alt="" loading="lazy"></div>' if r.get("image") else ""
                cards.append(
                    f'<a class="article-related-card{"" if r.get("image") else " no-media"}" href="{r["id"]}.html">'
                    f'{media}<span class="article-related-title">{r["headline"]}</span>'
                    f'<span class="article-related-byline">{rp["name"]} &middot; {_format_toc_date(r["date"])}</span></a>'
                )
            related_html = f"""<div class="article-related">
    <h3>Related Coverage</h3>
    <div class="article-related-grid">
{"".join(cards)}
    </div>
  </div>"""

        author_avatar = person_avatar(person, 2, "article-author-avatar", "article-author-avatar-mono")
        author_card = f"""<div class="article-author-card">
    {author_avatar}
    <div>
      <div class="article-author-label">About the Author</div>
      <div class="article-author-name"><a href="../journalists.html#{attr(person['id'])}">{person['name']}</a></div>
      <div class="article-author-role">{person['role']} &middot; {outlet}</div>
      <p class="article-author-bio">{person['bio']}</p>
    </div>
  </div>"""

        main = f"""<article class="article-shell">
  <div class="article-kicker">
    <span>{outlet}</span><span class="article-kicker-sep">&middot;</span><span>{cat_label}</span>
  </div>
  <h1 class="article-headline">{a['headline']}</h1>
  <p class="article-deck">{a['dek']}</p>
  <div class="article-byline">
    {byline_avatar}
    <div>
      <div class="article-byline-name"><a href="../journalists.html#{attr(person['id'])}">{person['name']}</a></div>
      <div class="article-byline-sub">{person['role']} &middot; {outlet} &middot; {_format_toc_date(a['date'])}</div>
    </div>
  </div>
  {hero_html}
  <div class="article-body">
    {a['body_html']}
    {inline_html}
  </div>
  {related_html}
  {author_card}
  <a class="article-back" href="../index.html">&larr; Back to the Media Centre</a>
</article>"""
        html_out = page_shell(
            2, f"{a['headline']} | Media Centre",
            a.get("dek", a["headline"]),
            "article-page", "article-wrap", main,
        )
        (ARTICLES_DIR / f"{a['id']}.html").write_text(html_out, encoding="utf-8")

    print(f"Wrote {len(media_articles)} article pages under docs/media/articles/")


def main():
    people, people_by_id, articles = load_data()
    regenerate_journal_html(articles)
    render_media_index_js(people, people_by_id, articles)
    render_media_index(people, people_by_id, articles)
    render_journalists_page(people, people_by_id, articles)
    render_archive_page(people, people_by_id, articles)
    render_article_pages(people, people_by_id, articles)


if __name__ == "__main__":
    main()
