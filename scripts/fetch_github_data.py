"""Fetch real contribution calendar and public repository data for this profile."""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "contributions.json"
USERNAME = "singhdeepesh20"
ENDPOINT = "https://api.github.com/graphql"

QUERY = """query($login:String!, $from:DateTime!, $to:DateTime!) {
  user(login:$login) {
    createdAt
    contributionsCollection(from:$from,to:$to) {
      contributionCalendar { totalContributions weeks { contributionDays { date contributionCount } } }
    }
    repositories(first:100, ownerAffiliations:OWNER, privacy:PUBLIC, orderBy:{field:STARGAZERS,direction:DESC}) {
      nodes { name url description stargazerCount primaryLanguage { name } }
    }
  }
}"""


def graphql(token: str, start: date, end: date) -> dict:
    body = json.dumps({"query": QUERY, "variables": {
        "login": USERNAME, "from": datetime.combine(start, datetime.min.time(), timezone.utc).isoformat(),
        "to": datetime.combine(end, datetime.max.time(), timezone.utc).isoformat(),
    }}).encode()
    request = urllib.request.Request(ENDPOINT, body, headers={
        "Authorization": f"Bearer {token}", "Content-Type": "application/json",
        "User-Agent": "singhdeepesh20-profile-dashboard",
    })
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                result = json.loads(response.read())
            if result.get("errors"):
                raise RuntimeError("GitHub GraphQL: " + "; ".join(e.get("message", "unknown error") for e in result["errors"]))
            if not result.get("data", {}).get("user"):
                raise RuntimeError(f"GitHub user {USERNAME!r} was not returned")
            return result["data"]["user"]
        except urllib.error.HTTPError as exc:
            rate_limited = exc.code == 429 or (exc.code == 403 and exc.headers.get("X-RateLimit-Remaining") == "0")
            if rate_limited or exc.code >= 500:
                if attempt < 3:
                    retry_after = exc.headers.get("Retry-After")
                    time.sleep(min(int(retry_after), 30) if retry_after and retry_after.isdigit() else 2 ** attempt)
                    continue
            raise RuntimeError(f"GitHub API returned HTTP {exc.code}") from exc
    raise RuntimeError("GitHub API retry limit exceeded")


def main() -> int:
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Set GH_TOKEN (or GITHUB_TOKEN) to fetch private contribution data.", file=sys.stderr)
        return 1
    today = datetime.now(timezone.utc).date()
    try:
        # GitHub limits contribution collection windows; use adjacent one-year slices.
        user = graphql(token, today - timedelta(days=364), today)
        created = date.fromisoformat(user["createdAt"][:10])
        all_days = [d for week in user["contributionsCollection"]["contributionCalendar"]["weeks"]
                    for d in week["contributionDays"]]
        cursor = today - timedelta(days=365)
        while cursor >= created:
            end = cursor + timedelta(days=364)
            historical = graphql(token, max(created, cursor), end)
            all_days.extend(d for week in historical["contributionsCollection"]["contributionCalendar"]["weeks"]
                            for d in week["contributionDays"])
            cursor -= timedelta(days=365)
        calendar = user["contributionsCollection"]["contributionCalendar"]
        # Merge overlapping dates while retaining GitHub's exact daily counts.
        days = all_days
        normalized = {d["date"]: int(d["contributionCount"]) for d in days}
        data = {
            "username": USERNAME,
            "days": [{"date": key, "contributionCount": value} for key, value in sorted(normalized.items())],
            "repositories": user["repositories"]["nodes"],
        }
        OUT.parent.mkdir(parents=True, exist_ok=True)
        temp = OUT.with_suffix(".json.tmp")
        temp.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        temp.replace(OUT)
        print(f"Saved {len(normalized)} contribution dates and {len(data['repositories'])} repositories.")
        return 0
    except (OSError, KeyError, RuntimeError, ValueError) as exc:
        # Never replace a previously valid snapshot on an API or decoding failure.
        print(f"GitHub data fetch failed; existing snapshot was preserved: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
