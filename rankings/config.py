"""Central configuration. Change SITE_NAME once you've picked the real brand."""
import os
from pathlib import Path

SITE_NAME = os.environ.get("SITE_NAME", "50x50")
SITE_TAGLINE = "The top 50 road runners in every state"

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = Path(os.environ.get("DB_PATH", ROOT / "data" / "rankings.db"))
SITE_DIR = ROOT / "site"

TOP_N = 50
LOOKBACK_DAYS = 365  # rankings cover a rolling 12 months

# Canonical distances: key -> (label, meters, accepted spellings)
DISTANCES = {
    "5k": ("5K", 5000, ["5k", "5 k", "5km", "5 km", "3.1 mi", "3.1 miles", "3.1mi"]),
    "10k": ("10K", 10000, ["10k", "10 k", "10km", "10 km", "6.2 mi", "6.2 miles", "6.2mi"]),
    "15k": ("15K", 15000, ["15k", "15 k", "15km", "15 km", "9.3 mi", "9.3 miles"]),
    "half": ("Half Marathon", 21097.5, ["half marathon", "half", "13.1", "13.1 mi", "13.1 miles", "21.1k", "21.1 km"]),
    "full": ("Marathon", 42195, ["marathon", "full marathon", "26.2", "26.2 mi", "26.2 miles", "42.2k", "42.2 km"]),
}

# Plausibility floors (seconds) — anything faster is treated as a data error.
# Roughly world-record pace minus a margin, men's and women's combined.
MIN_SECONDS = {"5k": 12 * 60 + 30, "10k": 26 * 60, "15k": 40 * 60, "half": 57 * 60, "full": 2 * 3600}

# Benchmark times (seconds) used to normalize performances for Power Rankings.
# A performance equal to the benchmark scores 1000 points before depth weighting.
BENCHMARKS = {
    "M": {"5k": 14 * 60, "10k": 29 * 60, "15k": 44 * 60 + 30, "half": 63 * 60, "full": 2 * 3600 + 12 * 60},
    "F": {"5k": 15 * 60 + 30, "10k": 32 * 60, "15k": 49 * 60 + 30, "half": 70 * 60, "full": 2 * 3600 + 28 * 60},
}

US_STATES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California",
    "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware", "FL": "Florida", "GA": "Georgia",
    "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa",
    "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi", "MO": "Missouri",
    "MT": "Montana", "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey",
    "NM": "New Mexico", "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio",
    "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont",
    "VA": "Virginia", "WA": "Washington", "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming",
}
