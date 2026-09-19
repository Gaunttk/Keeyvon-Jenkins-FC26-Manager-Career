#!/usr/bin/env python3
"""Squad performance + depth audit, derived entirely from data already in the repo.

This is the analysis that used to be done by hand in a Claude session (see
Earle Durow's 2027-11-16 briefing in media-articles.json, which this script
reproduces the arithmetic for). Nothing here is a judgement call -- it is
deterministic aggregation over season_log.json, wrexham_squad.csv and
youth_academy.csv. Run it after any match session; the interpretation is
still a human/Claude job, but the numbers should never be recomputed by hand
again.

    python3 scripts/squad_analysis.py              # full report
    python3 scripts/squad_analysis.py --json       # machine-readable
    python3 scripts/squad_analysis.py --section usage

WHY "RATING VS OWN TEAM" IS THE CORE METRIC
-------------------------------------------
A raw average match rating rewards whoever happened to play in the wins. Every
player here is therefore scored as his rating *minus his own team's average
rating in that same match* ("rel"), which cancels out opposition strength,
home/away and whether the team collapsed that day. A 7.0 in a 0-4 defeat is a
better performance than a 7.0 in a 4-1 win, and rel says so.

MINUTES, AND WHY THEY MAY BE ABSENT
-----------------------------------
Matches may carry an optional `lineup` field (see "Season Log Schema" in
CLAUDE.md) giving each player's position and on/off minutes. When it is
present this script weights everything by minutes and reports per-90 output.
When it is absent it falls back to the only appearance signal that exists --
presence in `player_ratings` -- which cannot tell a 90-minute starter from a
70th-minute substitute. The report states which mode each section ran in
rather than quietly mixing them. Matches without `lineup` are never given
invented minutes.

COMPETITION SCOPE
-----------------
Pre-season/invitational fixtures are excluded from the competitive splits by
default: they are 18-20 player rating dumps against opposition that isn't
trying, and they inflate every fringe player's numbers. Youth Academy matches
never carry senior `player_ratings` and are ignored entirely here.
"""
import argparse
import csv
import itertools
import json
import os
import statistics as st
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEASON_LOG = ROOT / "season_log.json"
SQUAD_CSV = ROOT / "wrexham_squad.csv"
ACADEMY_CSV = ROOT / "youth_academy.csv"

# Competitions that count toward the "competitive" split. Anything not listed
# is treated as a warm-up/invitational and reported separately.
COMPETITIVE = {
    "Premier League",
    "UEFA Champions League",
    "Carabao Cup",
    "FA Cup",
    "FA Community Shield",
    "UEFA Europa League",
    "UEFA Conference League",
    "EFL Championship",
}
LEAGUE = "Premier League"
# Youth competitions carry no senior ratings; never part of a senior audit.
YOUTH_MARKERS = ("Youth Academy", "Youth League")

# Minimum sample sizes. Below these a line is suppressed rather than shown with
# a caveat -- a two-match average masquerading as a rating is worse than a gap.
MIN_APPS = 4
MIN_PAIR = 6

# FC26 scouting tiers, keyed off the ceiling of a player's Potential range.
# The `Status` column carries the game's own wording for players still being
# scouted; a closed range (blank Potential on a senior) means fully scouted.
TIERS = [(91, "HPTBS"), (85, "EP"), (80, "SGP")]
TIER_WORDS = [
    ("potential to be special", "HPTBS"),
    ("exciting prospect", "EP"),
    ("showing great potential", "SGP"),
]
# Which slot on the pitch each squad position feeds. A player with a slash
# list covers every slot he lists; the depth ladder reports him under each.
SLOTS = ["GK", "RB", "CB", "LB", "CDM", "CM", "CAM", "RW", "LW", "ST"]
SLOT_ALIASES = {"RM": "RW", "LM": "LW"}


