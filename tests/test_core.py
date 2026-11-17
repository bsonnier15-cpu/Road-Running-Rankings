import unittest
from datetime import date
from pathlib import Path

from rankings.db import connect
from rankings.ingest import add_result, refresh_finisher_counts, upsert_event, upsert_race
from rankings.normalize import distance_key, parse_seconds
from rankings.rank import compute


class Normalize(unittest.TestCase):
    def test_distances(self):
        self.assertEqual(distance_key("Half Marathon"), "half")
        self.assertEqual(distance_key("Marathon"), "full")
        self.assertEqual(distance_key("13.1 Miles"), "half")
        self.assertEqual(distance_key("Turkey Trot 5K"), "5k")
        self.assertEqual(distance_key("10K Run"), "10k")
        self.assertIsNone(distance_key("Marathon Relay"))
        self.assertIsNone(distance_key("Kids 1 Mile"))
        self.assertIsNone(distance_key("50K Ultra"))

    def test_times(self):
        self.assertEqual(parse_seconds("1:23:45"), 5025)
        self.assertEqual(parse_seconds("17:05.5"), 1025.5)
        self.assertIsNone(parse_seconds("DNF"))


class Rankings(unittest.TestCase):
    def setUp(self):
        self.ctx = connect(Path(":memory:"))
        self.conn = self.ctx.__enter__()
        d = date.today().isoformat()
        upsert_race(self.conn, 1, "Capitol 10K", "Austin", "TX")
        upsert_event(self.conn, 10, 1, "10K", "10k", d)
        rows = [("Ana", "Garza", "F", 34 * 60, 30), ("Bea", "Reyes", "F", 36 * 60, 41),
                ("Cal", "Hale", "M", 31 * 60, 28), ("Ana", "Garza", "F", 35 * 60, 30)]
        for i, (f, l, g, t, age) in enumerate(rows):
            add_result(self.conn, 10, "10k", d, {"result_id": i, "first_name": f, "last_name": l,
                                                 "gender": g, "state": "TX", "age": age, "chip_time": t})
        refresh_finisher_counts(self.conn)

    def tearDown(self):
        self.ctx.__exit__(None, None, None)

    def test_same_runner_matched(self):
        n = self.conn.execute("SELECT COUNT(*) FROM runners").fetchone()[0]
        self.assertEqual(n, 3)

    def test_top_times_keeps_best(self):
        _, tops, power = compute(self.conn)
        women = tops[("TX", "10k", "F")]
        self.assertEqual([p["last_name"] for p in women], ["Garza", "Reyes"])
        self.assertEqual(women[0]["seconds"], 34 * 60)
        self.assertEqual(power[("TX", "F")][0]["last_name"], "Garza")


if __name__ == "__main__":
    unittest.main()
