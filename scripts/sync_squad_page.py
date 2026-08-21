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
"Match Submission Checklist").
"""
import csv
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SQUAD_CSV = ROOT / "wrexham_squad.csv"
PLAYER_STATS_JS = ROOT / "docs" / "assets" / "player_stats.js"
PL_TABLE_JS = ROOT / "docs" / "assets" / "pl_table.js"
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


LOAN_RE = re.compile(r"On Loan at ([^(]+?)\s*(?:\(back ([^)]+)\))?$")


def load_player_stats():
    text = PLAYER_STATS_JS.read_text(encoding="utf-8")
    m = re.search(r"const PLAYER_SEASON_STATS = (\{.*?\});", text, re.DOTALL)
    return json.loads(m.group(1)) if m else {}


def load_season_context():
    text = PL_TABLE_JS.read_text(encoding="utf-8")
    m = re.search(r"season:\s*'([^']+)'", text)
    return m.group(1) if m else None


def load_players():
    with open(SQUAD_CSV, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    return [row for row in rows[1:] if row and row[0].strip()]


def build():
    rows = load_players()
    stats_by_lastname = {last_name_key(k): v for k, v in load_player_stats().items()}
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

        is_captain = bool(re.search(r"\bclub captain\b", notes, re.IGNORECASE))

        stats = stats_by_lastname.get(last_name_key(name))
        season_stats = None
        if stats:
            season_stats = {
                "apps": stats["apps"],
                "goals": stats["goals"],
                "assists": stats["assists"],
                "rating": stats["rating"],
            }

        players.append({
            "name": name,
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

    top_scorer = top_by(lambda p: p["season"]["goals"] if p["season"] else None, players)
    top_assist = top_by(lambda p: p["season"]["assists"] if p["season"] else None, players)
    if top_scorer and top_scorer["season"]["goals"] > 0:
        glance["topScorer"] = top_scorer["name"]
        glance["topScorerGoals"] = top_scorer["season"]["goals"]
    if top_assist and top_assist["season"]["assists"] > 0:
        glance["mostAssists"] = top_assist["name"]
        glance["mostAssistsValue"] = top_assist["season"]["assists"]

    leaders = {
        "goals": sorted([p for p in players if p["season"] and p["season"]["goals"] > 0],
                         key=lambda p: -p["season"]["goals"])[:5],
        "assists": sorted([p for p in players if p["season"] and p["season"]["assists"] > 0],
                           key=lambda p: -p["season"]["assists"])[:5],
        "apps": sorted([p for p in players if p["season"]], key=lambda p: -p["season"]["apps"])[:5],
        "rating": sorted([p for p in players if p["season"] and p["season"]["apps"] >= 5],
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

    nationalities_note = None  # not reliably stored across the squad -- intentionally omitted

    return {
        "season": season,
        "competition": "Premier League",
        "players": players,
        "featured": featured,
        "glance": glance,
        "leaders": leaders_out,
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


if __name__ == "__main__":
    main()