def deaccent(s):
    return "".join(
        c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c)
    ).lower()


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def load_roster():
    """Squad + academy rows, keyed by full name, with a last-name index for
    resolving the abbreviated "F. Lastname" form used in season_log.json.

    Raises on a last-name collision rather than silently merging two players'
    numbers -- that failure mode is invisible in the output and would quietly
    corrupt every table below it."""
    people, last_index = {}, defaultdict(list)
    for path, squad in ((SQUAD_CSV, True), (ACADEMY_CSV, False)):
        with open(path, newline="", encoding="utf-8") as f:
            for row in list(csv.reader(f))[1:]:
                if not row or not row[0].strip():
                    continue
                name = row[0]
                people[name] = {
                    "name": name,
                    "pos": row[1],
                    "age": int(row[2]),
                    "ovr": int(row[3]),
                    "role": row[7],
                    "status": row[11],
                    "potential": row[53].strip(),
                    "senior": squad,
                }
                last_index[deaccent(name.split()[-1])].append(name)
    clashes = {k: v for k, v in last_index.items() if len(v) > 1}
    if clashes:
        raise SystemExit(
            "Ambiguous surnames -- season_log.json's 'F. Lastname' keys cannot be "
            "resolved safely: " + "; ".join(f"{k}: {v}" for k, v in clashes.items())
        )
    return people, {k: v[0] for k, v in last_index.items()}


def load_matches(people, last_index):
    """Senior matches carrying player ratings, with names resolved to the CSV
    spelling and each match's team-average rating precomputed."""
    log = json.loads(SEASON_LOG.read_text(encoding="utf-8"))
    out, unresolved = [], set()
    for m in log.get("matches", []):
        if any(y in m["competition"] for y in YOUTH_MARKERS):
            continue
        ratings = m.get("player_ratings") or {}
        if not ratings:
            continue
        resolved = {}
        for key, value in ratings.items():
            full = last_index.get(deaccent(key.split()[-1]))
            if full is None:
                unresolved.add(key)
                continue
            # A departed player keeps his historical ratings; keep the higher
            # value if a match somehow lists a name twice.
            resolved[full] = max(value, resolved.get(full, 0))
        if not resolved:
            continue
        gf, ga = (int(x) for x in m["score"].split("-", 1))
        lineup = m.get("lineup") or {}
        out.append({
            "date": m["date"],
            "competition": m["competition"],
            "opponent": m["opponent"],
            "home": m.get("home"),
            "score": m["score"],
            "result": m["result"],
            "gf": gf,
            "ga": ga,
            "pts": {"W": 3, "D": 1, "L": 0}[m["result"]],
            "ratings": resolved,
            "team_avg": st.mean(resolved.values()),
            "team_stats": m.get("team_stats") or {},
            "formation": m.get("formation"),
            "lineup": {last_index.get(deaccent(k.split()[-1]), k): v
                       for k, v in lineup.items()},
        })
    out.sort(key=lambda m: m["date"])
    return out, sorted(unresolved), log


def minutes_for(match, player):
    """Minutes played, or None when the match carries no lineup data. Never
    guessed: a match without `lineup` returns None for everyone, and the
    caller falls back to counting appearances."""
    entry = (match.get("lineup") or {}).get(player)
    if not entry:
        return None
    start = entry.get("start", 0) or 0
    off = entry.get("off")
    end = 90 if off is None else off
    return max(0, end - start)


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------

def split(matches):
    comp = [m for m in matches if m["competition"] in COMPETITIVE]
    return {
        "all": matches,
        "competitive": comp,
        "league": [m for m in comp if m["competition"] == LEAGUE],
        "warmup": [m for m in matches if m["competition"] not in COMPETITIVE],
    }


