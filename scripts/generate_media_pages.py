"""Regenerate the Media Centre pages (docs/media/*) and docs/journal.html's
entry stream from media-personalities.json / media-articles.json.

Run this after any edit to either JSON file:
    python3 scripts/generate_media_pages.py

Source of truth: media-personalities.json (journalist/author profiles) and
media-articles.json (every article/entry, both Media Centre pieces and the
journal's Dispatch/Diary entries). This script never edits the JSON files —
only derived HTML under docs/.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
JOURNAL_HTML = DOCS / "journal.html"
MEDIA_DIR = DOCS / "media"
ARTICLES_DIR = MEDIA_DIR / "articles"

JOURNAL_CONTENT_TYPES = {"dispatch", "diary"}
MEDIA_SECTIONS = [
    "Featured Columns",
    "Match Coverage",
    "Tactical Analysis",
    "Television Debate",
    "International Reaction",
    "Press Conferences",
]

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


def replace_between(html, start_marker, end_marker, new_inner):
    pattern = re.compile(re.escape(start_marker) + r".*?" + re.escape(end_marker), re.DOTALL)
    if not pattern.search(html):
        raise SystemExit(f"Could not find marker pair {start_marker!r} / {end_marker!r}")
    return pattern.sub(start_marker + "\n" + new_inner + "\n" + end_marker, html, count=1)


# ---------------------------------------------------------------------------
# journal.html regeneration
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

    html = JOURNAL_HTML.read_text(encoding="utf-8")
    html = replace_between(html, MARK_ENTRIES_START, MARK_ENTRIES_END, build_journal_stream(journal_articles))
    html = replace_between(html, MARK_TOC_START, MARK_TOC_END, build_journal_toc(journal_articles))
    JOURNAL_HTML.write_text(html, encoding="utf-8")
    print(f"Regenerated {JOURNAL_HTML.relative_to(ROOT)} ({len(journal_articles)} entries)")


# ---------------------------------------------------------------------------
# Media Centre page chrome
# ---------------------------------------------------------------------------

NAV_LINKS = [
    ("index.html", "Season Hub"),
    ("journal.html", "Journal"),
    ("season.html", "Season Stats"),
    ("roster.html", "Roster"),
    ("depth_chart.html", "Depth Chart"),
    ("academy.html", "Academy"),
    ("season_preview.html", "Season Preview"),
    ("dossier.html", "Dossier"),
    ("history.html", "History"),
    ("media/index.html", "Media Centre"),
]


def render_nav(depth, active_href):
    prefix = "../" * depth
    parts = [f'    <a href="{prefix}index.html" class="snav-brand">WRXM <span>FC26</span></a>']
    for href, label in NAV_LINKS:
        cls = "snav-link active" if href == active_href else "snav-link"
        parts.append(f'    <a href="{prefix}{href}" class="{cls}">{label}</a>')
    parts.append(
        f'    <a href="{prefix}submit.html" class="snav-link" style="margin-left:auto; color:var(--gold);">⚡ Submit</a>'
    )
    return '<nav class="site-nav">\n  <div class="site-nav-inner">\n' + "\n".join(parts) + "\n  </div>\n</nav>"


def page_shell(depth, title, active_href, masthead_label, masthead_date, body_html):
    prefix = "../" * depth
    nav = render_nav(depth, active_href)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
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
<body>

<!-- SITE NAV -->
{nav}

<div class="page-wrap">

<div class="masthead">
  <span class="masthead-label">{masthead_label}</span>
  <span class="masthead-date">{masthead_date}</span>
</div>

{body_html}

</div>

</body>
</html>
"""


def journalist_avatar(person, depth=0):
    initials = "".join(w[0] for w in person["name"].split()[:2]).upper()
    if person.get("headshot"):
        prefix = "../" * depth
        return f'<img class="journalist-avatar" src="{prefix}{person["headshot"]}" alt="{person["name"]}">'
    return f'<div class="journalist-avatar journalist-avatar-mono" style="background:{person["accent_color"]}">{initials}</div>'


# ---------------------------------------------------------------------------
# Media Centre: index, journalists, archive, article pages
# ---------------------------------------------------------------------------

def media_card(a, people_by_id):
    """Card linking to a Media Centre article page. Only ever rendered on pages
    that live directly in docs/media/ (index.html, archive.html), so the article
    href is always relative to that directory."""
    person = people_by_id[a["author_id"]]
    return f"""<a class="media-card" href="articles/{a['id']}.html" style="border-top:3px solid {person['accent_color']}">
  <div class="media-card-outlet">{a.get('outlet', person['outlet'])}</div>
  <h3 class="media-card-title">{a['headline']}</h3>
  <p class="media-card-dek">{a['dek']}</p>
  <div class="media-card-byline">{person['name']} &middot; {_format_toc_date(a['date'])}</div>
</a>"""


