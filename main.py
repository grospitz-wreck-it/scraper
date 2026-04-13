from bs4 import BeautifulSoup
import requests
import pandas as pd
import re
from unidecode import unidecode

URL = "https://www.transfermarkt.de/westfalenliga-1/startseite/wettbewerb/VLW1"


def normalize(name):
    name = name.lower()
    name = unidecode(name)
    name = re.sub(r'\b(e\.v\.|gmbh|ag)\b', '', name)
    name = re.sub(r'[^a-z0-9 ]', '', name)
    return name.strip()


headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(URL, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

teams = []

# 👉 ALLE Vereinslinks extrahieren
for a in soup.select("a[href*='/verein/']"):
    name = a.get_text(strip=True)

    if name and 3 < len(name) < 60:
        teams.append({
            "league": "westfalenliga_1",
            "team": name,
            "team_normalized": normalize(name)
        })

# 👉 dedupe
teams = list({t["team"]: t for t in teams}.values())

df = pd.DataFrame(teams)
df.to_csv("teams_transfermarkt.csv", index=False)

print("✅ Fertig:", len(df), "Teams")