def player_table(pool, people):
    """Per-player aggregates over one pool of matches.

    An appearance is anyone who shows up in EITHER `lineup` or
    `player_ratings`. The two can disagree: a post-match ratings screenshot
    sometimes misses a late substitute who is plainly in the recap, and a
    player can be in the lineup with no rating captured at all. Counting only
    rated players would silently undercount those appearances -- and would
    have done so invisibly, since the row just wouldn't exist.

    `apps` therefore counts appearances, while `rated_apps` counts the subset
    with a rating. Rating averages use the latter; a player with minutes but
    no ratings at all gets no rating figures rather than a fabricated one."""
    rows = {}
    for m in pool:
        played = set(m["ratings"]) | set(m.get("lineup") or {})
        for name in played:
            r = rows.setdefault(name, {
                "apps": 0, "rated_apps": 0, "minutes": 0, "minutes_known": 0,
                "ratings": [], "rel": [], "w": 0, "d": 0, "l": 0, "gd": 0,
            })
            r["apps"] += 1
            r[{"W": "w", "D": "d", "L": "l"}[m["result"]]] += 1
            r["gd"] += m["gf"] - m["ga"]
            rating = m["ratings"].get(name)
            if rating is not None:
                r["rated_apps"] += 1
                r["ratings"].append(rating)
                r["rel"].append(rating - m["team_avg"])
            mins = minutes_for(m, name)
            if mins is not None:
                r["minutes"] += mins
                r["minutes_known"] += 1
    for name, r in rows.items():
        r["name"] = name
        r["avg"] = st.mean(r["ratings"]) if r["ratings"] else None
        r["rel_avg"] = st.mean(r["rel"]) if r["rel"] else None
        r["ppm"] = (r["w"] * 3 + r["d"]) / r["apps"]
        r["meta"] = people.get(name, {})
    return rows


def with_without(pool, rows):
    """Team points/goal difference per game with and without each player.

    Heavily confounded -- a player who signed mid-season has an entire
    pre-signing 'without' sample, and a squad player's 'with' games are the
    easy ones. Reported because it is cheap and occasionally striking, never
    as a standalone verdict."""
    out = {}
    total = len(pool)
    for name, r in rows.items():
        played = [m for m in pool
                  if name in m["ratings"] or name in (m.get("lineup") or {})]
        missed = [m for m in pool if m not in played]
        if len(played) < MIN_APPS or not missed:
            continue
        out[name] = {
            "ppm_with": st.mean([m["pts"] for m in played]),
            "ppm_without": st.mean([m["pts"] for m in missed]),
            "gd_with": st.mean([m["gf"] - m["ga"] for m in played]),
            "gd_without": st.mean([m["gf"] - m["ga"] for m in missed]),
            "n_with": len(played),
            "n_without": len(missed),
            "coverage": len(played) / total,
        }
    return out


def pair_interaction(pool, rows):
    """Does a pairing beat the sum of its two parts?

    `joint` is the mean combined rel of both players when they appear
    together; `interaction` subtracts each player's own baseline rel, so a
    positive number means they were better *together* than they each are in
    general. This is the only defensible way to ask the 'who combines well'
    question without lineup data, and it is still weak: it cannot see who
    played near whom, and at MIN_PAIR co-appearances the noise is large."""
    base = {n: r["rel_avg"] for n, r in rows.items()
            if r["rel_avg"] is not None and r["rated_apps"] >= MIN_APPS}
    out = []
    for a, b in itertools.combinations(sorted(base), 2):
        together = [m for m in pool if a in m["ratings"] and b in m["ratings"]]
        if len(together) < MIN_PAIR:
            continue
        joint = st.mean([
            (m["ratings"][a] - m["team_avg"]) + (m["ratings"][b] - m["team_avg"])
            for m in together
        ])
        shared = [minutes_for(m, a) for m in together]
        out.append({
            "a": a, "b": b, "n": len(together),
            "joint": joint,
            "interaction": joint - (base[a] + base[b]),
            "gd": st.mean([m["gf"] - m["ga"] for m in together]),
            "ppm": st.mean([m["pts"] for m in together]),
            "minutes_known": all(x is not None for x in shared),
        })
    out.sort(key=lambda p: p["interaction"], reverse=True)
    return out


