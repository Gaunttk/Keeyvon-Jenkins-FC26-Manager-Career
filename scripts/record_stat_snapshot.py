#!/usr/bin/env python3
"""Appends a point-in-time stat snapshot to player_stat_history.json, read
straight from the current wrexham_squad.csv and youth_academy.csv.

Usage:
    python3 scripts/record_stat_snapshot.py base 2027-01-31
    python3 scripts/record_stat_snapshot.py full 2027-01-31

Run this after the CSVs have been updated from that round of screenshots —
it logs whatever is currently in the CSVs under the given in-game date, it
does not read screenshots itself.

'base' records OVR + the six Summary-tab stats (Pace/Shooting/Passing/
Dribbling/Defending/Physical) for every player in both CSVs — the monthly
base-card check-in.

'full' records those same fields plus every detailed attribute column
(Acceleration..Volleys, Skill_Moves, Weak_Foot, Potential) — the winter
transfer-window-close / season-start check-in.
"""
import csv
import json
import sys

BASE_FIELDS = [
    'OVR', 'Pace', 'Shooting', 'Passing', 'Dribbling', 'Defending', 'Physical',
]

FULL_EXTRA_FIELDS = [
    'Acceleration', 'Agility', 'Balance', 'Jumping', 'Sprint_Speed', 'Stamina',
    'Strength', 'Aggression', 'Att_Position', 'Composure', 'Interceptions',
    'Reactions', 'Vision', 'Ball_Control', 'Crossing', 'Curve', 'Def_Aware',
    'Dribbling_Tech', 'FK_Acc', 'Finishing', 'Heading_Acc', 'Long_Pass',
    'Long_Shots', 'Penalties', 'Short_Pass', 'Shot_Power', 'Slide_Tackle',
    'Stand_Tackle', 'Volleys', 'Skill_Moves', 'Weak_Foot', 'Potential',
]

CSV_FILES = ['wrexham_squad.csv', 'youth_academy.csv']
HISTORY_FILE = 'player_stat_history.json'


def load_players(fields):
    players = {}
    for path in CSV_FILES:
        with open(path, newline='', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                players[row['Name']] = {field: row[field] for field in fields}
    return players


def main():
    if len(sys.argv) != 3 or sys.argv[1] not in ('base', 'full'):
        sys.exit('Usage: python3 scripts/record_stat_snapshot.py <base|full> <YYYY-MM-DD>')
    snapshot_type, date = sys.argv[1], sys.argv[2]

    fields = BASE_FIELDS if snapshot_type == 'base' else BASE_FIELDS + FULL_EXTRA_FIELDS
    players = load_players(fields)

    with open(HISTORY_FILE, encoding='utf-8') as f:
        history = json.load(f)

    history['snapshots'].append({
        'date': date,
        'type': snapshot_type,
        'players': players,
    })
    history['_meta'][f'last_{snapshot_type}_snapshot'] = date

    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)
        f.write('\n')

    print(f'Recorded {snapshot_type} snapshot for {len(players)} players on {date}.')


if __name__ == '__main__':
    main()
