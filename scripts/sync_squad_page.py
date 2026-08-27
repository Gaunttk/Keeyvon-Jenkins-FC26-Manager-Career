#!/usr/bin/env python3
"""Regenerate docs/assets/squad_data.js from wrexham_squad.csv + docs/assets/player_stats.js.

Powers the redesigned Squad landing page (docs/roster.html's senior-squad
section, rendered by docs/assets/squad.js). This script is the single source
of truth translation layer -- it never invents a fact. Anything not reliably
present in wrexham_squad.csv (jersey number, nationality) is simply omitted
from the output rather than guessed.

Photo paths are resolved from PHOTO_MAP below -- add a new senior signing's
photo file there (or leave them out for the placeholder silhouette).

Current-season Apps/Goals/Assists/Avg Rating are joined in from
docs/assets/player_stats.js by last-name key (same join key
sync_home_player_stats.py already uses across the site) -- never
hand-entered here, so a match session that regenerates player_stats.js and
then reruns this script keeps the Squad page's leaders/spotlight numbers
correct automatically.

Run this after any change to wrexham_squad.csv, or after player_stats.js is
regenerated following a match session (see CLAUDE.md's "Squad Changes" /
"Match Submission Checklist"). Also chains scripts/generate_player_pages.py
at the end, so a single run of this script keeps docs/players/*.html (each
player's full attribute breakdown) in sync too -- no separate step needed.
"""
import csv
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SQUAD_CSV = ROOT / "wrexham_squad.csv"
PLAYER_STATS_JS = ROOT / "docs" / "assets" / "player_stats.js"
PL_TABLE_JS = ROOT / "docs" / "assets" / "pl_table.js"
SEASON_LOG = ROOT / "season_log.json"
HOME_CONFIG_JS = ROOT / "docs" / "assets" / "home_config.js"
OUT = ROOT / "docs" / "assets" / "squad_data.js"

# name -> photo path under docs/assets/. Players without an entry here get
# the neutral placeholder silhouette on the Squad page.
PHOTO_MAP = {
    "Arthur Okonkwo": "assets/photos/arthur_okonkwo.png",
    "Liberato Cacace": "assets/photos/liberato_cacace.png",
    "Max Cleworth": "assets/photos/max_cleworth.png",
    "Callum Doyle": "assets/photos/callum_doyle.png",
    "Joenathan Amelia": "assets/photos/joenathan_amelia.png",
    "Bailey Cadamarteri": "assets/photos/bailey_cadamarteri.png",
    "Yacel Amrizi": "assets/photos/yacel_amrizi.png",
    "Andrés Gómez": "assets/photos/andres_gomez.png",
    "Brian Gutiérrez": "assets/photos/brian_gutierrez.png",
    "Damián Bobadilla": "assets/photos/damian_bobadilla.png",
    "Mason Webber": "assets/photos/mason_webber.png",
    # Santiago Ortega: only image on file is a raw Attributes-tab screenshot,
    # not portrait photography -- falls back to the placeholder silhouette.
    "Milán Vitális": "assets/photos/milan_vitalis.png",
    "Vladyslav Veleten": "assets/photos/vladyslav_veleten.png",
    "Alan Minda": "assets/photos/alan_minda.png",
    "Chido Obi": "assets/photos/chido_obi.png",
    "Jorthy Mokio": "assets/photos/jorthy_mokio.png",
    "Toni Fruk": "assets/photos/toni_fruk.png",
    "Jamal Belghazi": "assets/photos/jamal_belghazi.png",
    "Mario Barbieri": "assets/photos/mario_barbieri.png",
    "Rio Ngumoha": "assets/photos/rio_ngumoha.png",
    "Ayden Heaven": "assets/photos/ayden_heaven.png",
    "Elijah Dijkstra": "assets/photos/elijah_dijkstra.png",
    "Andrés Cuenca": "assets/photos/andres_cuenca.png",
    "Leo Sauer": "assets/photos/leo_sauer.png",
    "Carlos Macia": "assets/photos/carlos_macia.png",
    "Bernt Klaverboer": "assets/photos/bernt_klaverboer.png",
    "Juan Cruz Vargas": "assets/photos/vargas.png",
    "Marco Soria": "assets/photos/soria.png",
    "Emiliano Bianchi": "assets/photos/bianchi.png",
    "Thiago Pitarch": "assets/photos/thiago_pitarch.png",
    "Jermaine Lord": "assets/photos/lord.png",
    "Vittorio Martini": "assets/photos/martini.png",
    "Nico Kopp": "assets/photos/kopp.png",
    "Fabricio Sandoval": "assets/photos/sandoval.png",
    "Lilian Faure": "assets/photos/faure.png",
    "Stephane Bertrand": "assets/photos/bertrand.png",
    "Adrian Kaczmarek": "assets/photos/adrian_kaczmarek.png",
    # Aaron James: no approved photo -- falls back to placeholder.
}