def keeper_table(pool, people):
    """Goals conceded and clean sheets per keeper. Only counts matches the
    keeper actually appears in, so a shared match (injury, sending off) is
    credited to both -- rare enough to flag in prose rather than model."""
    out = {}
    for name, meta in people.items():
        if not meta["senior"] or "GK" not in meta["pos"].split("/"):
            continue
        played = [m for m in pool if name in m["ratings"]]
        if not played:
            continue
        out[name] = {
            "apps": len(played),
            "conceded": sum(m["ga"] for m in played),
            "per_game": sum(m["ga"] for m in played) / len(played),
            "clean_sheets": sum(1 for m in played if m["ga"] == 0),
            "avg": st.mean([m["ratings"][name] for m in played]),
            "rel": st.mean([m["ratings"][name] - m["team_avg"] for m in played]),
        }
    return out


def team_shape(pool):
    """Team-level totals. Shot figures come only from matches where the Team
    Stats screen was captured, so the denominator is stated alongside them."""
    sf = sa = sot_f = sot_a = 0
    shots_n = sot_n = 0
    poss, passing, tackles = [], [], []
    for m in pool:
        ts = m["team_stats"]
        if ts.get("shots"):
            a, b = ts["shots"].split("-", 1)
            sf += int(a); sa += int(b); shots_n += 1
        if ts.get("shots_on_target"):
            a, b = ts["shots_on_target"].split("-", 1)
            sot_f += int(a); sot_a += int(b); sot_n += 1
        for key, bucket in (("possession", poss), ("pass_accuracy", passing),
                            ("tackles", tackles)):
            if ts.get(key) is not None:
                bucket.append(ts[key])
    n = len(pool) or 1
    gf = sum(m["gf"] for m in pool)
    ga = sum(m["ga"] for m in pool)
    return {
        "played": len(pool),
        "w": sum(1 for m in pool if m["result"] == "W"),
        "d": sum(1 for m in pool if m["result"] == "D"),
        "l": sum(1 for m in pool if m["result"] == "L"),
        "gf": gf, "ga": ga, "gf_pg": gf / n, "ga_pg": ga / n,
        "shots_for": sf, "shots_against": sa, "shots_matches": shots_n,
        "sot_for": sot_f, "sot_against": sot_a, "sot_matches": sot_n,
        "conversion": (gf / sf * 100) if sf else None,
        "possession": st.mean(poss) if poss else None,
        "pass_accuracy": st.mean(passing) if passing else None,
        "tackles": st.mean(tackles) if tackles else None,
        "stats_coverage": shots_n / n,
    }


# ---------------------------------------------------------------------------
# Depth ladder
# ---------------------------------------------------------------------------

def tier_of(meta):
    """Best evidence for a player's ceiling, and where it came from.

    FC26 stops showing a potential range once a player is fully scouted, so a
    blank Potential on an established senior is expected, not missing data --
    the report says 'closed' rather than pretending to a tier."""
    status = (meta.get("status") or "").lower()
    for phrase, tier in TIER_WORDS:
        if phrase in status:
            return tier, "status"
    pot = meta.get("potential") or ""
    if "-" in pot:
        try:
            ceiling = int(pot.split("-")[1])
        except ValueError:
            return None, "unparsed"
        for threshold, tier in TIERS:
            if ceiling >= threshold:
                return tier, "potential"
        return "sub-SGP", "potential"
    return None, "closed"


def on_loan(meta):
    return "on loan at" in (meta.get("status") or "").lower()


def slots_for(meta):
    out = []
    for p in (meta.get("pos") or "").split("/"):
        p = SLOT_ALIASES.get(p.strip(), p.strip())
        if p in SLOTS and p not in out:
            out.append(p)
    return out


