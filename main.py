from bs4 import BeautifulSoup
import requests
import pandas as pd
import re
from unidecode import unidecode

BASE_URL = "https://www.transfermarkt.de"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "de-DE,de;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Connection": "keep-alive",
}


def normalize(name):
    name = name.lower()
    name = unidecode(name)
    name = re.sub(r'\b(e\.v\.|gmbh|ag)\b', '', name)
    name = re.sub(r'[^a-z0-9 ]', '', name)
    return name.strip()


def scrape_league(code, league_name):
    url = f"{BASE_URL}/{league_name}/startseite/wettbewerb/{code}"

    print(f"👉 {league_name} ({code})")

    session = requests.Session()
    session.headers.update(HEADERS)

    # 👉 WICHTIG: Erst Startseite laden (setzt Cookies)
    session.get(BASE_URL)

    res = session.get(url)

    soup = BeautifulSoup(res.text, "html.parser")

    teams = []

    # 👉 Debug (einmal laufen lassen!)
    if "verein" not in res.text:
        print("   ⚠️ Seite ohne Vereinsdaten geladen")

    table = soup.select_one("table.items")

    if not table:
        print("   ❌ Tabelle nicht gefunden")
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

    teams = list({t["team"]: t for t in teams}.values())

    print(f"   ✅ {len(teams)} Teams")

    return teams


LEAGUES = [
    ("VLW1", "westfalenliga-1"),
]

all_teams = []

for code, name in LEAGUES:
    teams = scrape_league(code, name)
    all_teams.extend(teams)

df = pd.DataFrame(all_teams)
df.to_csv("teams_transfermarkt.csv", index=False)

print("\n🎉 FERTIG:", len(df), "Teams gesamt")
