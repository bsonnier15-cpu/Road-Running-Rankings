"""Thin RunSignup REST client.

Credentials come from the environment (RSU_API_KEY / RSU_API_SECRET), which in
GitHub Actions are repository secrets — never commit them.
"""
import json
import os
import time
import urllib.parse
import urllib.request

BASE = "https://api.runsignup.com/rest"


class RunSignup:
    def __init__(self, api_key=None, api_secret=None, pause=0.4):
        self.api_key = api_key or os.environ.get("RSU_API_KEY")
        self.api_secret = api_secret or os.environ.get("RSU_API_SECRET")
        # Registered API caller (required by RunSignup on every request from 2026 on)
        self.reg_token = os.environ.get("RSU_API_REG")
        self.reg_secret = os.environ.get("RSU_API_REG_SECRET")
        self.pause = pause  # be polite: RunSignup rate-limits aggressive callers

    def _get(self, path, **params):
        params = {k: v for k, v in params.items() if v is not None}
        params["format"] = "json"
        if self.api_key:
            params["rsu_api_key"] = self.api_key
        if self.reg_token:
            params["rsu_api_reg"] = self.reg_token
        req = urllib.request.Request(f"{BASE}{path}?{urllib.parse.urlencode(params)}")
        if self.api_secret:
            req.add_header("X-RSU-API-SECRET", self.api_secret)
        if self.reg_secret:
            req.add_header("X-RSU-API-REG-SECRET", self.reg_secret)
        for attempt in range(4):
            try:
                with urllib.request.urlopen(req, timeout=60) as resp:
                    data = json.load(resp)
                time.sleep(self.pause)
                if isinstance(data, dict) and data.get("error"):
                    raise RuntimeError(f"RunSignup error on {path}: {data['error']}")
                return data
            except (urllib.error.URLError, TimeoutError):
                if attempt == 3:
                    raise
                time.sleep(2 ** attempt * 2)

    def races(self, state, start_date, end_date):
        """Yield races in a state with events between two dates (YYYY-MM-DD)."""
        page = 1
        while True:
            data = self._get(
                "/races",
                state=state, start_date=start_date, end_date=end_date,
                events="T", race_headings="F", include_waiver="F",
                only_races_with_results="T", page=page, results_per_page=250,
            )
            races = data.get("races", [])
            for wrapper in races:
                yield wrapper.get("race", wrapper)
            if len(races) < 250:
                return
            page += 1

    def results(self, race_id, event_id):
        """Yield every individual result for one event, across result sets and pages."""
        sets = self._get(f"/race/{race_id}/results/get-result-sets", event_id=event_id)
        set_ids = [s["individual_result_set_id"] for s in sets.get("individual_results_sets", [])]
        for set_id in set_ids or [None]:
            page = 1
            while True:
                data = self._get(
                    f"/race/{race_id}/results/get-results",
                    event_id=event_id, individual_result_set_id=set_id,
                    page=page, results_per_page=1000,
                )
                rows = []
                for rset in data.get("individual_results_sets", []):
                    rows.extend(rset.get("results", []))
                yield from rows
                if len(rows) < 1000:
                    break
                page += 1
            if set_ids:
                break  # the first (primary) result set is the official one
