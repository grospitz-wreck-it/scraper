from playwright.sync_api import sync_playwright
import pandas as pd
import re
from unidecode import unidecode

# 👉 HIER deine Ligen eintragen
LEAGUES = [
    "https://www.fussball.de/spieltagsuebersicht/bundesliga-deutschland-bundesliga-herren-saison2526-deutschland/-/staffel/02TKC4CR0O00001BVS5489BUVUD1610F-G#!/"
]


def normalize(name):
    name = name.lower()
    name = unidecode(name)
    name = re.sub(r'\b(e\.v\.|gmbh|ag)\b', '', name)
    name = re.sub(r'[^a-z0-9 ]', '', name)
    return name.strip()


def extract_teams(page):
    teams = []
    elements = page.locator("a[href*='verein']")

    for i in range(elements.count()):
        text = elements.nth(i).inner_text().strip()

        if text and 3 < len(text) < 60:
            teams.append(text)

    return list(set(teams))


def scrape():
    data = []

    with sync_playwright() as p:
        browser = p.firefox.launch
    headless=True,
    executable_path="/home/codespace/.cache/ms-playwright/chromium-1208/chrome-linux/chrome",
    args=[
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
        "--disable-software-rasterizer",
        "--disable-setuid-sandbox",
        "--disable-features=UseOzonePlatform",
    ]
)

        # 👉 DAS HAT GEFEHLT
        context = browser.new_context()
        page = context.new_page()

        for league in LEAGUES:
            print(f"\n👉 Lade Liga: {league}")

            page.goto(league, timeout=60000)
            page.wait_for_timeout(5000)

            # 👉 warten bis Tabs da sind
            page.wait_for_selector("text=Tabelle")

            # 👉 auf Mannschaften klicken
            if page.locator("text=Mannschaften").count() > 0:
                page.click("text=Mannschaften")
            elif page.locator("text=Teams").count() > 0:
                page.click("text=Teams")
            else:
                print("❌ Kein Teams-Tab gefunden")
                continue

            page.wait_for_timeout(5000)

            teams = extract_teams(page)

            print(f"✅ {len(teams)} Teams gefunden")

            for team in teams:
                data.append({
                    "league": league,
                    "team": team,
                    "team_normalized": normalize(team)
                })

        browser.close()

    return pd.DataFrame(data)


if __name__ == "__main__":
    df = scrape()
    df.to_csv("teams_once.csv", index=False)
    print("\n🎉 Fertig! Datei: teams_once.csv")
