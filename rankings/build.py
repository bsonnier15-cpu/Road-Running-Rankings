"""Build the static site: one self-contained index.html with the rankings embedded.

    python -m rankings.build                       # uses data/rankings.db
    python -m rankings.build --db data/sample.db   # preview with sample data
"""
import argparse
import json
from collections import defaultdict
from datetime import date
from pathlib import Path

from .config import (DISTANCES, SITE_DIR, SITE_NAME, SITE_TAGLINE,
                     STATE_PAGE_NAME, US_STATES)
from .db import connect
from .ingest import purge_excluded, refresh_finisher_counts
from .rank import compute

HERE = Path(__file__).parent
TEMPLATE = HERE / "template.html"


def runner_name(p):
    return f"{p['first_name']} {p['last_name']}"


def payload(conn, as_of=None):
    perfs, tops, power = compute(conn, as_of)
    state_rows = dict(conn.execute("SELECT key, value FROM sync_state").fetchall())

    top_out, power_out = {}, {}
    for (st, dist, g), entries in tops.items():
        top_out.setdefault(st, {}).setdefault(dist, {})[g] = [
            [runner_name(p), p["city"] or "", round(p["seconds"], 1), p["race_name"], p["event_date"], p["race_id"]]
            for p in entries
        ]
    for (st, g), runners in power.items():
        power_out.setdefault(st, {})[g] = [
            [runner_name(r), r["city"] or "", round(r["score"], 1), r["races"],
             [[p["distance_key"], round(p["seconds"], 1), p["race_name"], p["event_date"], round(p["points"], 1), p["race_id"]]
              for p in r["counting"]]]
            for r in runners
        ]

    # Per-state totals for the page header: runners with a result, and races they ran.
    runners, races = defaultdict(set), defaultdict(set)
    for p in perfs:
        runners[p["state"]].add(p["runner_id"])
        races[p["state"]].add(p["race_id"])
    stats = {st: {"runners": len(runners[st]), "races": len(races[st])} for st in runners}

    return {
        "meta": {
            "site": SITE_NAME, "tagline": SITE_TAGLINE, "statePage": STATE_PAGE_NAME,
            "lastSync": state_rows.get("last_sync"), "built": (as_of or date.today()).isoformat(),
            "sample": state_rows.get("sample") == "1",
        },
        "states": US_STATES,
        "distances": {k: v[0] for k, v in DISTANCES.items()},
        "stats": stats,
        "top": top_out,
        "power": power_out,
    }


def build(db_path=None, out_dir=None, as_of=None):
    out_dir = Path(out_dir or SITE_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    with connect(Path(db_path) if db_path else None) as conn:
        purge_excluded(conn)          # clean out anything synced before a filter existed
        refresh_finisher_counts(conn)
        data = payload(conn, as_of)
    blob = json.dumps(data, separators=(",", ":")).replace("</", "<\\/")
    flags = (HERE / "flags.js").read_text()
    page = (TEMPLATE.read_text().replace("__SITE_NAME__", SITE_NAME)
            .replace("/*__FLAGS__*/", flags).replace("/*__DATA__*/null", blob))
    (out_dir / "index.html").write_text(page)
    (out_dir / ".nojekyll").write_text("")
    return out_dir / "index.html"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db")
    ap.add_argument("--out")
    args = ap.parse_args()
    print(f"built {build(args.db, args.out)}")


if __name__ == "__main__":
    main()
