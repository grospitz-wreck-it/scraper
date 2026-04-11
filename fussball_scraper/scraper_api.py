import requests
import pandas as pd
import re
from unidecode import unidecode

def normalize(name):
    name = name.lower()
    name = unidecode(name)
    name = re.sub(r'\b(e\.v\.|gmbh|ag)\b', '', name)
    name = re.sub(r'[^a-z0-9 ]', '', name)
    return name.strip()


# 👉 Beispiel: Bundesliga Teams direkt
API_URL = "https://www.fussball.de/ajax.teamlist/-/staffel/02TKC4CR0O00001BVS5489BUVUD1610F-G"

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}

response = requests.get(API_URL, headers=headers)

data = response.json()

teams = []

for team in data.get("teams", []):
    name = team.get("name")
    if name:
        teams.append({
            "league": "bundesliga",
            "team": name,
            "team_normalized": normalize(name)
        })

df = pd.DataFrame(teams)
df.to_csv("teams_once.csv", index=False)

print("✅ Fertig:", len(df), "Teams")