# Editorial-only: which player anchors the Squad Spotlight. A presentation
# choice, not a stat -- see CLAUDE.md's home_config.js precedent.
FEATURED_PLAYER = "Yacel Amrizi"

GK, DEF, MID, FWD = "Goalkeepers", "Defenders", "Midfielders", "Forwards"
GROUP_MAP = {
    "GK": GK,
    "CB": DEF, "RB": DEF, "LB": DEF,
    "CDM": MID, "CM": MID, "CAM": MID, "LM": MID, "RM": MID,
    "ST": FWD, "LW": FWD, "RW": FWD, "CF": FWD,
}


def strip_accents(s):
    d = unicodedata.normalize("NFKD", s)
    return "".join(c for c in d if not unicodedata.combining(c))


def last_name_key(name):
    token = name.strip().split()[-1] if name.strip() else name
    return strip_accents(token).lower()


def slugify(name):
    ascii_name = strip_accents(name).lower()
    return re.sub(r"[^a-z0-9]+", "-", ascii_name).strip("-")


LOAN_RE = re.compile(r"On Loan at ([^(]+?)\s*(?:\(back ([^)]+)\))?$")

# FC26's development-status classification, stored as free text at the front
# of the Status column (col 11) -- e.g. "Showing Great Potential — Contract
# already accepted (signed from Ajax)". Order matters: check the more
# specific "Potential To Be Special" phrase before "Great Potential" since
# neither substring is a prefix of the other, but keep this ordered by
# specificity for safety if the game ever varies the wording.
DEV_STATUS_MAP = [
    ("Has Potential To Be Special", "HPTBS"),
    ("An Exciting Prospect", "EP"),
    ("Showing Great Potential", "SGP"),
]


def parse_dev_status(status_text):
    for phrase, code in DEV_STATUS_MAP:
        if phrase in status_text:
            return {"code": code, "label": phrase}
    return None


def load_player_stats():
    text = PLAYER_STATS_JS.read_text(encoding="utf-8")
    m = re.search(r"const PLAYER_SEASON_STATS = (\{.*?\});", text, re.DOTALL)
    return json.loads(m.group(1)) if m else {}


def load_season_context():
    text = PL_TABLE_JS.read_text(encoding="utf-8")
    m = re.search(r"season:\s*'([^']+)'", text)
    return m.group(1) if m else None


def load_gk_match_log():
    """Per-goalkeeper defensive log derived from season_log.json's
    player_ratings (only matches with a captured ratings screenshot) joined
    to that match's score (always "Wrexham-Opponent"). Partial-coverage by
    construction -- see the Squad At a Glance / card note this feeds. Mirrors
    the identical derivation in scripts/generate_player_pages.py."""
    d = json.loads(SEASON_LOG.read_text(encoding="utf-8"))
    by_lastname = {}
    for m in d["matches"]:
        score = m.get("score")
        pr = m.get("player_ratings")
        if not score or not pr:
            continue
        wg, og = (int(x) for x in score.split("-"))
        for pkey in pr:
            lk = last_name_key(pkey)
            entry = by_lastname.setdefault(lk, {"trackedApps": 0, "cleanSheets": 0, "goalsConceded": 0})
            entry["trackedApps"] += 1
            entry["goalsConceded"] += og
            if og == 0:
                entry["cleanSheets"] += 1
    return by_lastname