def dispatch_teaser_card(a):
    """Teaser card linking back into docs/journal.html. Only ever rendered on
    docs/media/index.html, one directory below docs/."""
    return f"""<a class="media-card media-card-teaser" href="../journal.html#{a['id']}">
  <div class="media-card-outlet">Red Dragon Dispatch</div>
  <h3 class="media-card-title">{a['headline']}</h3>
  <p class="media-card-dek">{a['dek']}</p>
  <div class="media-card-byline">Owen Meredith &middot; {_format_toc_date(a['date'])}</div>
</a>"""


def render_media_index(people, people_by_id, articles):
    media_articles = [a for a in articles if a["content_type"] not in JOURNAL_CONTENT_TYPES]
    dispatches = sorted(
        (a for a in articles if a["content_type"] == "dispatch"), key=lambda a: a["date"], reverse=True
    )[:3]

    section_html = []
    for section in MEDIA_SECTIONS:
        section_html.append(f'<div class="media-section-header"><h2>{section}</h2></div>')
        if section == "Match Coverage":
            cards = [dispatch_teaser_card(a) for a in dispatches]
        else:
            cards = [media_card(a, people_by_id) for a in media_articles if a.get("section") == section]
        if cards:
            section_html.append('<div class="media-grid">\n' + "\n".join(cards) + "\n</div>")
        else:
            section_html.append('<p class="media-empty">More coverage coming as the season develops.</p>')

    body = f"""<div class="media-hub-header">
  <div class="hub-eyebrow">An Alternate-History Football Timeline &middot; FC26 Career Mode</div>
  <h1 class="hub-title">Media <span>Centre</span></h1>
  <p class="hub-subtitle">Wrexham AFC as covered by a fictional press corps &mdash; Sky Sports, BBC Sport, The Athletic, Gazzetta dello Sport, ESPN FC, and the Racecourse's own Red Dragon Dispatch. None of this is real journalism about a real event; it's this career's story, told by recurring voices.</p>
  <div class="media-hub-links">
    <a class="media-hub-link" href="journalists.html">Journalist Profiles &rarr;</a>
    <a class="media-hub-link" href="archive.html">Full Archive &rarr;</a>
  </div>
</div>

{chr(10).join(section_html)}
"""
    html = page_shell(1, "Media Centre | Wrexham AFC", "media/index.html", "Wrexham AFC · Media Centre",
                       "Season 2026–27", body)
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    (MEDIA_DIR / "index.html").write_text(html, encoding="utf-8")
    print(f"Wrote docs/media/index.html ({len(media_articles)} Media Centre articles)")


def render_journalists_page(people, people_by_id, articles):
    counts = {}
    for a in articles:
        counts[a["author_id"]] = counts.get(a["author_id"], 0) + 1

    cards = []
    for p in people:
        n = counts.get(p["id"], 0)
        byline_tag = "The Manager's Diary" if not p["is_press"] else p["outlet"]
        specialties = ", ".join(p["specialties"])
        cards.append(f"""<div class="journalist-card">
  {journalist_avatar(p, depth=1)}
  <div class="journalist-card-body">
    <h3>{p['name']}</h3>
    <div class="journalist-card-outlet">{p['role']} &middot; {byline_tag}</div>
    <p>{p['bio']}</p>
    <p class="journalist-card-voice"><strong>Voice:</strong> {p['voice']}</p>
    <p class="journalist-card-specialties"><strong>Covers:</strong> {specialties}</p>
    <p class="journalist-card-relationship"><strong>On Wrexham:</strong> {p['relationship_with_wrexham']}</p>
    <a href="archive.html#author-{p['id']}" class="journalist-card-link">{n} article{'s' if n != 1 else ''} &rarr;</a>
  </div>
</div>""")

    body = f"""<div class="media-hub-header">
  <h1 class="hub-title">Journalist <span>Profiles</span></h1>
  <p class="hub-subtitle">Every recurring voice covering Keeyvon Jenkins' Wrexham, fictional to a person, each with their own outlet, angle, and opinion of the club.</p>
</div>
<div class="journalist-grid">
{chr(10).join(cards)}
</div>
"""
    html = page_shell(1, "Journalist Profiles | Media Centre", "media/index.html", "Wrexham AFC · Media Centre",
                       "Journalist Profiles", body)
    (MEDIA_DIR / "journalists.html").write_text(html, encoding="utf-8")
    print(f"Wrote docs/media/journalists.html ({len(people)} profiles)")


