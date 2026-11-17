"""Rankings engine.

Top Times
    Each runner's single best time at a distance in the last 12 months.
    Top 50 per state x distance x gender.

Power Rankings (depth-weighted)
    1. Every performance gets base points: 1000 * (benchmark / time)^2, so a
       benchmark-level run is 1000 and slower runs fall off smoothly.
    2. Base points are multiplied by a depth factor for that race:
         - field size:   bigger fields count a little more (log scale, 0.92-1.08)
         - competition:  +1.5% for every other strong runner (>= 650 base pts)
                         in the same race, capped at +12%
         - placing:      +4% for a win, +2% for top 3 among strong runners
    3. A runner's Power Score is a weighted blend of their best three weighted
       performances at any distance: 50% / 30% / 20%. One great race helps, but
       racing well repeatedly against good fields is what wins.
"""
import math
from collections import defaultdict
from datetime import date, timedelta

from .config import BENCHMARKS, LOOKBACK_DAYS, TOP_N

STRONG = 650
BLEND = (0.5, 0.3, 0.2)


def base_points(gender, dist_key, seconds):
    return 1000.0 * (BENCHMARKS[gender][dist_key] / seconds) ** 2


def field_factor(finishers):
    if finishers <= 0:
        return 1.0
    return max(0.92, min(1.08, 1.0 + 0.02 * math.log2(finishers / 100)))


def load_performances(conn, as_of=None):
    as_of = as_of or date.today()
    since = (as_of - timedelta(days=LOOKBACK_DAYS)).isoformat()
    rows = conn.execute(
        """SELECT r.result_id, r.runner_id, r.seconds, r.event_id,
                  e.distance_key, e.event_date, e.finishers,
                  ra.name AS race_name, ra.city AS race_city, ra.state AS race_state,
                  u.first_name, u.last_name, u.gender, u.state, u.city, u.birth_year
           FROM results r
           JOIN events e  ON e.event_id = r.event_id
           JOIN races ra  ON ra.race_id = e.race_id
           JOIN runners u ON u.runner_id = r.runner_id
           WHERE e.event_date BETWEEN ? AND ?""",
        (since, as_of.isoformat()),
    ).fetchall()
    return [dict(r) for r in rows]


def score_performances(perfs):
    """Attach base and depth-weighted points to each performance (in place)."""
    by_event = defaultdict(list)
    for p in perfs:
        p["base"] = base_points(p["gender"], p["distance_key"], p["seconds"])
        by_event[(p["event_id"], p["gender"])].append(p)

    for (_, _), field in by_event.items():
        strong = sorted((p for p in field if p["base"] >= STRONG), key=lambda p: p["seconds"])
        strong_rank = {p["result_id"]: i + 1 for i, p in enumerate(strong)}
        for p in field:
            others = len(strong) - (1 if p["result_id"] in strong_rank else 0)
            comp = min(0.12, 0.015 * others)
            place = strong_rank.get(p["result_id"])
            placing = 0.04 if place == 1 and others > 0 else 0.02 if place and place <= 3 and others > 1 else 0.0
            p["depth"] = field_factor(p["finishers"]) * (1 + comp + placing)
            p["points"] = p["base"] * p["depth"]
    return perfs


def top_times(perfs):
    """{(state, dist, gender): [entry, ...]} — best time per runner, top N."""
    best = {}
    for p in perfs:
        k = (p["state"], p["distance_key"], p["gender"], p["runner_id"])
        if k not in best or p["seconds"] < best[k]["seconds"]:
            best[k] = p
    grouped = defaultdict(list)
    for (state, dist, gender, _), p in best.items():
        grouped[(state, dist, gender)].append(p)
    out = {}
    for key, entries in grouped.items():
        entries.sort(key=lambda p: (p["seconds"], p["event_date"]))
        out[key] = entries[:TOP_N]
    return out


def power_rankings(perfs):
    """{(state, gender): [runner dict with score + counting races], ...}"""
    by_runner = defaultdict(list)
    for p in perfs:
        by_runner[p["runner_id"]].append(p)

    grouped = defaultdict(list)
    for runner_id, races in by_runner.items():
        # One counting performance per event (guards against duplicate result sets).
        unique = {}
        for p in races:
            if p["event_id"] not in unique or p["points"] > unique[p["event_id"]]["points"]:
                unique[p["event_id"]] = p
        best = sorted(unique.values(), key=lambda p: -p["points"])[:3]
        score = sum(w * p["points"] for w, p in zip(BLEND, best))
        head = best[0]
        grouped[(head["state"], head["gender"])].append({
            "runner_id": runner_id,
            "first_name": head["first_name"], "last_name": head["last_name"],
            "gender": head["gender"], "state": head["state"], "city": head["city"],
            "score": score, "races": len(unique), "counting": best,
        })

    out = {}
    for key, runners in grouped.items():
        runners.sort(key=lambda r: -r["score"])
        out[key] = runners[:TOP_N]
    return out


def compute(conn, as_of=None):
    perfs = score_performances(load_performances(conn, as_of))
    return perfs, top_times(perfs), power_rankings(perfs)