def depth_ladder(people, rows_comp):
    """Every player grouped by the slot(s) he covers, ranked by current OVR,
    annotated with tier, availability and competitive-match form."""
    ladder = {s: [] for s in SLOTS}
    for name, meta in people.items():
        tier, source = tier_of(meta)
        form = rows_comp.get(name)
        entry = {
            "name": name, "age": meta["age"], "ovr": meta["ovr"],
            "pos": meta["pos"], "senior": meta["senior"], "role": meta["role"],
            "tier": tier, "tier_source": source, "potential": meta["potential"],
            "loan": on_loan(meta),
            "apps": form["apps"] if form else 0,
            "rel": form["rel_avg"] if form else None,
        }
        for slot in slots_for(meta):
            ladder[slot].append(entry)
    for slot in ladder:
        ladder[slot].sort(key=lambda e: (-e["ovr"], e["age"]))
    return ladder


RANK = {"HPTBS": 3, "EP": 2, "SGP": 1}
# The stated standard's own bands: EP is 85-90, SGP is 80-84.
EP_FLOOR, SGP_FLOOR = 85, 80


def standard_check(ladder):
    """Score each slot against the stated standard on BOTH axes, separately.

    The standard ("an EP-level player at every position, an SGP-level clear
    backup") collapses two different questions, and conflating them produces
    nonsense in either direction:

      NOW      -- who can actually play the position this weekend, measured
                  on current OVR against the standard's own 85/80 bands.
      CEILING  -- who is projected to get there, measured on the scouting
                  tier (or, for a fully-scouted senior whose range the game
                  has closed, on his current OVR, since that IS his ceiling).

    Judging on ceiling alone says a 64-OVR eighteen-year-old with an exciting-
    prospect tag satisfies the position. Judging on current OVR alone writes
    off every prospect in the building. Both numbers are reported; neither is
    blended into a single score.

    'Available' excludes players out on loan. A 92-potential winger at another
    club is a plan, not cover, and counting him is how a depth chart flatters
    itself."""
    verdicts = {}
    for slot, players in ladder.items():
        available = [p for p in players if p["senior"] and not p["loan"]]

        now_ep = [p for p in available if p["ovr"] >= EP_FLOOR]
        now_sgp = [p for p in available if p["ovr"] >= SGP_FLOOR]
        # Ceiling: an explicit tier, or a closed range where current OVR is it.
        ceil_ep = [p for p in available
                   if RANK.get(p["tier"], 0) >= 2
                   or (p["tier"] is None and p["ovr"] >= EP_FLOOR)]
        ceil_sgp = [p for p in available
                    if RANK.get(p["tier"], 0) >= 1
                    or (p["tier"] is None and p["ovr"] >= SGP_FLOOR)]

        verdicts[slot] = {
            "available": len(available),
            "best_ovr": max((p["ovr"] for p in available), default=None),
            "now_ep": [p["name"] for p in now_ep],
            "now_sgp_count": len(now_sgp),
            "ceiling_ep": [p["name"] for p in ceil_ep],
            "ceiling_sgp_count": len(ceil_sgp),
            "meets_now_starter": bool(now_ep),
            "meets_now_backup": len(now_sgp) >= 2,
            "meets_ceiling_starter": bool(ceil_ep),
            "meets_ceiling_backup": len(ceil_sgp) >= 2,
            "pipeline": sorted(
                (p["name"], p["tier"], p["potential"], p["age"])
                for p in players if (not p["senior"] or p["loan"])
                and RANK.get(p["tier"], 0) >= 1
            ),
        }
    return verdicts


def usage_flags(rows, pool):
    """Players whose share of available matches is out of line with how they
    have performed. Not a verdict -- a shortlist of things to go and look at."""
    n = len(pool) or 1
    eligible = [r for r in rows.values()
                if r["rel_avg"] is not None and r["rated_apps"] >= MIN_APPS]
    if not eligible:
        return {"underused": [], "overused": []}
    under, over = [], []
    for r in eligible:
        share = r["apps"] / n
        if r["rel_avg"] >= 0.15 and share <= 0.6:
            under.append(r)
        elif r["rel_avg"] <= -0.15 and share >= 0.6:
            over.append(r)
    under.sort(key=lambda r: -r["rel_avg"])
    over.sort(key=lambda r: r["rel_avg"])
    return {"underused": under, "overused": over}


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def rule(title):
    return f"\n{title}\n{'=' * len(title)}"


