#!/usr/bin/env python3
"""Generate docs/players/<slug>.html player dossiers for the current senior squad.

Phase 3B. Data-driven, like scripts/generate_media_pages.py -- every player page
is regenerated from source data, never hand-edited. Sources (never invented):

  wrexham_squad.csv          identity/attributes/dev-plan (also drives squad_data.js)
  docs/assets/player_stats.js current-season Apps/Goals/Assists/Rating + last5
  docs/season/season-NN.html  every archived season's Player Season Stats table --
                               parsed with the same regex sync_home_player_stats.py uses,
                               one career-timeline row per rolled-over season (season
                               label/competition read from docs/season.html's own
                               "Past Seasons" links, so nothing is hand-typed per season)
  player_career_history.csv   real pre-Wrexham club career (season/club/competition/apps/goals)
  player_bios.json            recovered "Player Profile" prose (see extraction note below)
  season_log.json             transfers (direction=in), for Movement
  media-articles.json         "IN THE NEWS" -- matched via the body_html context-card-key
                               spans (structured, e.g. "Y. Amrizi"), never prose substring
                               matching
  docs/assets/media_index.js  headline/dek/date/author/url/image for matched articles

player_bios.json was extracted once from the pre-Phase-3A docs/roster.html (git commit
c08c5f6), which had hand-authored "Player Profile" bio paragraphs per senior player that
were lost when Phase 3A replaced that markup with generated squad cards. It is a durable,
committed data file now -- this script does not touch git history.

Run after any wrexham_squad.csv change, any match session (player_stats.js refresh), or
any media-articles.json change:
    python3 scripts/generate_player_pages.py
"""
import csv
import html
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SQUAD_CSV = ROOT / "wrexham_squad.csv"
CAREER_CSV = ROOT / "player_career_history.csv"
BIOS_JSON = ROOT / "player_bios.json"
SEASON_LOG = ROOT / "season_log.json"
SEASON_HTML = ROOT / "docs" / "season.html"
SEASON_LOGS_DIR = ROOT / "season_logs"
PLAYER_STATS_JS = ROOT / "docs" / "assets" / "player_stats.js"
MEDIA_ARTICLES_JSON = ROOT / "media-articles.json"
MEDIA_INDEX_JS = ROOT / "docs" / "assets" / "media_index.js"
PL_TABLE_JS = ROOT / "docs" / "assets" / "pl_table.js"
OUT_DIR = ROOT / "docs" / "players"


def load_current_season_label():
    text = PL_TABLE_JS.read_text(encoding="utf-8")
    m = re.search(r"season:\s*'([^']+)'", text)
    return m.group(1) if m else "2026/27"


def load_current_competition():
    """Most-frequent competition among this season's logged matches, so the
    live-season career row doesn't hard-code a competition name that goes
    stale on promotion/relegation. No matches logged yet (start of season)
    falls back to "Premier League" -- the current top-flight status."""
    if not SEASON_LOG.exists():
        return "Premier League"
    d = json.loads(SEASON_LOG.read_text(encoding="utf-8"))
    comps = [m["competition"] for m in d.get("matches", []) if m.get("competition")]
    if not comps:
        return "Premier League"
    return Counter(comps).most_common(1)[0][0]

# Column indices into wrexham_squad.csv / youth_academy.csv rows -- see
# CLAUDE.md's "squad CSV -- Column Index" for the authoritative reference.
COL = {
    "Pace": 12, "Shooting": 13, "Passing": 14, "Dribbling": 15, "Defending": 16, "Physical": 17,
    "Acceleration": 18, "Agility": 19, "Balance": 20, "Jumping": 21, "Sprint_Speed": 22,
    "Stamina": 23, "Strength": 24,
    "Aggression": 25, "Att_Position": 26, "Composure": 27, "Interceptions": 28,
    "Reactions": 29, "Vision": 30,
    "Ball_Control": 31, "Crossing": 32, "Curve": 33, "Def_Aware": 34, "Dribbling_Tech": 35,
    "FK_Acc": 36, "Finishing": 37, "Heading_Acc": 38, "Long_Pass": 39, "Long_Shots": 40,
    "Penalties": 41, "Short_Pass": 42, "Shot_Power": 43, "Slide_Tackle": 44, "Stand_Tackle": 45,
    "Volleys": 46,
    "Skill_Moves": 47, "Weak_Foot": 48, "PlayStyles": 49, "Roles": 50,
}

# Labels for the main-six tiles -- GKs (see CLAUDE.md's "GK mapping") reuse
# the same six CSV columns for different real-world stats.
MAIN_SIX_OUTFIELD = [("Pace", "PAC"), ("Shooting", "SHO"), ("Passing", "PAS"),
                     ("Dribbling", "DRI"), ("Defending", "DEF"), ("Physical", "PHY")]
