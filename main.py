from bs4 import BeautifulSoup
import requests
import pandas as pd
import re
from unidecode import unidecode
import time

BASE_URL = "https://www.transfermarkt.de"
HEADERS = {"User-Agent": "Mozilla/5.0"}


def normalize(name):
    name = name.lower()
    name = unidecode(name)
    name = re.sub(r'\b(e\.v\.|gmbh|ag)\b', '', name)
    name = re.sub(r'[^a-z0-9 ]', '', name)
    return name.strip()


def scrape_league(code, league_name):
    url = f"https://www.transfermarkt.de/{league_name}/startseite/wettbewerb/{code}"

    print(f"👉 {league_name} ({code})")

    try:
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(res.text, "html.parser")

        teams = []

        # 👉 WICHTIG: richtige Tabelle
        table = soup.select_one("table.items")

        if not table:
            print("   ❌ keine Tabelle gefunden")
            return []

        for row in table.select("tbody tr"):
            a = row.select_one("td.hauptlink a")

            if not a:
                continue

            name = a.get_text(strip=True)

            teams.append({
                "league": league_name,
                "team": name,
                "team_normalized": normalize(name)
            })

        # dedupe
        teams = list({t["team"]: t for t in teams}.values())

        print(f"   ✅ {len(teams)} Teams")

        return teams

    except Exception as e:
        print("   ❌ Fehler:", e)
        return []


# 👉 Liste erweitern = mehr Coverage
LEAGUES = [
    ("L1", "bundesliga"),
    ("L2", "2-bundesliga"),
    ("L3", "3-liga"),
    ("RLN", "regionalliga-nord"),
    ("RLW", "regionalliga-west"),
    ("RLSW", "regionalliga-suedwest"),
    ("RLB", "regionalliga-bayern"),
    ("RLNO", "regionalliga-nordost"),
    ("OLW3", "oberliga-westfalen"),
    ("VLW1", "westfalenliga-1"),
    ("VLW2", "westfalenliga-2"),
]


all_teams = []

for code, name in LEAGUES:
    teams = scrape_league(code, name)
    all_teams.extend(teams)
    time.sleep(1)  # 👉 wichtig (kein rate limit)

df = pd.DataFrame(all_teams)

# globale dedupe
df = df.drop_duplicates(subset=["team"])

df.to_csv("germany_teams_full.csv", index=False)

print("\n🎉 FERTIG:", len(df), "Teams gesamt")