def fmt_player_rows(rows, pool, limit=None):
    n = len(pool) or 1
    ordered = sorted(
        [r for r in rows.values()
         if r["rel_avg"] is not None and r["rated_apps"] >= MIN_APPS],
        key=lambda r: -r["rel_avg"],
    )
    if limit:
        ordered = ordered[:limit]
    minutes_seen = any(r["minutes_known"] for r in ordered)
    head = "%-24s%-16s%4s%4s%5s%7s%8s%7s" % (
        "Player", "Pos", "Age", "OVR", "App", "AvgR", "vsTeam", "Share")
    if minutes_seen:
        head += "%8s" % "Mins"
    lines = [head, "-" * len(head)]
    for r in ordered:
        meta = r["meta"]
        line = "%-24s%-16s%4s%4s%5d%7.2f%+8.2f%6.0f%%" % (
            r["name"], meta.get("pos", "?"), meta.get("age", "?"),
            meta.get("ovr", "?"), r["apps"], r["avg"], r["rel_avg"],
            100 * r["apps"] / n)
        if minutes_seen:
            line += "%8s" % (r["minutes"] if r["minutes_known"] else "--")
        lines.append(line)
    return "\n".join(lines)


def report(data, sections):
    people = data["people"]
    pools = data["pools"]
    comp = pools["competitive"]
    rows_comp = data["rows"]["competitive"]
    out = []

    if "team" in sections:
        out.append(rule("TEAM SHAPE"))
        for label, pool in (("Competitive", comp), ("League", pools["league"])):
            t = team_shape(pool)
            if not t["played"]:
                continue
            out.append(
                f"{label}: P{t['played']} W{t['w']} D{t['d']} L{t['l']} | "
                f"GF {t['gf']} ({t['gf_pg']:.2f}/g)  GA {t['ga']} ({t['ga_pg']:.2f}/g)")
            if t["shots_matches"]:
                out.append(
                    f"  Shots {t['shots_for']}-{t['shots_against']} over "
                    f"{t['shots_matches']} match(es) = "
                    f"{t['shots_for']/t['shots_matches']:.1f}-"
                    f"{t['shots_against']/t['shots_matches']:.1f}/g"
                    + (f" | conversion {t['conversion']:.1f}%" if t["conversion"] else ""))
            if t["sot_matches"]:
                out.append(
                    f"  On target {t['sot_for']}-{t['sot_against']} over "
                    f"{t['sot_matches']} match(es)")
            bits = []
            for key, label2, suffix in (("possession", "possession", "%"),
                                        ("pass_accuracy", "pass acc", "%"),
                                        ("tackles", "tackles", "")):
                if t[key] is not None:
                    bits.append(f"{label2} {t[key]:.1f}{suffix}")
            if bits:
                out.append("  " + " | ".join(bits))
            if t["stats_coverage"] < 1:
                out.append(f"  (team_stats captured for {t['stats_coverage']:.0%} of matches)")

    if "usage" in sections:
        out.append(rule("USAGE VS PERFORMANCE"))
        flags = usage_flags(rows_comp, comp)
        for label, group in (("Playing less than they have earned", flags["underused"]),
                             ("Playing more than they have earned", flags["overused"])):
            out.append(f"\n{label}:")
            if not group:
                out.append("  (none)")
            for r in group:
                out.append(
                    "  %-24s %-16s rel %+0.2f over %d apps (%.0f%% of matches), role: %s"
                    % (r["name"], r["meta"].get("pos", "?"), r["rel_avg"], r["apps"],
                       100 * r["apps"] / len(comp), r["meta"].get("role", "?")))

    if "players" in sections:
        for label, key in (("COMPETITIVE MATCHES", "competitive"),
                           ("LEAGUE ONLY", "league")):
            pool = pools[key]
            if not pool:
                continue
            out.append(rule(f"PLAYER RATINGS -- {label} (n={len(pool)})"))
            out.append(fmt_player_rows(data["rows"][key], pool))

    if "keepers" in sections:
        out.append(rule("GOALKEEPERS (competitive)"))
        ks = keeper_table(comp, people)
        if not ks:
            out.append("  (no keeper appearances recorded)")
        for name, k in sorted(ks.items(), key=lambda kv: kv[1]["per_game"]):
            out.append(
                "  %-24s %2d apps | %2d conceded (%.2f/g) | %d CS | avg %.2f | rel %+0.2f"
                % (name, k["apps"], k["conceded"], k["per_game"],
                   k["clean_sheets"], k["avg"], k["rel"]))

    if "pairs" in sections:
        pairs = pair_interaction(comp, rows_comp)
        out.append(rule(f"PAIRINGS (competitive, min {MIN_PAIR} together)"))
        if not any(p["minutes_known"] for p in pairs):
            out.append("  NOTE: no lineup/minutes data -- 'together' means both "
                       "appeared in the same match, which cannot distinguish a "
                       "shared 90 minutes from two cameos at opposite ends of it.")
        out.append("\n  Better together than apart:")
        for p in pairs[:8]:
            out.append("    %-22s + %-22s n=%2d  interaction %+0.2f  joint %+0.2f  GD %+0.2f"
                       % (p["a"], p["b"], p["n"], p["interaction"], p["joint"], p["gd"]))
        out.append("\n  Worse together than apart:")
        for p in pairs[-6:]:
            out.append("    %-22s + %-22s n=%2d  interaction %+0.2f  joint %+0.2f  GD %+0.2f"
                       % (p["a"], p["b"], p["n"], p["interaction"], p["joint"], p["gd"]))

    if "withwithout" in sections:
        out.append(rule("TEAM RESULTS WITH / WITHOUT (confounded -- read the docstring)"))
        ww = with_without(comp, rows_comp)
        for name, w in sorted(ww.items(), key=lambda kv: kv[1]["ppm_with"] - kv[1]["ppm_without"],
                              reverse=True):
            out.append(
                "  %-24s PPM %.2f (n=%2d) vs %.2f (n=%2d)  |  GD %+0.2f vs %+0.2f"
                % (name, w["ppm_with"], w["n_with"], w["ppm_without"],
                   w["n_without"], w["gd_with"], w["gd_without"]))

    if "depth" in sections:
        ladder = data["ladder"]
        verdicts = data["standard"]
        out.append(rule("DEPTH LADDER VS STANDARD (EP 85-90 starter / SGP 80-84 backup)"))
        out.append(
            "  NOW = current OVR. CEILING = scouting tier, or current OVR where the\n"
            "  game has closed a senior's potential range. Reported separately on\n"
            "  purpose -- see standard_check()'s docstring.\n"
            "  Slots come from each player's LISTED positions in the CSV, not from\n"
            "  where he is actually picked. Until matches carry a `lineup` field a\n"
            "  utility player shows up under every slot he lists, which can put the\n"
            "  wrong name at the top of a ladder.\n"
            "  Players out on loan appear only under Pipeline, never as cover.\n")
        for slot in SLOTS:
            v = verdicts[slot]

            def mark(starter, backup):
                return "OK  " if starter and backup else ("WARN" if starter or backup else "FAIL")

            out.append(
                "  %-4s  NOW [%s] starter:%-3s backup:%-3s (%d at 80+)   "
                "CEILING [%s] starter:%-3s backup:%-3s (%d at SGP+)   best OVR %s"
                % (slot,
                   mark(v["meets_now_starter"], v["meets_now_backup"]),
                   "yes" if v["meets_now_starter"] else "no",
                   "yes" if v["meets_now_backup"] else "no",
                   v["now_sgp_count"],
                   mark(v["meets_ceiling_starter"], v["meets_ceiling_backup"]),
                   "yes" if v["meets_ceiling_starter"] else "no",
                   "yes" if v["meets_ceiling_backup"] else "no",
                   v["ceiling_sgp_count"],
                   v["best_ovr"] if v["best_ovr"] is not None else "-"))
            for p in ladder[slot]:
                if not p["senior"] or p["loan"]:
                    continue
                tier = p["tier"] or ("closed" if p["tier_source"] == "closed" else "?")
                rel = "%+0.2f" % p["rel"] if p["rel"] is not None else "  -  "
                out.append("        %-24s %-16s age %-3d OVR %-4d %-7s %2d apps  rel %s"
                           % (p["name"], p["pos"], p["age"], p["ovr"], tier, p["apps"], rel))
            pipeline = [p for p in ladder[slot] if (not p["senior"] or p["loan"])
                        and p["tier"] in ("HPTBS", "EP", "SGP")]
            for p in pipeline:
                where = "loan" if p["loan"] else "academy"
                out.append("        . %-22s %-16s age %-3d POT %-8s %-7s (%s)"
                           % (p["name"], p["pos"], p["age"], p["potential"] or "-",
                              p["tier"], where))
            out.append("")

    if data["unresolved"]:
        out.append(rule("UNRESOLVED NAMES"))
        out.append("  These player_ratings keys matched no CSV row and were skipped:")
        for key in data["unresolved"]:
            out.append(f"    {key}")

    return "\n".join(out)


