"""Parsing helpers: distances, times, names, and runner identity."""
import re
import unicodedata

from .config import DISTANCES, MIN_SECONDS, US_STATES


def distance_key(*labels):
    """Map free-text event names/distances ("Half Marathon", "13.1 Miles", "5K Run") to a canonical key."""
    for label in labels:
        if not label:
            continue
        text = str(label).lower().replace("-", " ")
        # Check longest spellings first so "half marathon" wins over "marathon".
        candidates = sorted(
            ((alias, key) for key, (_, _, aliases) in DISTANCES.items() for alias in aliases),
            key=lambda p: -len(p[0]),
        )
        for alias, key in candidates:
            if re.search(r"(?<![\d.])" + re.escape(alias) + r"(?![\d])", text):
                # Exclude relays, walks, kids, virtual and ultra variants.
                if re.search(r"relay|walk|kids|virtual|ultra|50k|challenge|team", text):
                    return None
                return key
    return None


def parse_seconds(value):
    """'1:23:45', '23:45', '23:45.6' -> seconds. Returns None if unparseable."""
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.upper() in {"DNF", "DNS", "DQ", "N/A"}:
        return None
    parts = text.split(":")
    try:
        nums = [float(p) for p in parts]
    except ValueError:
        return None
    seconds = 0.0
    for n in nums:
        seconds = seconds * 60 + n
    return seconds if seconds > 0 else None


def plausible(dist_key, seconds, max_hours=8):
    return seconds is not None and MIN_SECONDS[dist_key] <= seconds <= max_hours * 3600


def clean_name(name):
    name = unicodedata.normalize("NFKD", name or "").encode("ascii", "ignore").decode()
    name = re.sub(r"[^A-Za-z' -]", "", name).strip()
    return re.sub(r"\s+", " ", name)


def gender_code(value):
    v = (value or "").strip().upper()[:1]
    return v if v in {"M", "F"} else None


def state_code(value):
    v = (value or "").strip().upper()
    if v in US_STATES:
        return v
    for code, full in US_STATES.items():
        if full.upper() == v:
            return code
    return None


def match_key(first, last, gender, state, birth_year):
    """Identity key. Birth year is bucketed in 2-year windows because race-day age
    can imply either of two birth years; neighbouring buckets are checked on lookup."""
    f = clean_name(first).lower().split(" ")[0]
    l = clean_name(last).lower().replace(" ", "")
    bucket = (birth_year // 2) * 2 if birth_year else 0
    return f"{f}|{l}|{gender}|{state}|{bucket}"


def fmt_time(seconds):
    s = int(round(seconds))
    h, rem = divmod(s, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"