MAIN_SIX_GK = [("Pace", "DIV"), ("Shooting", "HAN"), ("Passing", "KIC"),
              ("Dribbling", "REF"), ("Defending", "SPD"), ("Physical", "POS")]
MAIN_SIX_GK_LABELS = {"Pace": "Diving", "Shooting": "Handling", "Passing": "Kicking",
                      "Dribbling": "Reflexes", "Defending": "Speed", "Physical": "Positioning"}

PHYSICAL_ATTRS = ["Acceleration", "Agility", "Balance", "Jumping", "Sprint_Speed", "Stamina", "Strength"]
MENTAL_ATTRS = ["Aggression", "Att_Position", "Composure", "Interceptions", "Reactions", "Vision"]
TECHNICAL_ATTRS = ["Ball_Control", "Crossing", "Curve", "Def_Aware", "Dribbling_Tech", "FK_Acc",
                   "Finishing", "Heading_Acc", "Long_Pass", "Long_Shots", "Penalties",
                   "Short_Pass", "Shot_Power", "Slide_Tackle", "Stand_Tackle", "Volleys"]
ATTR_LABELS = {
    "Att_Position": "Att. Position", "Def_Aware": "Def. Awareness", "Dribbling_Tech": "Dribbling",
    "FK_Acc": "FK Accuracy", "Heading_Acc": "Heading Acc.", "Sprint_Speed": "Sprint Speed",
    "Ball_Control": "Ball Control", "Long_Pass": "Long Pass", "Long_Shots": "Long Shots",
    "Short_Pass": "Short Pass", "Shot_Power": "Shot Power", "Slide_Tackle": "Slide Tackle",
    "Stand_Tackle": "Stand Tackle",
}


def attr_label(key):
    return ATTR_LABELS.get(key, key.replace("_", " "))


GK, DEF, MID, FWD = "Goalkeepers", "Defenders", "Midfielders", "Forwards"
GROUP_MAP = {
    "GK": GK, "CB": DEF, "RB": DEF, "LB": DEF,
    "CDM": MID, "CM": MID, "CAM": MID, "LM": MID, "RM": MID,
    "ST": FWD, "LW": FWD, "RW": FWD, "CF": FWD,
}

# Same PHOTO_MAP as scripts/sync_squad_page.py (kept in sync manually -- both
# read the same approved-imagery set; see that script's comment on why
# Santiago Ortega has no entry).
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
}


def strip_accents(s):
    d = unicodedata.normalize("NFKD", s)
    return "".join(c for c in d if not unicodedata.combining(c))


def slugify(name):
    ascii_name = strip_accents(name).lower()
    ascii_name = re.sub(r"[^a-z0-9]+", "-", ascii_name).strip("-")
    return ascii_name


def last_name_key(name):
    token = name.strip().split()[-1] if name.strip() else name
    return strip_accents(token).lower()


def esc(s):
    return html.escape(str(s), quote=True)


# ── Load sources ────────────────────────────────────────────────────────────

