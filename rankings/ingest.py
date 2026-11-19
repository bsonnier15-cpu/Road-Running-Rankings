"""Turn raw race results into races/events/runners/results rows."""
from datetime import date

from .normalize import (clean_name, distance_key, gender_code, match_key,
                        parse_seconds, plausible, state_code)


def upsert_race(conn, race_id, name, city, state, synced_at=None):
    conn.execute(
        """INSERT INTO races (race_id, name, city, state, synced_at) VALUES (?,?,?,?,?)
           ON CONFLICT(race_id) DO UPDATE SET name=excluded.name, city=excluded.city,
           state=excluded.state, synced_at=excluded.synced_at""",
        (race_id, name, city, state, synced_at),
    )


def upsert_event(conn, event_id, race_id, name, dist_key, event_date):
    conn.execute(
        """INSERT INTO events (event_id, race_id, name, distance_key, event_date) VALUES (?,?,?,?,?)
           ON CONFLICT(event_id) DO UPDATE SET name=excluded.name,
           distance_key=excluded.distance_key, event_date=excluded.event_date""",
        (event_id, race_id, name, dist_key, event_date),
    )


def find_or_create_runner(conn, first, last, gender, state, age, event_date, city=None):
    """Match a result to a known runner. A race-day age implies one of two birth
    years, so both buckets are tried before creating a new runner."""
    year = int(str(event_date)[:4])
    candidates = [year - age, year - age - 1] if age else [None]
    for by in candidates:
        row = conn.execute(
            "SELECT runner_id FROM runners WHERE match_key = ?",
            (match_key(first, last, gender, state, by),),
        ).fetchone()
        if row:
            return row["runner_id"]
    birth_year = candidates[0]
    cur = conn.execute(
        """INSERT INTO runners (match_key, first_name, last_name, gender, state, birth_year, city)
           VALUES (?,?,?,?,?,?,?)""",
        (match_key(first, last, gender, state, birth_year),
         clean_name(first).title(), clean_name(last).title(), gender, state, birth_year, city),
    )
    return cur.lastrowid


def add_result(conn, event_id, dist_key, event_date, row, fallback_state=None):
    """row: a RunSignup-shaped result dict. Returns True if stored."""
    first, last = row.get("first_name"), row.get("last_name")
    gender = gender_code(row.get("gender"))
    state = state_code(row.get("state")) or fallback_state
    seconds = parse_seconds(row.get("chip_time")) or parse_seconds(row.get("clock_time"))
    if not (first and last and gender and state and plausible(dist_key, seconds)):
        return False
    try:
        age = int(row.get("age")) if row.get("age") not in (None, "") else None
    except ValueError:
        age = None
    runner_id = find_or_create_runner(conn, first, last, gender, state, age, event_date, row.get("city"))
    rid = row.get("result_id")
    source_id = str(rid) if rid not in (None, "") else f"runner-{runner_id}"
    conn.execute(
        """INSERT INTO results (event_id, runner_id, source_id, seconds, overall_place, age)
           VALUES (?,?,?,?,?,?)
           ON CONFLICT(event_id, source_id) DO UPDATE SET seconds=excluded.seconds,
           overall_place=excluded.overall_place""",
        (event_id, runner_id, source_id, seconds, row.get("place"), age),
    )
    return True


def purge_excluded(conn):
    """Remove events (and their results) that the current filters reject, e.g. virtual
    races synced before the filter caught them. Safe to run on every sync and build."""
    from .normalize import excluded
    bad = [r["event_id"] for r in conn.execute("SELECT event_id, name FROM events") if excluded(r["name"])]
    for eid in bad:
        conn.execute("DELETE FROM results WHERE event_id = ?", (eid,))
        conn.execute("DELETE FROM events WHERE event_id = ?", (eid,))
    conn.execute("DELETE FROM runners WHERE runner_id NOT IN (SELECT runner_id FROM results)")
    return len(bad)


def refresh_finisher_counts(conn):
    conn.execute(
        """UPDATE events SET finishers =
           (SELECT COUNT(*) FROM results r WHERE r.event_id = events.event_id)"""
    )


def parse_event_date(raw):
    """RunSignup gives 'MM/DD/YYYY HH:MM' style start times."""
    if not raw:
        return None
    raw = str(raw).strip().split(" ")[0]
    if "/" in raw:
        m, d, y = raw.split("/")
        return date(int(y), int(m), int(d)).isoformat()
    return raw[:10]


def event_distance(event):
    return distance_key(event.get("distance"), event.get("name"))
