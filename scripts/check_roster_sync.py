"""
Cross-checks docs/roster.html against wrexham_squad.csv for the class of sync
bugs CLAUDE.md already warns about ("Squad Changes — Keep All Pages in Sync"):
a player edited in the CSV but not updated on the roster page, a departed
player left behind as a stale card, or a name/age/OVR that's drifted between
the two because one file got hand-edited and the other didn't.

This is deliberately a *checker*, not a generator. roster.html's cards mix
mechanical CSV facts (name, age, OVR, position) with judgment-laden prose
(development trajectory phrasing, elite/faded emphasis, loan narratives) that
a script shouldn't be rewriting -- see the "Journal Style Guide" note on the
same principle for docs/journal.html. This only flags mechanical drift; the
prose stays hand-authored.

Run after editing wrexham_squad.csv or docs/roster.html:
    python3 scripts/check_roster_sync.py
Exits non-zero if any mismatch is found (usable as a pre-commit sanity check).
"""
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SQUAD_CSV = ROOT / "wrexham_squad.csv"
ROSTER_HTML = ROOT / "docs" / "roster.html"

CARD_START_RE = re.compile(r'<div class="acad-profile-card[^"]*">')
NAME_RE = re.compile(r'<div class="acad-profile-name">([^<]+)</div>')
META_RE = re.compile(r'<div class="acad-profile-meta">(.*?)</div>', re.DOTALL)
POS_BADGE_RE = re.compile(r'<span class="acad-pos-badge[^"]*">([^<]+)</span>')
AGE_RE = re.compile(r'Age (\d+)')
OVR_RE = re.compile(r'<div class="acad-ovr[^"]*"[^>]*>(\d+)</div>')


def load_csv_players():
    with open(SQUAD_CSV, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    players = {}
    for row in rows[1:]:
        if not row or not row[0].strip():
            continue
        name, position, age, ovr = row[0], row[1], row[2], row[3]
        players[name] = {"position": position, "age": age, "ovr": ovr}
    return players


def load_html_players():
    html = ROSTER_HTML.read_text(encoding="utf-8")
    # Only the senior-squad section; academy cards use the same class but are
    # out of scope for this CSV.
    academy_start = html.find('id="sec-academy"')
    senior_html = html[:academy_start] if academy_start != -1 else html

    starts = [m.start() for m in CARD_START_RE.finditer(senior_html)] + [len(senior_html)]

    players = {}
    for i in range(len(starts) - 1):
        card = senior_html[starts[i]:starts[i + 1]]
        name_m = NAME_RE.search(card)
        meta_m = META_RE.search(card)
        ovr_m = OVR_RE.search(card)
        if not (name_m and meta_m and ovr_m):
            continue
        meta = meta_m.group(1)
        pos_m = POS_BADGE_RE.search(meta)
        age_m = AGE_RE.search(meta)
        players[name_m.group(1)] = {
            "position": pos_m.group(1) if pos_m else "?",
            "age": age_m.group(1) if age_m else "?",
            "ovr": ovr_m.group(1),
        }
    return players


def main():
    csv_players = load_csv_players()
    html_players = load_html_players()

    problems = []

    for name, csv_p in csv_players.items():
        if name not in html_players:
            problems.append(f"MISSING FROM ROSTER: {name} is in wrexham_squad.csv but has no card in roster.html")
            continue
        html_p = html_players[name]
        if csv_p["age"] != html_p["age"]:
            problems.append(f"AGE MISMATCH: {name} — CSV says {csv_p['age']}, roster.html says {html_p['age']}")
        if csv_p["ovr"] != html_p["ovr"]:
            problems.append(f"OVR MISMATCH: {name} — CSV says {csv_p['ovr']}, roster.html says {html_p['ovr']}")
        csv_positions = [p.strip() for p in csv_p["position"].split("/") if p.strip()]
        if csv_positions and html_p["position"] not in csv_positions:
            problems.append(f"POSITION DRIFT: {name} — CSV lists '{csv_p['position']}', roster.html badge '{html_p['position']}' isn't one of those")

    for name in html_players:
        if name not in csv_players:
            problems.append(f"STALE CARD: {name} has a card in roster.html but is not in wrexham_squad.csv (departed and not removed?)")

    if not problems:
        print(f"OK — {len(csv_players)} senior players match between wrexham_squad.csv and roster.html")
        return 0

    print(f"Found {len(problems)} mismatch(es):")
    for p in problems:
        print(f"  - {p}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