def render_archive_page(people, people_by_id, articles):
    all_sorted = sorted(articles, key=lambda a: a["date"], reverse=True)

    filter_buttons = ['<button class="jf-btn active" onclick="filterArchive(\'all\',this)">All</button>']
    for p in people:
        filter_buttons.append(
            f'<button class="jf-btn" onclick="filterArchive(\'{p["id"]}\',this)">{p["name"]}</button>'
        )

    rows = []
    for a in all_sorted:
        person = people_by_id[a["author_id"]]
        if a["content_type"] in JOURNAL_CONTENT_TYPES:
            href = f'../journal.html#{a["id"]}'
        else:
            href = f'articles/{a["id"]}.html'
        outlet = a.get("outlet", person["outlet"])
        rows.append(f"""<a class="archive-row" data-author="{person['id']}" href="{href}">
  <span class="archive-row-date">{_format_toc_date(a['date'])}</span>
  <span class="archive-row-title">{a['headline']}</span>
  <span class="archive-row-byline">{person['name']} &middot; {outlet}</span>
</a>""")

    body = f"""<div class="media-hub-header">
  <h1 class="hub-title">Full <span>Archive</span></h1>
  <p class="hub-subtitle">Every article and entry published this season, browsable by author.</p>
</div>
<div class="media-filter-bar">
{chr(10).join(filter_buttons)}
</div>
<div class="archive-list">
{chr(10).join(rows)}
</div>
<script>
function filterArchive(authorId, btn) {{
  document.querySelectorAll('.jf-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  document.querySelectorAll('.archive-row').forEach(row => {{
    row.style.display = (authorId === 'all' || row.dataset.author === authorId) ? '' : 'none';
  }});
}}
</script>
"""
    html = page_shell(1, "Archive | Media Centre", "media/index.html", "Wrexham AFC · Media Centre",
                       "Full Archive", body)
    (MEDIA_DIR / "archive.html").write_text(html, encoding="utf-8")
    print(f"Wrote docs/media/archive.html ({len(all_sorted)} entries)")


def render_article_pages(people, people_by_id, articles):
    media_articles = [a for a in articles if a["content_type"] not in JOURNAL_CONTENT_TYPES]
    ARTICLES_DIR.mkdir(parents=True, exist_ok=True)

    for a in media_articles:
        person = people_by_id[a["author_id"]]
        related = [
            other for other in media_articles
            if other["id"] != a["id"] and (other["author_id"] == a["author_id"] or set(other.get("tags", [])) & set(a.get("tags", [])))
        ][:3]
        related_html = ""
        if related:
            related_items = "\n".join(
                f'<a class="related-link" href="{r["id"]}.html">{r["headline"]}</a>' for r in related
            )
            related_html = f'<div class="related-articles"><h3>Related Coverage</h3>{related_items}</div>'

        body = f"""<article class="media-article">
  <div class="media-article-header" style="border-top:3px solid {person['accent_color']}">
    <div class="media-article-outlet">{a.get('outlet', person['outlet'])} &middot; {a.get('section', '')}</div>
    <h1 class="media-article-title">{a['headline']}</h1>
    <p class="media-article-dek">{a['dek']}</p>
    <div class="media-article-byline">
      {journalist_avatar(person, depth=2)}
      <div>
        <strong><a href="../journalists.html#{person['id']}">{person['name']}</a></strong>
        <div class="media-article-byline-sub">{a.get('outlet', person['outlet'])} &middot; {_format_toc_date(a['date'])}</div>
      </div>
    </div>
  </div>
  <div class="media-article-body">
    {a['body_html']}
  </div>
</article>
{related_html}
"""
        html = page_shell(2, f"{a['headline']} | Media Centre", "media/index.html",
                           a.get('outlet', person['outlet']), _format_toc_date(a['date']), body)
        (ARTICLES_DIR / f"{a['id']}.html").write_text(html, encoding="utf-8")

    print(f"Wrote {len(media_articles)} article pages under docs/media/articles/")


def main():
    people, people_by_id, articles = load_data()
    regenerate_journal_html(articles)
    render_media_index(people, people_by_id, articles)
    render_journalists_page(people, people_by_id, articles)
    render_archive_page(people, people_by_id, articles)
    render_article_pages(people, people_by_id, articles)


if __name__ == "__main__":
    main()
