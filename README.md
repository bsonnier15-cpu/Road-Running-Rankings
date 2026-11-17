# Road Rankings (working name: 50x50)

The top 50 road runners in every U.S. state, across 5K, 10K, 15K, half marathon and marathon, with Top Times and depth-weighted Power Rankings. Results come from RunSignup, refresh nightly, and publish to GitHub Pages.

## Run it locally

```bash
python -m unittest discover -s tests       # tests
python -m rankings.sample --db data/sample.db
python -m rankings.build --db data/sample.db
open site/index.html
```

No third-party packages needed; it's standard-library Python 3.11+.

## Go live

1. Create a GitHub repo and push this folder.
2. Get a RunSignup API key and secret (RunSignup account → API keys). Add them as repo secrets `RSU_API_KEY` and `RSU_API_SECRET`.
3. Repo Settings → Pages → Source: **GitHub Actions**.
4. Actions → "Nightly sync and deploy" → Run workflow with `days = 365` once to backfill a year. After that it runs every night on its own.

## Renaming

Set `SITE_NAME` in `rankings/config.py` (or as an env var in the workflow). Everything else picks it up.

## How the rankings work

- **Top Times**: each runner's fastest time at a distance in the last 12 months. Runners are ranked in their home state, not where the race was.
- **Power Rankings**: every race scores `1000 × (benchmark ÷ time)²`, then gets a depth multiplier for field size, the number of other strong runners in the race, and placing among them. A runner's score blends their three best races at any distance, weighted 50/30/20.
- **Identity**: results are matched to one runner by name, gender, home state and birth year (from race-day age), so the same person across races counts as one entry.

Tuning knobs (benchmarks, top N, lookback window) are in `rankings/config.py` and `rankings/rank.py`.
