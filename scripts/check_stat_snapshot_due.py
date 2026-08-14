#!/usr/bin/env python3
"""Reports whether a monthly base-stat or transfer-window/season full-stat
snapshot is due, by comparing season_log.json's latest known in-game date
against player_stat_history.json's last recorded snapshot dates.

Run at the start of any session (no arguments). Prints one line per prompt
that is due, or "Nothing due." if neither is.
"""
import datetime
import json

SEASON_LOG = 'season_log.json'
HISTORY_FILE = 'player_stat_history.json'


def parse(d):
    return datetime.date.fromisoformat(d)


def latest_ingame_date(season_log):
    dates = [season_log['_meta']['last_updated']]
    dates += [m['date'] for m in season_log['matches']]
    return parse(max(dates))


def most_recent_jan31(today):
    candidate = datetime.date(today.year, 1, 31)
    if candidate <= today:
        return candidate
    return datetime.date(today.year - 1, 1, 31)


def main():
    with open(SEASON_LOG, encoding='utf-8') as f:
        season_log = json.load(f)
    with open(HISTORY_FILE, encoding='utf-8') as f:
        history = json.load(f)

    today = latest_ingame_date(season_log)
    last_base = history['_meta']['last_base_snapshot']
    last_full = history['_meta']['last_full_snapshot']

    due = []

    last_base_date = parse(last_base) if last_base else None
    if last_base_date is None or (last_base_date.year, last_base_date.month) != (today.year, today.month):
        due.append(
            f'BASE snapshot due: in-game date is {today.isoformat()}, last base snapshot was '
            f'{last_base or "never"}. Prompt the user to screenshot every current player\'s base '
            f'card (OVR + Summary stats), update the CSVs if anything changed, then run: '
            f'python3 scripts/record_stat_snapshot.py base {today.isoformat()}'
        )

    boundary = most_recent_jan31(today)
    last_full_date = parse(last_full) if last_full else None
    if last_full_date is None or last_full_date < boundary:
        due.append(
            f'FULL snapshot due: transfer window closed / season boundary at {boundary.isoformat()} '
            f'has passed with no full snapshot since. Prompt the user for a full round of Attributes '
            f'tab screenshots, update the CSVs, then run: '
            f'python3 scripts/record_stat_snapshot.py full {today.isoformat()}'
        )

    if due:
        for line in due:
            print(line)
    else:
        print('Nothing due.')


if __name__ == '__main__':
    main()
