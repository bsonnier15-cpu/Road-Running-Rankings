"""SQLite storage. One file, no server — commits cleanly into the repo for GitHub Pages."""
import sqlite3
from contextlib import contextmanager

from .config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS races (
    race_id     INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    city        TEXT,
    state       TEXT,
    synced_at   TEXT
);

CREATE TABLE IF NOT EXISTS events (
    event_id      INTEGER PRIMARY KEY,
    race_id       INTEGER NOT NULL REFERENCES races(race_id),
    name          TEXT,
    distance_key  TEXT NOT NULL,       -- 5k | 10k | 15k | half | full
    event_date    TEXT NOT NULL,       -- YYYY-MM-DD
    finishers     INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS runners (
    runner_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    match_key   TEXT UNIQUE NOT NULL,  -- normalized name|gender|state|birth-year bucket
    first_name  TEXT NOT NULL,
    last_name   TEXT NOT NULL,
    gender      TEXT NOT NULL,         -- M | F
    state       TEXT NOT NULL,
    birth_year  INTEGER,
    city        TEXT
);

CREATE TABLE IF NOT EXISTS results (
    result_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id      INTEGER NOT NULL REFERENCES events(event_id),
    runner_id     INTEGER NOT NULL REFERENCES runners(runner_id),
    source_id     TEXT,                -- RunSignup result_id, for idempotent re-syncs
    seconds       REAL NOT NULL,       -- chip time preferred, clock time fallback
    overall_place INTEGER,
    age           INTEGER,
    UNIQUE (event_id, source_id)
);

CREATE INDEX IF NOT EXISTS idx_results_runner ON results(runner_id);
CREATE INDEX IF NOT EXISTS idx_events_dist_date ON events(distance_key, event_date);
CREATE INDEX IF NOT EXISTS idx_runners_state ON runners(state, gender);

CREATE TABLE IF NOT EXISTS sync_state (
    key   TEXT PRIMARY KEY,
    value TEXT
);
"""


@contextmanager
def connect(path=None):
    path = path or DB_PATH
    if str(path) != ":memory:":
        path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()