ACADEMY_SECTION_RE = re.compile(r"academy:\s*\{(.*)\}\s*;", re.DOTALL)
ACADEMY_ENTRY_RE = re.compile(r"\{([^{}]*name:\s*'[^{}]*)\}")
ACADEMY_FIELD_RES = {
    "name": re.compile(r"name:\s*'([^']*)'"),
    "position": re.compile(r"position:\s*'([^']*)'"),
    "age": re.compile(r"age:\s*(\d+)"),
    "ovr": re.compile(r"ovr:\s*(\d+)"),
    "potential": re.compile(r"potential:\s*'([^']*)'"),
    "image": re.compile(r"image:\s*'([^']*)'"),
}


def load_academy_preview():
    """Reuses the homepage's own editorial academy picks (home_config.js's
    `academy.featured`/`academy.others`) as the Squad page's Youth Academy
    preview -- same four prospects already surfaced on the homepage, so the
    Squad page isn't inventing a second, competing "who's the best prospect"
    judgment call, and isn't duplicating the full academy.html roster.
    Parsed with small field-level regexes (each academy entry is a flat
    object, no nesting) rather than a JS-literal eval, since this is
    hand-authored JS, not JSON."""
    text = HOME_CONFIG_JS.read_text(encoding="utf-8")
    section_m = ACADEMY_SECTION_RE.search(text)
    if not section_m:
        return []
    picks = []
    for entry_m in ACADEMY_ENTRY_RE.finditer(section_m.group(1)):
        block = entry_m.group(1)
        pick = {}
        for field, field_re in ACADEMY_FIELD_RES.items():
            fm = field_re.search(block)
            if fm:
                pick[field] = int(fm.group(1)) if field in ("age", "ovr") else fm.group(1)
        if pick.get("name"):
            picks.append(pick)
    return picks


