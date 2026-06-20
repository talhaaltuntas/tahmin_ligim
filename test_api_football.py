import requests
import json

API_KEY = "aed9131fa2f16768e0176986c3307409"
headers = {
    "x-apisports-key": API_KEY
}

# 1. Try fetching odds by fixture ID
fixture_id = 1489392
print(f"Fetching odds for fixture {fixture_id}...")
r = requests.get(f"https://v3.football.api-sports.io/odds?fixture={fixture_id}", headers=headers)
if r.ok:
    data = r.json()
    print("Fixture Odds response:")
    print(json.dumps(data, indent=2))
else:
    print("Error:", r.text)

# 2. Try fetching odds by date
print("\nFetching odds for date 2026-06-21...")
r = requests.get("https://v3.football.api-sports.io/odds?date=2026-06-21", headers=headers)
if r.ok:
    data = r.json()
    print("Date Odds response length:", len(data.get("response", [])))
    if data.get("response"):
        print("First odd item:")
        print(json.dumps(data.get("response")[0], indent=2))
else:
    print("Error:", r.text)
