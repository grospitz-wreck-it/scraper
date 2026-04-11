from bs4 import BeautifulSoup
import requests
import pandas as pd
import re
from unidecode import unidecode

# 👉 Deine Liga (Staffel-ID bleibt gleich)
API_URL = "https://www.fussball.de/ajax.teamlist/-/staffel/02TKC4CR0O00001BVS5489BUVUD1610F-G"


def normalize(name):
    name = name.lower()
    name = unidecode(name)
    name = re.sub(r'\b(e\.v\.|gmbh|ag)\b', '', name)
    name = re.sub(r'[^a-z0-9 ]', '', name)
    return name.strip()


headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(API_URL, headers=headers)

# 👉 Debug (kannst du später entfernen)
print("Status:", response.status_code)

soup = BeautifulSoup(response.text, "html.parser")

teams = []

# 👉 echte Vereinslinks finden
for a in soup.select("a[href*='verein']"):
    name = a.get_text(strip=True)

    if name and 3 < len(name) < 60:
        teams.append({
            "league": "bundesliga",
            "team": name,
            "team_normalized": normalize(name)
        })

# 👉 Deduplizieren
teams = list({t["team"]: t for t in teams}.values())

df = pd.DataFrame(teams)
df.to_csv("teams_once.csv", index=False)

print(f"✅ Fertig: {len(df)} Teams gespeichert")