def load_players():
    with open(SQUAD_CSV, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    return [row for row in rows[1:] if row and row[0].strip()]


def build():
    rows = load_players()
    stats_by_lastname = {last_name_key(k): v for k, v in load_player_stats().items()}
    gk_log = load_gk_match_log()
    season = load_season_context() or "2026/27"

    players = []
    for row in rows:
        name = row[0]
        positions = [p.strip() for p in row[1].split("/") if p.strip()]
        primary_pos = positions[0] if positions else "?"
        group = GROUP_MAP.get(primary_pos, MID)
        age = int(row[2])
        ovr = int(row[3])
        height = row[4]
        foot = row[6]
        squad_role = row[7]
        status = row[11]
        notes = row[52]
        potential = row[53].strip()

        loan = None
        loan_m = LOAN_RE.search(status)
        if loan_m:
            loan = {"club": loan_m.group(1).strip(), "back": loan_m.group(2) or None}

        dev_status = parse_dev_status(status)

        is_captain = bool(re.search(r"\bclub captain\b", notes, re.IGNORECASE))

        lk = last_name_key(name)
        stats = stats_by_lastname.get(lk)
        season_stats = None
        if stats and group == GK:
            gk = gk_log.get(lk, {"trackedApps": 0, "cleanSheets": 0, "goalsConceded": 0})
            season_stats = {
                "isGk": True,
                "apps": stats["apps"],
                "rating": stats["rating"],
                "trackedApps": gk["trackedApps"],
                "cleanSheets": gk["cleanSheets"],
                "goalsConceded": gk["goalsConceded"],
            }
        elif stats:
            season_stats = {
                "isGk": False,
                "apps": stats["apps"],
                "goals": stats["goals"],
                "assists": stats["assists"],
                "rating": stats["rating"],
            }

        players.append({
            "name": name,
            "slug": slugify(name),
            "positions": positions,
            "group": group,
            "age": age,
            "ovr": ovr,
            "height": height or None,
            "foot": foot or None,
            "squadRole": squad_role or None,
            "potential": potential or None,
            "captain": is_captain,
            "loan": loan,
            "devStatus": dev_status,
            "image": PHOTO_MAP.get(name),
            "season": season_stats,
        })

    active = [p for p in players if not p["loan"]]
    loaned = [p for p in players if p["loan"]]

    def top_by(key_fn, pool):
        pool = [p for p in pool if key_fn(p) is not None]
        return max(pool, key=key_fn) if pool else None

    glance = {
        "squadSize": len(players),
        "avgAge": round(sum(p["age"] for p in players) / len(players), 1),
        "avgOvr": round(sum(p["ovr"] for p in players) / len(players), 1),
        "highestOvr": max(players, key=lambda p: p["ovr"])["name"],
        "highestOvrValue": max(p["ovr"] for p in players),
        "youngest": min(players, key=lambda p: p["age"])["name"],
        "youngestAge": min(p["age"] for p in players),
        "onLoan": len(loaned),
        "captain": next((p["name"] for p in players if p["captain"]), None),
    }

    outfield_with_season = [p for p in players if p["season"] and not p["season"]["isGk"]]
    top_scorer = top_by(lambda p: p["season"]["goals"], outfield_with_season)
    top_assist = top_by(lambda p: p["season"]["assists"], outfield_with_season)
    if top_scorer and top_scorer["season"]["goals"] > 0:
        glance["topScorer"] = top_scorer["name"]
        glance["topScorerGoals"] = top_scorer["season"]["goals"]
    if top_assist and top_assist["season"]["assists"] > 0:
        glance["mostAssists"] = top_assist["name"]
        glance["mostAssistsValue"] = top_assist["season"]["assists"]

    leaders = {
        "goals": sorted([p for p in outfield_with_season if p["season"]["goals"] > 0],
                         key=lambda p: -p["season"]["goals"])[:5],
        "assists": sorted([p for p in outfield_with_season if p["season"]["assists"] > 0],
                           key=lambda p: -p["season"]["assists"])[:5],
        "apps": sorted([p for p in players if p["season"]], key=lambda p: -p["season"]["apps"])[:5],
        "rating": sorted([p for p in outfield_with_season if p["season"]["apps"] >= 5],
                          key=lambda p: -p["season"]["rating"])[:5],
    }

    def leader_entry(p, field):
        return {"name": p["name"], "image": p["image"], "positions": p["positions"], "value": p["season"][field]}

    leaders_out = {
        "goals": [leader_entry(p, "goals") for p in leaders["goals"]],
        "assists": [leader_entry(p, "assists") for p in leaders["assists"]],
        "apps": [leader_entry(p, "apps") for p in leaders["apps"]],
        "rating": [leader_entry(p, "rating") for p in leaders["rating"]],
    }

    featured = next((p for p in players if p["name"] == FEATURED_PLAYER), None)

    return {
        "season": season,
        "competition": "Premier League",
        "players": players,
        "featured": featured,
        "glance": glance,
        "leaders": leaders_out,
        "academyPreview": load_academy_preview(),
    }


def main():
    data = build()
    js = (
        "/* GENERATED by scripts/sync_squad_page.py -- do not hand-edit.\n"
        "   Senior-squad facts from wrexham_squad.csv; current-season Apps/G/A/Rating\n"
        "   joined in from docs/assets/player_stats.js by last-name key. Powers the\n"
        "   Squad landing page (docs/roster.html + docs/assets/squad.js).\n"
        "   Re-run after any wrexham_squad.csv change or player_stats.js refresh. */\n"
        "const SQUAD_DATA = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n"
    )
    OUT.write_text(js, encoding="utf-8")
    print(f"Wrote {OUT} — {len(data['players'])} senior players, season {data['season']}")

    # Every senior player's individual dossier page (docs/players/<slug>.html,
    # via scripts/generate_player_pages.py) reads the same wrexham_squad.csv
    # attribute columns this script does. Chaining it here means a squad/attribute
    # update can never leave those detail pages stale just because this script
    # ran without the other one -- see CLAUDE.md's "Squad Changes" checklist.
    subprocess.run([sys.executable, str(ROOT / "scripts" / "generate_player_pages.py")], check=True)


if __name__ == "__main__":
    main()
