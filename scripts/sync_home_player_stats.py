#!/usr/bin/env python3
"""Regenerate docs/assets/player_stats.js from docs/season.html + season_log.json.

docs/season.html's "Player Season Stats -- Senior Matches" table (id
"player-stats") is the only source of truth for per-player season Apps/G/A/
MOTM/Rtg -- there is no JSON equivalent, it's hand-maintained match by match.
This script parses that table and emits a small generated lookup so the
homepage Squad Spotlight can show a featured player's real season goals,
assists and average rating without duplicating the numbers by hand (which
would go stale the moment the next match is logged).

It also reads the optional `player_ratings` field on season_log.json's
`matches` entries (see "Season Log Schema" in CLAUDE.md) to build each
player's last-5-match rating sequence for the homepage sparkline. That field
only gets filled in when a screenshot actually shows a player's match
rating, so a player's `last5` list may be short or absent -- the homepage
never fabricates a point that isn't there.

Goals/Assists are meaningless for goalkeepers, so GK entries additionally
carry `trackedApps`/`cleanSheets`/`goalsConceded` (same partial-coverage
derivation as sync_squad_page.py's load_gk_match_log) and docs/assets/home.js
renders those instead wherever a GK is spotlighted.

Senior matches only, matching the table's own scope -- youth academy players
have no rows here and none are generated, which is intentional: the homepage
Next Generation section never shows season stats or a sparkline.

Run this after any session that updates docs/season.html's Player Season
Stats table, or adds `player_ratings` to a match in season_log.json (i.e.
any match session, per the Match Submission Checklist in CLAUDE.md).
"""
import html
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEASON_HTML = ROOT / "docs" / "season.html"
SEASON_LOG = ROOT / "season_log.json"
OUT = ROOT / "docs" / "assets" / "player_stats.js"

ROW_RE = re.compile(
    r'<div class="stats-row">\s*'
    r'<div><div class="s-name">(?P<name>.*?)</div><div class="s-pos">(?P<pos>.*?)</div></div>\s*'
    r'<span class="s-num">(?P<apps>\d+)</span>\s*'
    r'<span class="s-num(?: highlight)?">(?P<goals>\d+)</span>\s*'
    r'<span class="s-num(?: highlight)?">(?P<assists>\d+)</span>\s*'
    r'<span class="s-motm">(?P<motm>.*?)</span>\s*'
    r'<span class="s-rating">(?P<rating>[\d.]+)</span>',
    re.S,
)


NOT_YET_BEGUN_MARKER = "has not yet begun"


def extract_table(html_text):
    marker = 'id="player-stats"'
    start = html_text.find(marker)
    if start == -1:
        if NOT_YET_BEGUN_MARKER in html_text:
            # Legitimate empty state right after a Season Rollover, before the
            # new season's first match is logged -- docs/season.html shows the
            # "Season N has not yet begun" placeholder instead of the table.
            return None
        raise SystemExit('Could not find id="player-stats" section in docs/season.html')
    end = html_text.find('<div class="footer">', start)
    if end == -1:
        end = len(html_text)
    return html_text[start:end]


def last_name_key(name):
    """Last whitespace token, lowercased, accents stripped -- lets "L. Sauer"
    and "Leo Sauer" (both appear in the wild across season.html / season_log.json)
    resolve to the same player without hand-maintained aliasing."""
    token = name.strip().split()[-1] if name.strip() else name
    decomposed = unicodedata.normalize("NFKD", token)
    return "".join(c for c in decomposed if not unicodedata.combining(c)).lower()


def build_players():
    text = SEASON_HTML.read_text(encoding="utf-8")
    table_html = extract_table(text)
    if table_html is None:
        return {}

    players = {}
    for m in ROW_RE.finditer(table_html):
        name = html.unescape(m.group("name")).strip()
        players[name] = {
            "position": html.unescape(m.group("pos")).strip(),
            "apps": int(m.group("apps")),
            "goals": int(m.group("goals")),
            "assists": int(m.group("assists")),
            "rating": float(m.group("rating")),
        }

    if not players:
        raise SystemExit("Parsed zero player rows -- season.html markup may have changed; check ROW_RE.")
    return players


def attach_gk_defensive_stats(players):
    """For goalkeepers, Goals/Assists are meaningless -- replace them with
    Clean Sheets / Goals Conceded, derived from season_log.json's
    player_ratings (only matches with a captured ratings screenshot) joined
    to that match's score. Partial-coverage by construction, same as the
    identical derivation in scripts/sync_squad_page.py's load_gk_match_log
    and scripts/generate_player_pages.py."""
    if not SEASON_LOG.exists():
        return
    log = json.loads(SEASON_LOG.read_text(encoding="utf-8"))
    by_last_name = {}
    for canonical in players:
        by_last_name.setdefault(last_name_key(canonical), canonical)

    gk_log = {}
    for m in log.get("matches", []):
        score = m.get("score")
        pr = m.get("player_ratings")
        if not score or not pr:
            continue
        wg, og = (int(x) for x in score.split("-"))
        for raw_name in pr:
            canonical = by_last_name.get(last_name_key(raw_name))
            if not canonical or players[canonical]["position"] != "GK":
                continue
            entry = gk_log.setdefault(canonical, {"trackedApps": 0, "cleanSheets": 0, "goalsConceded": 0})
            entry["trackedApps"] += 1
            entry["goalsConceded"] += og
            if og == 0:
                entry["cleanSheets"] += 1

    for canonical, player in players.items():
        if player["position"] != "GK":
            continue
        gk = gk_log.get(canonical, {"trackedApps": 0, "cleanSheets": 0, "goalsConceded": 0})
        player["trackedApps"] = gk["trackedApps"]
        player["cleanSheets"] = gk["cleanSheets"]
        player["goalsConceded"] = gk["goalsConceded"]


def attach_last5(players):
    if not SEASON_LOG.exists():
        return
    log = json.loads(SEASON_LOG.read_text(encoding="utf-8"))
    by_last_name = {}
    for canonical in players:
        by_last_name.setdefault(last_name_key(canonical), canonical)

    history = {}  # canonical player name -> list of (date, rating)
    matches = sorted(log.get("matches", []), key=lambda m: m.get("date", ""))
    for m in matches:
        ratings = m.get("player_ratings") or {}
        for raw_name, rating in ratings.items():
            canonical = by_last_name.get(last_name_key(raw_name))
            if not canonical:
                continue
            history.setdefault(canonical, []).append({"date": m["date"], "rating": rating})

    for canonical, entries in history.items():
        players[canonical]["last5"] = entries[-5:]


def main():
    players = build_players()
    attach_gk_defensive_stats(players)
    attach_last5(players)

    body = (
        "/* GENERATED by scripts/sync_home_player_stats.py -- do not hand-edit.\n"
        "   Season totals from docs/season.html's Player Season Stats (Senior Matches)\n"
        "   table; last5 sparkline points from season_log.json's player_ratings field.\n"
        "   Keyed by the abbreviated \"F. Lastname\" form used in that table.\n"
        "   Re-run after any session that updates either source. */\n"
        "const PLAYER_SEASON_STATS = " + json.dumps(players, indent=2, ensure_ascii=False) + ";\n"
    )
    OUT.write_text(body, encoding="utf-8")
    with_sparkline = sum(1 for p in players.values() if p.get("last5"))
    print(f"Wrote {OUT.relative_to(ROOT)} ({len(players)} players, {with_sparkline} with sparkline data)")


if __name__ == "__main__":
    main()
