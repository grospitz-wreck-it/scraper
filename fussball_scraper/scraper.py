from playwright.sync_api import sync_playwright
import pandas as pd
import re
from unidecode import unidecode

LEAGUES = [
    "https://www.fussball.de/wettbewerb/bundesliga",
    # 👉 weitere Ligen hier einfügen
]

def normalize(name):
    name = name.lower()
    name = unidecode(name)
    name = re.sub(r'\b(e\.v\.|gmbh|ag)\b', '', name)
    name = re.sub(r'[^a-z0-9 ]', '', name)
    return name.strip()


def extract_teams(page):
    teams = []

    # 👉 wichtigste Strategie: echte Team-Links finden
    anchors = page.locator("a:has-text('')")
    count = anchors.count()

    for i in range(count):
        text = anchors.nth(i).inner_text().strip()

        if not text:
            continue

        # 👉 typische Fußballnamen erkennen
        if any(prefix in text.lower() for prefix in ["sv", "fc", "tsv", "vfl", "sc"]):
            if 3 < len(text) < 50:
                teams.append(text)

    return list(set(teams))


def scrape():
    data = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        for league in LEAGUES:
            print(f"👉 {league}")
            page.goto(league, timeout=60000)
            page.wait_for_timeout(4000)

            # 👉 Teams Tab klicken (entscheidend!)
            try:
                page.click("text=Teams", timeout=5000)
                page.wait_for_timeout(4000)
            except:
                print("⚠️ kein Teams-Tab")

            teams = extract_teams(page)

            print(f"   → {len(teams)} Teams gefunden")

            for t in teams:
                data.append({
                    "league": league,
                    "team": t,
                    "team_norm": normalize(t)
                })

        browser.close()

    return pd.DataFrame(data)


df = scrape()
df.to_csv("teams_once.csv", index=False)

print("✅ Fertig:", len(df), "Teams")
