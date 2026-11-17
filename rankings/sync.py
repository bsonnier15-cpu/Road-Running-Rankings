"""Nightly sync: pull recent race results for every state from RunSignup.

Usage:
    python -m rankings.sync                 # all states, last 14 days (nightly)
    python -m rankings.sync --days 365      # backfill a full year
    python -m rankings.sync --states TX LA  # subset
"""
import argparse
from datetime import date, datetime, timedelta, timezone

from .config import US_STATES
from .db import connect
from .ingest import (add_result, event_distance, parse_event_date,
                     refresh_finisher_counts, upsert_event, upsert_race)
from .runsignup import RunSignup


def sync(states, days, client=None):
    client = client or RunSignup()
    end = date.today()
    start = end - timedelta(days=days)
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    totals = {"races": 0, "events": 0, "results": 0}

    with connect() as conn:
        for st in states:
            for race in client.races(st, start.isoformat(), end.isoformat()):
                race_id = int(race["race_id"])
                addr = race.get("address") or {}
                race_state = addr.get("state") or st
                upsert_race(conn, race_id, race.get("name", ""), addr.get("city"), race_state, now)
                totals["races"] += 1
                for ev in race.get("events", []):
                    dist = event_distance(ev)
                    ev_date = parse_event_date(ev.get("start_time"))
                    if not dist or not ev_date or not (start.isoformat() <= ev_date <= end.isoformat()):
                        continue
                    event_id = int(ev["event_id"])
                    upsert_event(conn, event_id, race_id, ev.get("name"), dist, ev_date)
                    totals["events"] += 1
                    for row in client.results(race_id, event_id):
                        if add_result(conn, event_id, dist, ev_date, row, fallback_state=None):
                            totals["results"] += 1
                conn.commit()
            print(f"[{st}] cumulative: {totals}", flush=True)
        refresh_finisher_counts(conn)
        conn.execute("INSERT OR REPLACE INTO sync_state VALUES ('last_sync', ?)", (now,))
    return totals


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=14)
    ap.add_argument("--states", nargs="*", default=sorted(US_STATES))
    args = ap.parse_args()
    print(sync([s.upper() for s in args.states], args.days))


if __name__ == "__main__":
    main()