def load_squad_rows():
    with open(SQUAD_CSV, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    return [r for r in rows[1:] if r and r[0].strip()]


def load_career_history():
    by_player = {}
    with open(CAREER_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            name = row["Player"]
            if not row.get("Season") or not row["Season"].strip():
                continue  # unconfirmed/no-history rows (Season blank)
            by_player.setdefault(name, []).append({
                "season": row["Season"], "club": row["Club"],
                "competition": row["Competition"],
                "apps": int(row["Apps"]) if row["Apps"] else None,
                "goals": int(row["Goals"]) if row["Goals"] else None,
            })
    for rows in by_player.values():
        rows.sort(key=lambda r: r["season"])
    return by_player


def load_bios():
    return json.loads(BIOS_JSON.read_text(encoding="utf-8"))


def load_current_season_stats():
    text = PLAYER_STATS_JS.read_text(encoding="utf-8")
    m = re.search(r"const PLAYER_SEASON_STATS = (\{.*?\});", text, re.DOTALL)
    return json.loads(m.group(1)) if m else {}


SEASON_ARCHIVE_ROW_RE = re.compile(
    r'<div class="stats-row">\s*'
    r'<div><div class="s-name">(?P<name>.*?)</div><div class="s-pos">(?P<pos>.*?)</div></div>\s*'
    r'<span class="s-num">(?P<apps>\d+)</span>\s*'
    r'<span class="s-num(?: highlight)?">(?P<goals>\d+)</span>\s*'
    r'<span class="s-num(?: highlight)?">(?P<assists>\d+)</span>\s*'
    r'<span class="s-motm">(?P<motm>.*?)</span>\s*'
    r'<span class="s-rating">(?P<rating>[\d.]+)</span>',
    re.S,
)

PAST_SEASON_LINK_RE = re.compile(
    r'<a href="season/(season-(?P<num>\d+)\.html)"[^>]*>'
    r'Season \d+ ·\s*(?P<year>[\d&;a-z]+?)\s*&middot;\s*(?P<desc>.*?)\s*\(',
    re.S,
)


def load_archived_seasons_stats():
    """Every archived Wrexham season (docs/season/season-NN.html), not just
    Season 1 -- each rolled-over season must keep contributing a real row to
    every player's career timeline on their dossier, or the timeline silently
    stops the moment a season is archived (this happened for real: Season 2,
    2026/27, the Premier League + FA Cup double, was missing entirely from
    every dossier until this generalization). Season label/competition text
    is read from docs/season.html's "Past Seasons" links so nothing here is
    hand-typed per season; table shape is the same one docs/season.html uses
    for the live season, just frozen in each archive file.

    Returns {season_num: {"season": "2025/26", "competition": "...",
                           "stats": {last_name_key: {"apps", "goals"}}}}
    """
    seasons = {}
    if not SEASON_HTML.exists():
        return seasons
    index_text = SEASON_HTML.read_text(encoding="utf-8")
    for lm in PAST_SEASON_LINK_RE.finditer(index_text):
        num = int(lm.group("num"))
        year = html.unescape(lm.group("year")).replace("–", "/").replace("-", "/").strip()
        desc = html.unescape(lm.group("desc")).strip()
        competition = desc.split(",", 1)[1].strip() if "," in desc else desc

        archive_path = ROOT / "docs" / "season" / f"season-{num:02d}.html"
        if not archive_path.exists():
            continue
        text = archive_path.read_text(encoding="utf-8")
        start = text.find("PLAYER SEASON STATS")
        if start == -1:
            continue
        end = text.find('<div class="footer">', start)
        table_html = text[start: end if end != -1 else len(text)]
        stats = {}
        for m in SEASON_ARCHIVE_ROW_RE.finditer(table_html):
            name = html.unescape(m.group("name")).strip()
            stats[last_name_key(name)] = {
                "apps": int(m.group("apps")), "goals": int(m.group("goals")),
            }
        seasons[num] = {"season": year, "competition": competition, "stats": stats}
    return seasons


def load_transfers_in(squad_names):
    """Joined-Wrexham transfer, keyed by last-name -- merges the current
    season_log.json (full player names) with every archived season_logs/
    season-NN.json (which used abbreviated "F. Lastname" names for this
    field), taking the earliest "in" transfer on record per player."""
    by_lastname = {}
    sources = [SEASON_LOG]
    if SEASON_LOGS_DIR.exists():
        sources.extend(sorted(SEASON_LOGS_DIR.glob("season-*.json")))
    for src in sources:
        d = json.loads(src.read_text(encoding="utf-8"))
        for t in d.get("transfers", []):
            if t.get("direction") != "in":
                continue
            lk = last_name_key(t["player"])
            if lk not in by_lastname or t["date"] < by_lastname[lk]["date"]:
                by_lastname[lk] = t
    # Re-key by full current squad name for easy lookup.
    by_name = {}
    for name in squad_names:
        t = by_lastname.get(last_name_key(name))
        if t:
            by_name[name] = t
    return by_name


def load_gk_match_log():
    """Per-goalkeeper defensive log derived from season_log.json's player_ratings
    (which matches were actually played) joined to that match's score (always
    "Wrexham-Opponent", verified against the `result` field). Deliberately
    scoped to *tracked* appearances only -- player_ratings only covers matches
    with a captured ratings screenshot, so this is a real but partial sample,
    never conflated with the full-season Apps figure from player_stats.js."""
    d = json.loads(SEASON_LOG.read_text(encoding="utf-8"))
    by_lastname = {}
    for m in d["matches"]:
        score = m.get("score")
        pr = m.get("player_ratings")
        if not score or not pr:
            continue
        wg, og = (int(x) for x in score.split("-"))
        for pkey, rating in pr.items():
            lk = last_name_key(pkey)
            by_lastname.setdefault(lk, []).append({
                "date": m["date"], "opponent": m["opponent"],
                "conceded": og, "clean_sheet": og == 0, "rating": rating,
            })
    return by_lastname


PROMOTED_RE = re.compile(r"Promoted to the first team on ([^.,]+)")
CAPTAIN_RE = re.compile(r"\bclub captain\b", re.IGNORECASE)

# FC26's development-status classification, stored as free text at the front
# of the Status column (col 11). Same source/logic as
# scripts/sync_squad_page.py's parse_dev_status -- kept in sync manually
# since these are small standalone scripts with no shared module.
DEV_STATUS_MAP = [
    ("Has Potential To Be Special", "HPTBS"),
    ("An Exciting Prospect", "EP"),
    ("Showing Great Potential", "SGP"),
]
DEV_STATUS_TITLES = {"HPTBS": "Has Potential To Be Special", "EP": "Exciting Prospect", "SGP": "Showing Great Potential"}


def parse_dev_status(status_text):
    for phrase, code in DEV_STATUS_MAP:
        if phrase in status_text:
            return {"code": code, "label": DEV_STATUS_TITLES[code]}
    return None
CONTEXT_KEY_RE = re.compile(r'<span class="context-card-key">([^<]+)</span>')
PLAYER_TAG_RE = re.compile(r"^[A-ZÀ-Ý]{1,2}\.(?:[A-ZÀ-Ý]\.)?\s+[A-ZÀ-Ý]")


def load_media_index():
    text = MEDIA_INDEX_JS.read_text(encoding="utf-8")
    m = re.search(r"const MEDIA_INDEX = (\{.*\});", text, re.DOTALL)
    return json.loads(m.group(1))


def build_media_matches():
    """Player -> list of article ids, matched via body_html's structured
    context-card-key spans (e.g. "Y. Amrizi") rather than prose substring
    search, to avoid false positives from partial-name collisions."""
    articles = json.loads(MEDIA_ARTICLES_JSON.read_text(encoding="utf-8"))
    by_lastname = {}
    for a in articles:
        keys = CONTEXT_KEY_RE.findall(a.get("body_html", ""))
        player_keys = {k for k in keys if PLAYER_TAG_RE.match(k)}
        for pk in player_keys:
            lk = last_name_key(pk)
            by_lastname.setdefault(lk, []).append((a["date"], a["id"]))
    for lk in by_lastname:
        by_lastname[lk].sort(key=lambda x: x[0], reverse=True)
    return by_lastname


# ── Build per-player data ───────────────────────────────────────────────────

def opponent_tag(opponent):
    first = opponent.split()[0]
    return first[:3].upper()


def build_players(rows, career_history, bios, current_stats, archived_seasons,
                   transfers_in, gk_log, media_matches, media_index,
                   current_season_label, current_competition):
    players = []
    by_group = {GK: [], DEF: [], MID: [], FWD: []}
    for row in rows:
        name = row[0]
        positions = [p.strip() for p in row[1].split("/") if p.strip()]
        primary = positions[0] if positions else "?"
        group = GROUP_MAP.get(primary, MID)
        age, ovr = int(row[2]), int(row[3])
        height, foot = row[4] or None, row[6] or None
        squad_role = row[7] or None
        contract_length = row[8] or None
        status = row[11]
        dev_plan = row[51] or None
        notes = row[52]
        potential = row[53].strip() or None

        def cell(key):
            v = row[COL[key]].strip() if COL[key] < len(row) else ""
            return int(v) if v.isdigit() else None

        main_six_defs = MAIN_SIX_GK if group == GK else MAIN_SIX_OUTFIELD
        main_six = [{"label": lbl, "value": cell(key)} for key, lbl in main_six_defs]
        if group == GK:
            main_six = [m for m in main_six if m["value"] is not None]

        def sub_group(keys):
            out = [{"label": attr_label(k), "value": cell(k)} for k in keys]
            return [o for o in out if o["value"] is not None]

        attributes = {
            "main_six": main_six,
            "physical": sub_group(PHYSICAL_ATTRS),
            "mental": sub_group(MENTAL_ATTRS),
            "technical": sub_group(TECHNICAL_ATTRS),
            "skill_moves": cell("Skill_Moves"),
            "weak_foot": cell("Weak_Foot"),
            "playstyles": [s.strip() for s in re.split(r"[,/]", row[COL["PlayStyles"]]) if s.strip() and s.strip().lower() != "none"],
            "roles": cell("Roles"),
        }

        loan_m = re.search(r"On Loan at ([^(]+?)\s*(?:\(back ([^)]+)\))?$", status)
        loan = {"club": loan_m.group(1).strip(), "back": loan_m.group(2)} if loan_m else None
        is_captain = bool(CAPTAIN_RE.search(notes))
        dev_status = parse_dev_status(status)

        lk = last_name_key(name)
        stats = current_stats.get(name) or next(
            (v for k, v in current_stats.items() if last_name_key(k) == lk), None)
        if group == GK:
            gk_matches = gk_log.get(lk, [])
            season = {
                "apps": stats["apps"] if stats else None,
                "avgRating": stats["rating"] if stats else None,
                "trackedApps": len(gk_matches),
                "cleanSheets": sum(1 for x in gk_matches if x["clean_sheet"]),
                "goalsConceded": sum(x["conceded"] for x in gk_matches),
            }
        else:
            season = {
                "apps": stats["apps"] if stats else None,
                "goals": stats["goals"] if stats else None,
                "assists": stats["assists"] if stats else None,
                "avgRating": stats["rating"] if stats else None,
            }
        last5 = []
        if stats and stats.get("last5"):
            by_date = {}
            d = json.loads(SEASON_LOG.read_text(encoding="utf-8"))
            for m in d["matches"]:
                by_date[m["date"]] = m["opponent"]
            for pt in stats["last5"]:
                opp = by_date.get(pt["date"])
                last5.append({"tag": opponent_tag(opp) if opp else "—", "rating": pt["rating"]})

        career = list(career_history.get(name, []))
        for num in sorted(archived_seasons):
            archived = archived_seasons[num]
            s = archived["stats"].get(lk)
            if not s:
                continue
            career.append({"season": archived["season"], "club": "Wrexham", "competition": archived["competition"],
                            "apps": s["apps"], "goals": None if group == GK else s["goals"]})
        if season.get("apps"):
            career.append({"season": current_season_label, "club": "Wrexham", "competition": current_competition,
                            "apps": season["apps"], "goals": None if group == GK else season.get("goals")})

        bio = bios.get(name, {}).get("paragraphs", [])
        promoted_m = PROMOTED_RE.search(" ".join(bio))
        pathway = f"Wrexham Academy → First Team ({promoted_m.group(1).strip()})" if promoted_m else None
        transfer = transfers_in.get(name)

        article_ids = [aid for _, aid in media_matches.get(lk, [])][:5]
        news = []
        for aid in article_ids:
            a = media_index["articles"].get(aid)
            if not a:
                continue
            person = media_index["people"].get(a["author_id"], {})
            news.append({
                "headline": a["headline"], "dek": a["dek"], "date_label": a["date_label"],
                "outlet": a["outlet"], "author": person.get("name", a["author_id"]),
                "url": a["url"], "image": a.get("image"),
            })

        player = {
            "name": name, "slug": slugify(name), "positions": positions, "group": group,
            "age": age, "height": height, "foot": foot, "ovr": ovr, "potential": potential,
            "squad_role": squad_role, "contract_length": contract_length, "captain": is_captain,
            "loan": loan, "dev_status": dev_status, "dev_plan": dev_plan, "image": PHOTO_MAP.get(name),
            "season": season, "last5": last5, "career": career, "bio": bio,
            "pathway": pathway, "transfer": transfer, "news": news, "attributes": attributes,
        }
        players.append(player)
        by_group[group].append(player)
    return players, by_group


# ── HTML rendering ───────────────────────────────────────────────────────────

def render_stat(label, value, gold=False):
    if value is None:
        return ""
    cls = "player-stat gold" if gold else "player-stat"
    return f'<div class="{cls}"><span class="player-stat-value">{esc(value)}</span><span class="player-stat-label">{esc(label)}</span></div>'


def render_identity_fact(label, value):
    if value in (None, ""):
        return ""
    return f'<div class="player-fact"><span class="player-fact-value">{esc(value)}</span><span class="player-fact-label">{esc(label)}</span></div>'


def render_season_block(p, season_label):
    s = p["season"]
    stats = []
    if p["group"] == GK:
        stats.append(render_stat("Appearances", s.get("apps"), gold=True))
        if s.get("trackedApps"):
            stats.append(render_stat("Clean Sheets", s.get("cleanSheets")))
            stats.append(render_stat("Goals Conceded", s.get("goalsConceded")))
            ga = round(s["goalsConceded"] / s["trackedApps"], 2) if s["trackedApps"] else None
            stats.append(render_stat("GA/APP", ga))
        stats.append(render_stat("Avg Rating", s.get("avgRating"), gold=True))
    else:
        stats.append(render_stat("Appearances", s.get("apps"), gold=True))
        stats.append(render_stat("Goals", s.get("goals")))
        stats.append(render_stat("Assists", s.get("assists")))
        stats.append(render_stat("Avg Rating", s.get("avgRating"), gold=True))
    stats = [x for x in stats if x]
    if not stats:
        return ""
    note = ""
    if p["group"] == GK and s.get("trackedApps"):
        note = (f'<p class="player-season-note">Clean sheets / goals conceded are tracked from '
                f'{s["trackedApps"]} appearance{"s" if s["trackedApps"] != 1 else ""} with a recorded '
                f'match rating this season, not the full {s.get("apps") or "?"} appearances -- they '
                f'fill in as more post-match ratings screens are captured.</p>')
    elif p["group"] == GK:
        note = '<p class="player-season-note">Clean sheets and goals conceded aren’t tracked yet this season -- they need a post-match ratings screenshot to derive from.</p>'
    return f'''
  <section class="player-section player-season" aria-label="Current season">
    <div class="player-section-head"><h2>{esc(season_label)} Season</h2></div>
    <div class="player-stat-grid">{''.join(stats)}</div>
    {note}
  </section>'''


def render_attributes(p):
    a = p["attributes"]
    if not a["main_six"] and not a["physical"] and not a["mental"] and not a["technical"]:
        return ""

    tiles = "".join(render_stat(m["label"], m["value"], gold=True) for m in a["main_six"] if m["value"] is not None)
    main_six_html = f'<div class="player-stat-grid">{tiles}</div>' if tiles else ""

    def sub_block(title, items):
        if not items:
            return ""
        rows = "".join(
            f'<div class="context-card-row"><span class="context-card-key">{esc(i["label"])}</span>'
            f'<span class="context-card-val">{esc(i["value"])}</span></div>'
            for i in items
        )
        return f'<div class="context-card"><div class="context-card-label">{esc(title)}</div>{rows}</div>'

    sub_html = (
        sub_block("Physical", a["physical"])
        + sub_block("Mental", a["mental"])
        + sub_block("Technical", a["technical"])
    )
    sub_wrap = f'<div class="player-attr-subgrid">{sub_html}</div>' if sub_html else ""

    extras = []
    if a["skill_moves"]:
        extras.append(f'<div class="context-card-row"><span class="context-card-key">Skill Moves</span><span class="context-card-val">{"★" * a["skill_moves"]}{"☆" * (5 - a["skill_moves"])}</span></div>')
    if a["weak_foot"]:
        extras.append(f'<div class="context-card-row"><span class="context-card-key">Weak Foot</span><span class="context-card-val">{"★" * a["weak_foot"]}{"☆" * (5 - a["weak_foot"])}</span></div>')
    if a["roles"] is not None:
        extras.append(f'<div class="context-card-row"><span class="context-card-key">Roles (+/++)</span><span class="context-card-val">{a["roles"]}</span></div>')
    extras_html = f'<div class="context-card">{"".join(extras)}</div>' if extras else ""

    playstyles_html = ""
    if a["playstyles"]:
        chips = "".join(f'<span class="player-playstyle-chip">{esc(ps)}</span>' for ps in a["playstyles"])
        playstyles_html = f'<div class="player-playstyles"><span class="context-card-key">PlayStyles</span><div class="player-playstyle-list">{chips}</div></div>'

    return f'''
  <section class="player-section player-attributes" aria-label="Attributes">
    <div class="player-section-head"><h2>Attributes</h2></div>
    {main_six_html}
    {sub_wrap}
    {extras_html}
    {playstyles_html}
  </section>'''


def render_form(p):
    if not p["last5"]:
        return ""
    pips = "".join(
        f'<div class="player-form-pip"><span class="player-form-opp">{esc(pt["tag"])}</span>'
        f'<span class="player-form-rating">{esc(pt["rating"])}</span></div>'
        for pt in p["last5"]
    )
    return f'''
  <section class="player-section player-form-section" aria-label="Recent form">
    <div class="player-section-head"><h2>Last {len(p["last5"])}</h2></div>
    <div class="player-form">{pips}</div>
  </section>'''


def render_career(p):
    if not p["career"]:
        return ""
    rows = []
    for c in p["career"]:
        bits = []
        if c.get("apps") is not None:
            bits.append(f'{c["apps"]} Apps')
        if c.get("goals") is not None:
            bits.append(f'{c["goals"]} Goals')
        stat_line = " &middot; ".join(bits)
        rows.append(f'''
      <div class="player-career-season">
        <div class="player-career-season-label">{esc(c["season"])}</div>
        <div class="player-career-club">{esc(c["club"])}<span class="player-career-comp">{esc(c["competition"])}</span></div>
        <div class="player-career-stats">{stat_line}</div>
      </div>''')
    dev = ""
    if p["dev_plan"] and ("→" in p["dev_plan"] or "->" in p["dev_plan"]):
        dev = f'<p class="player-development">Current development: {esc(p["dev_plan"])}</p>'
    elif p["potential"]:
        dev = f'<p class="player-development">Potential range: <strong>{esc(p["potential"])}</strong></p>'
    return f'''
  <section class="player-section player-career" aria-label="Career history">
    <div class="player-section-head"><h2>Career</h2></div>
    <div class="player-career-list">{''.join(rows)}</div>
    {dev}
  </section>'''


def render_movement(p):
    items = []
    if p["pathway"]:
        items.append(f'<div class="player-movement-item"><span class="player-movement-label">Pathway</span><span class="player-movement-value">{esc(p["pathway"])}</span></div>')
    t = p["transfer"]
    if t:
        fee = f' &middot; {esc(t["fee"])}' if t.get("fee") else ""
        club = f' from {esc(t["club"])}' if t.get("club") else ""
        items.append(f'<div class="player-movement-item"><span class="player-movement-label">Joined Wrexham</span><span class="player-movement-value">{esc(t["date"])}{club}{fee}</span></div>')
    if p["loan"]:
        back = f' &middot; back {esc(p["loan"]["back"])}' if p["loan"].get("back") else ""
        items.append(f'<div class="player-movement-item"><span class="player-movement-label">Currently on loan</span><span class="player-movement-value">{esc(p["loan"]["club"])}{back}</span></div>')
    if not items:
        return ""
    return f'''
  <section class="player-section player-movement" aria-label="Transfer and loan history">
    <div class="player-section-head"><h2>Movement</h2></div>
    <div class="player-movement-list">{''.join(items)}</div>
  </section>'''


def render_news(p):
    if not p["news"]:
        return ""
    cards = []
    for n in p["news"]:
        img = ""
        if n["image"]:
            img = f'<div class="player-news-media"><img src="../{esc(n["image"])}" alt="" loading="lazy" width="320" height="200"></div>'
        url = n["url"]
        href = ("../" + url) if not url.startswith("http") else url
        cards.append(f'''
      <a class="player-news-card" href="{esc(href)}">
        {img}
        <div class="player-news-body">
          <span class="player-news-outlet">{esc(n["outlet"])}</span>
          <div class="player-news-headline">{esc(n["headline"])}</div>
          <span class="player-news-meta">{esc(n["author"])} &middot; {esc(n["date_label"])}</span>
        </div>
      </a>''')
    return f'''
  <section class="player-section player-news-section" aria-label="Media coverage">
    <div class="player-section-head"><h2>In the News</h2></div>
    <div class="player-news-grid">{''.join(cards)}</div>
  </section>'''


def render_teammates(p, by_group):
    pool = [t for t in by_group[p["group"]] if t["name"] != p["name"] and not t["loan"]]
    pool.sort(key=lambda t: -t["ovr"])
    pool = pool[:4]
    if not pool:
        return ""
    cards = []
    for t in pool:
        media = f'<img src="../{esc(t["image"])}" alt="" loading="lazy" width="160" height="200">' if t["image"] else '<div class="player-teammate-placeholder"></div>'
        cards.append(f'''
      <a class="player-teammate-card" href="{esc(t["slug"])}.html">
        <div class="player-teammate-media">{media}</div>
        <span class="player-teammate-name">{esc(t["name"])}</span>
        <span class="player-teammate-meta">{esc('/'.join(t["positions"]))} &middot; {t["ovr"]} OVR</span>
      </a>''')
    return f'''
  <section class="player-section player-teammates" aria-label="Teammates">
    <div class="player-section-head"><h2>Teammates &middot; {esc(p["group"])}</h2></div>
    <div class="player-teammates-grid">{''.join(cards)}</div>
  </section>'''


PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{name} · Wrexham AFC</title>
  <meta name="description" content="{name} — Wrexham AFC player dossier: identity, current-season form, career history and media coverage under Keeyvon Jenkins.">
  <link rel="stylesheet" href="../assets/style.css">
<link rel="manifest" href="../manifest.json">
<meta name="theme-color" content="#C8102E">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="WRXM FC26">
<link rel="apple-touch-icon" href="../assets/icons/icon-192.png">
</head>
<body class="home-body player-page">

<a class="home-skip-link" href="#player-main">Skip to main content</a>

<header class="home-header">
  <div class="home-header-inner">
    <a class="home-brand" href="../index.html">
      <img class="home-brand-crest" src="../assets/photos/wrexham-crest.png" alt="Wrexham AFC crest">
      <span class="home-brand-text">
        <span class="home-brand-title">The Jenkins Era</span>
        <span class="home-brand-sub">Wrexham AFC · The Keevyon Jenkins Years</span>
      </span>
    </a>
    <div class="home-header-meta">
      <span class="home-header-season">Season 2026&ndash;27</span>
      <span class="home-header-comp">Premier League</span>
    </div>
  </div>
  <nav class="home-primary-nav" aria-label="Primary">
    <div class="home-primary-nav-inner">
      <a href="../index.html" class="home-nav-link">Home</a>
      <a href="../media/index.html" class="home-nav-link">News</a>
      <a href="../season.html" class="home-nav-link">Matches</a>
      <a href="../roster.html" class="home-nav-link is-active" aria-current="page">Squad</a>
      <a href="../academy.html" class="home-nav-link">Academy</a>
      <a href="../history.html" class="home-nav-link">The Jenkins Era</a>
      <a href="../season.html#player-stats" class="home-nav-link">Stats</a>
    </div>
  </nav>
  <nav class="home-utility-nav" aria-label="Secondary">
    <div class="home-utility-nav-inner">
      <a href="../roster.html">← First Team</a>
      <a href="../depth_chart.html">Depth Chart</a>
      <a href="../season.html#player-stats">Stats</a>
    </div>
  </nav>
</header>

<main class="player-shell" id="player-main">

  <section class="player-hero">
    <div class="player-hero-media">
      {hero_img}
    </div>
    <div class="player-identity">
      {identity_badges}
      <div class="player-name">{name_html}</div>
      <div class="player-position">{positions}</div>
      <div class="player-fact-row">{facts}</div>
      {role_line}
    </div>
  </section>

  {bio_section}
  {attributes_section}
  {season_section}
  {form_section}
  {career_section}
  {movement_section}
  {news_section}
  {teammates_section}

  <nav class="player-footer-nav" aria-label="Player navigation">
    <a href="../roster.html">← First Team</a>
    <a href="../depth_chart.html">Depth Chart</a>
    <a href="../season.html#player-stats">Full Season Stats</a>
  </nav>

</main>

<footer class="home-footer">
  <div class="home-footer-inner">
    <div class="home-footer-brand">
      <img class="home-footer-crest" src="../assets/photos/wrexham-crest.png" alt="">
      <div>
        <span class="home-footer-title">The Jenkins Era</span>
        <span class="home-footer-sub">Wrexham AFC · The Keevyon Jenkins Years</span>
      </div>
    </div>
    <nav class="home-footer-links" aria-label="Footer">
      <a href="../media/index.html">Media Centre</a>
      <a href="../journal.html">Journal</a>
      <a href="../season.html">Season</a>
      <a href="../roster.html">Squad</a>
      <a href="../depth_chart.html">Depth Chart</a>
      <a href="../academy.html">Academy</a>
      <a href="../history.html">History</a>
    </nav>
    <p class="home-footer-disclosure">An FC26 career-mode history project documenting the fictional managerial
      career of Keevyon Jenkins at Wrexham AFC. Not affiliated with, endorsed by, or connected to Wrexham AFC,
      the Premier League, the EFL, EA Sports, or any broadcaster or publication.</p>
  </div>
</footer>

</body>
</html>
"""


def render_player_page(p, by_group, season_label):
    if p["image"]:
        hero_img = f'<img src="../{esc(p["image"])}" alt="{esc(p["name"])}" loading="eager" width="1200" height="1500">'
    else:
        hero_img = '<div class="player-hero-placeholder"></div>'

    facts = [
        render_identity_fact("Age", p["age"]),
        render_identity_fact("Height", p["height"]),
        render_identity_fact("Foot", p["foot"]),
        render_identity_fact("OVR", p["ovr"]),
        render_identity_fact("Potential", p["potential"]),
    ]
    facts = "".join(f for f in facts if f)

    role_bits = []
    if p["squad_role"]:
        role_bits.append(p["squad_role"])
    if p["contract_length"]:
        role_bits.append(f'Contract: {p["contract_length"]}')
    role_line = f'<div class="player-role-line">{" &middot; ".join(esc(b) for b in role_bits)}</div>' if role_bits else ""

    captain_badge = '<span class="player-captain-badge">Club Captain</span>' if p["captain"] else ""
    dev_status_badge = ""
    if p["dev_status"]:
        code, label = p["dev_status"]["code"], p["dev_status"]["label"]
        dev_status_badge = (
            f'<span class="dev-status-badge dev-status-{code.lower()}" title="{esc(label)}">{esc(code)}</span>'
        )
    identity_badges = (
        f'<div class="player-badges">{captain_badge}{dev_status_badge}</div>'
        if (captain_badge or dev_status_badge) else ""
    )

    bio_paras = "".join(f'<p>{esc(b)}</p>' for b in p["bio"][:2]) if p["bio"] else ""
    bio_section = f'''
  <section class="player-section player-bio" aria-label="Player profile">
    <div class="player-section-head"><h2>Profile</h2></div>
    <div class="player-bio-text">{bio_paras}</div>
  </section>''' if bio_paras else ""

    return PAGE_TEMPLATE.format(
        name=esc(p["name"]), name_html=esc(p["name"]),
        hero_img=hero_img, identity_badges=identity_badges, positions=esc("/".join(p["positions"])),
        facts=facts, role_line=role_line, bio_section=bio_section,
        attributes_section=render_attributes(p),
        season_section=render_season_block(p, season_label), form_section=render_form(p),
        career_section=render_career(p), movement_section=render_movement(p),
        news_section=render_news(p), teammates_section=render_teammates(p, by_group),
    )


def main():
    rows = load_squad_rows()
    career_history = load_career_history()
    bios = load_bios()
    current_stats = load_current_season_stats()
    archived_seasons = load_archived_seasons_stats()
    transfers_in = load_transfers_in([r[0] for r in rows])
    gk_log = load_gk_match_log()
    media_matches = build_media_matches()
    media_index = load_media_index()
    season_label = load_current_season_label()
    current_competition = load_current_competition()

    players, by_group = build_players(
        rows, career_history, bios, current_stats, archived_seasons,
        transfers_in, gk_log, media_matches, media_index,
        season_label, current_competition,
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for existing in OUT_DIR.glob("*.html"):
        existing.unlink()

    for p in players:
        html_out = render_player_page(p, by_group, season_label)
        (OUT_DIR / f'{p["slug"]}.html').write_text(html_out, encoding="utf-8")

    slugs = {p["name"]: p["slug"] for p in players}
    (ROOT / "docs" / "assets" / "player_slugs.json").write_text(
        json.dumps(slugs, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Generated {len(players)} player dossiers in {OUT_DIR}")


if __name__ == "__main__":
    main()
