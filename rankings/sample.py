"""Generate realistic-looking SAMPLE data so the site can be built and previewed
without RunSignup credentials. Every name and race here is invented.

    python -m rankings.sample --db data/sample.db
"""
import argparse
import random
from datetime import date, timedelta
from pathlib import Path

from .config import BENCHMARKS, DISTANCES
from .db import connect
from .ingest import add_result, refresh_finisher_counts, upsert_event, upsert_race

FIRST_M = ["James", "Marcus", "Diego", "Tyler", "Ethan", "Noah", "Caleb", "Andre", "Luis", "Owen",
           "Mason", "Jalen", "Wyatt", "Isaac", "Grant", "Mateo", "Rhys", "Colin", "Darius", "Elijah"]
FIRST_F = ["Ava", "Maya", "Sofia", "Claire", "Jordan", "Riley", "Nadia", "Elena", "Grace", "Leah",
           "Camila", "Hannah", "Tessa", "Brooke", "Imani", "Paige", "Quinn", "Lucia", "Sienna", "Zoe"]
LAST = ["Alvarez", "Brooks", "Carter", "Dubois", "Ellison", "Fontenot", "Garza", "Hale", "Ibarra",
        "Jensen", "Kline", "LeBlanc", "Morales", "Nguyen", "Okafor", "Park", "Quintero", "Reyes",
        "Sato", "Thibodeaux", "Ueda", "Vance", "Whitaker", "Xu", "Young", "Zamora", "Boudreaux",
        "Castillo", "Delgado", "Ferris", "Guidry", "Holloway", "Landry", "Mercer", "Navarro", "Pierce"]

STATES = {
    "TX": ["Austin", "Houston", "Dallas", "San Antonio", "El Paso"],
    "LA": ["New Orleans", "Lafayette", "Baton Rouge", "Shreveport"],
    "CA": ["San Diego", "Sacramento", "Los Angeles", "San Jose"],
    "CO": ["Boulder", "Denver", "Colorado Springs", "Fort Collins"],
    "NY": ["Brooklyn", "Rochester", "Buffalo", "Albany"],
    "OR": ["Eugene", "Portland", "Bend"],
}
RACE_WORDS = ["Bayou", "Capitol", "Riverfront", "Turkey Trot", "Cowtown", "Harbor", "Mile High",
              "Pine Belt", "Lakeshore", "Hill Country", "Gulf Coast", "Rose City", "Front Range"]


def build(db_path, seed=50, runners_per_state=260, races_per_state=24):
    rng = random.Random(seed)
    today = date.today()
    with connect(Path(db_path)) as conn:
        race_id, event_id, result_id = 900000, 9000000, 1
        for state, cities in STATES.items():
            people = []
            for _ in range(runners_per_state):
                g = rng.choice("MF")
                people.append({
                    "first_name": rng.choice(FIRST_M if g == "M" else FIRST_F),
                    "last_name": rng.choice(LAST), "gender": g, "state": state,
                    "city": rng.choice(cities), "age0": rng.randint(18, 62),
                    # talent: 1.0 = benchmark level; most runners are well slower
                    "talent": 1.0 + abs(rng.gauss(0.32, 0.17)),
                })
            for _ in range(races_per_state):
                race_id += 1
                city = rng.choice(cities)
                when = today - timedelta(days=rng.randint(3, 360))
                upsert_race(conn, race_id, f"{rng.choice(RACE_WORDS)} {city} Classic", city, state)
                for dist in rng.sample(list(DISTANCES), rng.randint(1, 3)):
                    event_id += 1
                    upsert_event(conn, event_id, race_id, DISTANCES[dist][0], dist, when.isoformat())
                    field = rng.sample(people, rng.randint(25, 140))
                    for p in field:
                        # fitness drifts a little per race; longer races punish slower runners more
                        stretch = {"5k": 1.0, "10k": 1.02, "15k": 1.03, "half": 1.05, "full": 1.09}[dist]
                        t = BENCHMARKS[p["gender"]][dist] * (p["talent"] ** stretch) * rng.uniform(0.985, 1.05)
                        result_id += 1
                        add_result(conn, event_id, dist, when.isoformat(), {
                            "result_id": result_id, "first_name": p["first_name"],
                            "last_name": p["last_name"], "gender": p["gender"],
                            "state": p["state"], "city": p["city"],
                            "age": p["age0"] - (today.year - when.year),
                            "chip_time": t,
                        })
        refresh_finisher_counts(conn)
        conn.execute("INSERT OR REPLACE INTO sync_state VALUES ('last_sync', ?)", (today.isoformat(),))
        conn.execute("INSERT OR REPLACE INTO sync_state VALUES ('sample', '1')")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default="data/sample.db")
    args = ap.parse_args()
    Path(args.db).unlink(missing_ok=True)
    build(args.db)
    print(f"sample data written to {args.db}")


if __name__ == "__main__":
    main()
