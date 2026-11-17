"""Build the static site: one self-contained index.html with the rankings embedded.

    python -m rankings.build                       # uses data/rankings.db
    python -m rankings.build --db data/sample.db   # preview with sample data
"""
import argparse
import json
from datetime import date
from pathlib import Path

from .config import DISTANCES, SITE_DIR, SITE_NAME, SITE_TAGLINE, US_STATES
from .db import connect
from .rank import compute

TEMPLATE = Path(__file__).with_name("template.html")


def runner_name(p):
    return f"{p['first_name']} {p['last_name']}"


def payload(conn, as_of=None):
    _, tops, power = compute(conn, as_of)
    state_rows = dict(conn.execute("SELECT key, value FROM sync_state").fetchall())

    top_out, power_out = {}, {}
    for (st, dist, g), entries in tops.items():
        top_out.setdefault(st, {}).setdefault(dist, {})[g] = [
            [runner_name(p), p["city"] or "", round(p["seconds"], 1), p["race_name"], p["event_date"]]
            for p in entries
        ]
    for (st, g), runners in power.items():
        power_out.setdefault(st, {})[g] = [
            [runner_name(r), r["city"] or "", round(r["score"], 1), r["races"],
             [[p["distance_key"], round(p["seconds"], 1), p["race_name"], p["event_date"], round(p["points"], 1)]
              for p in r["counting"]]]
            for r in runners
        ]

    return {
        "meta": {
            "site": SITE_NAME, "tagline": SITE_TAGLINE,
            "lastSync": state_rows.get("last_sync"), "built": (as_of or date.today()).isoformat(),
            "sample": state_rows.get("sample") == "1",
        },
        "states": US_STATES,
        "distances": {k: v[0] for k, v in DISTANCES.items()},
        "top": top_out,
        "power": power_out,
    }


def build(db_path=None, out_dir=None, as_of=None):
    out_dir = Path(out_dir or SITE_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    with connect(Path(db_path) if db_path else None) as conn:
        data = payload(conn, as_of)
    blob = json.dumps(data, separators=(",", ":")).replace("</", "<\\/")
    body = TEMPLATE.read_text().replace("__SITE_NAME__", SITE_NAME).replace("/*__DATA__*/null", blob)
    # Fragment (no doctype) is what the Claude preview publishes; index.html is the full page for GitHub Pages.
    (out_dir / "preview.html").write_text(body)
    page = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            '<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}'
            'body{margin:0}[hidden]{display:none!important}</style>\n</head>\n<body>\n' + body + "\n</body>\n</html>\n")
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
