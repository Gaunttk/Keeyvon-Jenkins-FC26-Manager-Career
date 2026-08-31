"""
Regenerates the SEASON_SUMMARY block embedded in docs/index.html from season_log.json.

Why this exists: index.html has to work as a local file:// page, so it can't
fetch season_log.json at runtime. Previously the fix was to paste the ENTIRE
season_log.json into index.html as SEASON_DATA and re-sync it by hand every
session -- a full copy of the growing match/transfer/milestone history,
duplicated, that silently went stale if someone forgot to re-run the dump.

Instead, this script precomputes the only two things index.html actually
displays -- the season stat bar (P/W/D/L/Pts for league and cup) and the last
12 events for the log feed -- into a small SEASON_SUMMARY object. index.html
stays a small, constant size forever; season_log.json remains the single
full-history source of truth.

Run this after any edit to season_log.json:
    python3 scripts/sync_season_summary.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEASON_LOG = ROOT / "season_log.json"
INDEX_HTML = ROOT / "docs" / "index.html"

PRESEASON_COMPS = {"Youth Academy Rush Tournament", "European International Cup"}
RECENT_LIMIT = 12

MATCH_FIELDS = ("date", "opponent", "home", "score", "result", "competition")
TRANSFER_FIELDS = ("date", "player", "direction", "club")
INJURY_FIELDS = ("date", "player", "description")
MILESTONE_FIELDS = ("date", "description")


def pick(d, fields):
    return {k: d[k] for k in fields if k in d}


def build_summary(log):
    matches = log.get("matches", [])
    league_name = log.get("_meta", {}).get("competition", "EFL Championship")
    league = [m for m in matches if m.get("competition") == league_name]
    cup = [m for m in matches if m.get("competition") == "Carabao Cup"]
    fa_cup = [m for m in matches if m.get("competition") == "FA Cup"]
    competitive = [m for m in matches if m.get("competition") not in PRESEASON_COMPS]

    def record(ms):
        w = sum(1 for m in ms if m.get("result") == "W")
        d = sum(1 for m in ms if m.get("result") == "D")
        l = sum(1 for m in ms if m.get("result") == "L")
        return w, d, l

    lw, ld, ll = record(league)
    cw, cd, cl = record(cup)
    fw, fd, fl = record(fa_cup)

    stats = {
        "played": len(competitive),
        "league_p": len(league), "league_w": lw, "league_d": ld, "league_l": ll,
        "league_pts": lw * 3 + ld,
        "cup_p": len(cup), "cup_w": cw, "cup_d": cd, "cup_l": cl,
        "fa_cup_p": len(fa_cup), "fa_cup_w": fw, "fa_cup_d": fd, "fa_cup_l": fl,
    }

    all_events = (
        [{"type": "match", **pick(m, MATCH_FIELDS)} for m in matches]
        + [{"type": "transfer", **pick(t, TRANSFER_FIELDS)} for t in log.get("transfers", [])]
        + [{"type": "injury", **pick(i, INJURY_FIELDS)} for i in log.get("injuries", [])]
        + [{"type": "milestone", **pick(ms, MILESTONE_FIELDS)} for ms in log.get("milestones", [])]
    )
    all_events.sort(key=lambda e: e["date"], reverse=True)
    recent = all_events[:RECENT_LIMIT]

    schedule = build_schedule(log, league_name)

    # Last five completed FIRST-TEAM competitive matches, oldest -> newest.
    # Youth/preseason competitions (PRESEASON_COMPS) never count toward form.
    by_date = sorted(competitive, key=lambda m: m["date"])
    form = [pick(m, MATCH_FIELDS) for m in by_date[-5:]]
    latest = form[-1] if form else None

    return {
        "_meta": log.get("_meta", {}),
        "stats": stats,
        "form": form,
        "latest": latest,
        "recent": recent,
        "schedule": schedule,
    }


def build_schedule(log, league_name):
    """Cross-reference the fixed 38-game fixture list with played results.

    Matched by (opponent, home) rather than date -- each opponent is played
    home and away exactly once per season, so this stays correct even if a
    fixture's actual played date drifts from the originally scheduled one.
    """
    fixtures = [fx for fx in log.get("fixtures", []) if fx.get("competition") == league_name]
    league_matches = {
        (m.get("opponent"), m.get("home")): m
        for m in log.get("matches", [])
        if m.get("competition") == league_name
    }

    def fx_home(fx):
        return fx["home"] if "home" in fx else fx.get("venue") == "home"

    schedule = []
    for i, fx in enumerate(fixtures, start=1):
        home = fx_home(fx)
        key = (fx.get("opponent"), home)
        played = league_matches.get(key)
        entry = {
            "md": i,
            "date": fx.get("date"),
            "opponent": fx.get("opponent"),
            "home": home,
        }
        if played:
            entry["score"] = played.get("score")
            entry["result"] = played.get("result")
        schedule.append(entry)
    return schedule


def main():
    log = json.loads(SEASON_LOG.read_text(encoding="utf-8"))
    summary = build_summary(log)
    blob = json.dumps(summary, separators=(",", ":"), ensure_ascii=False)

    html = INDEX_HTML.read_text(encoding="utf-8")
    pattern = re.compile(r"const SEASON_(?:DATA|SUMMARY) = \{.*?\};", re.DOTALL)
    if not pattern.search(html):
        raise SystemExit("Could not find SEASON_DATA/SEASON_SUMMARY block in index.html")
    html = pattern.sub(f"const SEASON_SUMMARY = {blob};", html, count=1)
    INDEX_HTML.write_text(html, encoding="utf-8")
    print(f"Synced SEASON_SUMMARY: {len(blob)} chars ({stats_line(summary)})")


def stats_line(summary):
    s = summary["stats"]
    return f"league P{s['league_p']} W{s['league_w']} D{s['league_d']} L{s['league_l']} Pts{s['league_pts']}"


if __name__ == "__main__":
    main()
