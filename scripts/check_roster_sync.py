"""
Cross-checks docs/roster.html (senior section against wrexham_squad.csv,
academy section against youth_academy.csv) and docs/academy.html (against
youth_academy.csv) for the class of sync bugs CLAUDE.md already warns about
("Squad Changes — Keep All Pages in Sync" / "Academy Changes — Keep Pages in
Sync"): a player edited in the CSV but not updated on a page, a
departed/promoted player left behind as a stale card, or a name/age/OVR/POT
that's drifted between the two because one file got hand-edited and the
other didn't.

This is deliberately a *checker*, not a generator. roster.html's cards mix
mechanical CSV facts (name, age, OVR, position, POT) with judgment-laden
prose (development trajectory phrasing, elite/faded emphasis, loan
narratives) that a script shouldn't be rewriting -- see the "Journal Style
Guide" note on the same principle for docs/journal.html. This only flags
mechanical drift; the prose stays hand-authored.

Run after editing wrexham_squad.csv, youth_academy.csv, docs/roster.html, or
docs/academy.html:
    python3 scripts/check_roster_sync.py
Exits non-zero if any mismatch is found (usable as a pre-commit sanity check).
"""
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SQUAD_CSV = ROOT / "wrexham_squad.csv"
ACADEMY_CSV = ROOT / "youth_academy.csv"
ROSTER_HTML = ROOT / "docs" / "roster.html"
ACADEMY_HTML = ROOT / "docs" / "academy.html"

CARD_START_RE = re.compile(r'<div class="acad-profile-card[^"]*">')
NAME_RE = re.compile(r'<div class="acad-profile-name">([^<]+)</div>')
META_RE = re.compile(r'<div class="acad-profile-meta">(.*?)</div>', re.DOTALL)
POS_BADGE_RE = re.compile(r'<span class="acad-pos-badge[^"]*">([^<]+)</span>')
AGE_RE = re.compile(r'Age (\d+)')
OVR_RE = re.compile(r'<div class="acad-ovr[^"]*"[^>]*>(\d+)</div>')
POT_RE = re.compile(r'<div class="acad-pot"><strong>POT</strong>\s*(\d+)\s*[-–]\s*(\d+)</div>')
NOTES_POT_RE = re.compile(r'POT (\d+)-(\d+)')


def load_squad_csv_players():
    with open(SQUAD_CSV, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    players = {}
    for row in rows[1:]:
        if not row or not row[0].strip():
            continue
        name, position, age, ovr = row[0], row[1], row[2], row[3]
        players[name] = {"position": position, "age": age, "ovr": ovr}
    return players


def load_academy_csv_players():
    with open(ACADEMY_CSV, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    players = {}
    for row in rows[1:]:
        if not row or not row[0].strip():
            continue
        name, position, age, ovr, notes = row[0], row[1], row[2], row[3], row[52]
        pot_m = NOTES_POT_RE.search(notes)
        players[name] = {
            "position": position,
            "age": age,
            "ovr": ovr,
            "pot": pot_m.groups() if pot_m else None,
        }
    return players


def parse_cards(html_slice, with_pot=False):
    starts = [m.start() for m in CARD_START_RE.finditer(html_slice)] + [len(html_slice)]

    players = {}
    for i in range(len(starts) - 1):
        card = html_slice[starts[i]:starts[i + 1]]
        name_m = NAME_RE.search(card)
        meta_m = META_RE.search(card)
        ovr_m = OVR_RE.search(card)
        if not (name_m and meta_m and ovr_m):
            continue
        meta = meta_m.group(1)
        pos_m = POS_BADGE_RE.search(meta)
        age_m = AGE_RE.search(meta)
        entry = {
            "position": pos_m.group(1) if pos_m else "?",
            "age": age_m.group(1) if age_m else "?",
            "ovr": ovr_m.group(1),
        }
        if with_pot:
            pot_m = POT_RE.search(card)
            entry["pot"] = pot_m.groups() if pot_m else None
        players[name_m.group(1)] = entry
    return players


def load_roster_html_sections():
    html = ROSTER_HTML.read_text(encoding="utf-8")
    academy_start = html.find('id="sec-academy"')
    if academy_start == -1:
        return html, ""
    return html[:academy_start], html[academy_start:]


def diff_group(label, csv_players, html_players, check_pot=False):
    problems = []
    for name, csv_p in csv_players.items():
        if name not in html_players:
            problems.append(f"MISSING FROM ROSTER ({label}): {name} is in the CSV but has no card in roster.html")
            continue
        html_p = html_players[name]
        if csv_p["age"] != html_p["age"]:
            problems.append(f"AGE MISMATCH ({label}): {name} — CSV says {csv_p['age']}, roster.html says {html_p['age']}")
        if csv_p["ovr"] != html_p["ovr"]:
            problems.append(f"OVR MISMATCH ({label}): {name} — CSV says {csv_p['ovr']}, roster.html says {html_p['ovr']}")
        csv_positions = [p.strip() for p in csv_p["position"].split("/") if p.strip()]
        if csv_positions and html_p["position"] not in csv_positions:
            problems.append(f"POSITION DRIFT ({label}): {name} — CSV lists '{csv_p['position']}', roster.html badge '{html_p['position']}' isn't one of those")
        if check_pot and csv_p.get("pot") and html_p.get("pot") and csv_p["pot"] != html_p["pot"]:
            problems.append(
                f"POT MISMATCH ({label}): {name} — CSV Notes say {csv_p['pot'][0]}-{csv_p['pot'][1]}, "
                f"roster.html says {html_p['pot'][0]}-{html_p['pot'][1]}"
            )

    for name in html_players:
        if name not in csv_players:
            problems.append(f"STALE CARD ({label}): {name} has a card in roster.html but is not in the CSV (departed/promoted and not removed?)")

    return problems


def main():
    senior_html, roster_academy_html = load_roster_html_sections()

    squad_csv_players = load_squad_csv_players()
    squad_html_players = parse_cards(senior_html)
    problems = diff_group("roster.html senior", squad_csv_players, squad_html_players)

    academy_csv_players = load_academy_csv_players()

    roster_academy_html_players = parse_cards(roster_academy_html, with_pot=True)
    problems += diff_group("roster.html academy", academy_csv_players, roster_academy_html_players, check_pot=True)

    academy_html = ACADEMY_HTML.read_text(encoding="utf-8")
    academy_page_players = parse_cards(academy_html, with_pot=True)
    problems += diff_group("academy.html", academy_csv_players, academy_page_players, check_pot=True)

    if not problems:
        print(
            f"OK — {len(squad_csv_players)} senior players and {len(academy_csv_players)} academy players "
            f"match roster.html and academy.html"
        )
        return 0

    print(f"Found {len(problems)} mismatch(es):")
    for p in problems:
        print(f"  - {p}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