def build(argv=None):
    people, last_index = load_roster()
    matches, unresolved, log = load_matches(people, last_index)
    pools = split(matches)
    rows = {k: player_table(v, people) for k, v in pools.items()}
    ladder = depth_ladder(people, rows["competitive"])
    return {
        "season": log.get("_meta", {}).get("season"),
        "people": people,
        "pools": pools,
        "rows": rows,
        "ladder": ladder,
        "standard": standard_check(ladder),
        "unresolved": unresolved,
        "has_lineups": any(m["lineup"] for m in matches),
    }


ALL_SECTIONS = ["team", "usage", "players", "keepers", "pairs", "withwithout", "depth"]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--section", action="append", choices=ALL_SECTIONS,
                    help="limit to one or more sections (repeatable)")
    args = ap.parse_args()

    data = build()
    if args.json:
        payload = {
            "season": data["season"],
            "has_lineups": data["has_lineups"],
            "team": {k: team_shape(v) for k, v in data["pools"].items() if v},
            "players": {
                pool: {
                    n: {kk: vv for kk, vv in r.items()
                        if kk not in ("ratings", "rel", "meta")}
                    for n, r in rs.items()
                }
                for pool, rs in data["rows"].items()
            },
            "pairs": pair_interaction(data["pools"]["competitive"],
                                      data["rows"]["competitive"]),
            "standard": data["standard"],
            "unresolved": data["unresolved"],
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return

    header = f"WREXHAM AFC -- SQUAD ANALYSIS  ({data['season'] or 'season unknown'})"
    print(header)
    print("=" * len(header))
    print("Appearance basis: %s" % (
        "lineup minutes where recorded, appearances elsewhere"
        if data["has_lineups"] else
        "APPEARANCES ONLY -- no match carries a `lineup` field, so a 90-minute\n"
        "  starter and a late substitute count the same. Add `lineup` to match\n"
        "  entries (see CLAUDE.md, Season Log Schema) to upgrade every figure here."))
    print(report(data, args.section or ALL_SECTIONS))


if __name__ == "__main__":
    # The full report runs to a couple of hundred lines, so piping it into
    # `head`/`less` is the normal way to read it. Without this, closing the
    # pager raises BrokenPipeError and prints a traceback over the output.
    try:
        main()
    except BrokenPipeError:
        try:
            sys.stdout.close()
        finally:
            os._exit(0)
