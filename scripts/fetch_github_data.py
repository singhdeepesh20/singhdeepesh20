
import json
import os
import urllib.request
from datetime import datetime, timezone

USERNAME = "singhdeepesh20"
TOKEN = os.environ["GH_TOKEN"]

now = datetime.now(timezone.utc)
start = datetime(now.year, 1, 1, tzinfo=timezone.utc)

query = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
    repositories(
      first: 6
      ownerAffiliations: OWNER
      privacy: PUBLIC
      orderBy: {field: STARGAZERS, direction: DESC}
    ) {
      nodes {
        name
        url
        description
        stargazerCount
        primaryLanguage {
          name
        }
      }
    }
  }
}
"""

payload = {
    "query": query,
    "variables": {
        "login": USERNAME,
        "from": start.isoformat(),
        "to": now.isoformat()
    }
}

request = urllib.request.Request(
    "https://api.github.com/graphql",
    data=json.dumps(payload).encode(),
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
)

with urllib.request.urlopen(request) as response:
    result = json.loads(response.read())

if "errors" in result:
    raise RuntimeError(result["errors"])

user = result["data"]["user"]
calendar = user["contributionsCollection"]["contributionCalendar"]

days = [
    day
    for week in calendar["weeks"]
    for day in week["contributionDays"]
]

data = {
    "username": USERNAME,
    "generated_at": now.isoformat(),
    "total_contributions": calendar["totalContributions"],
    "days": days,
    "repositories": user["repositories"]["nodes"]
}

os.makedirs("data", exist_ok=True)

with open("data/contributions.json", "w") as file:
    json.dump(data, file, indent=2)

print("GitHub contribution data updated successfully.")
