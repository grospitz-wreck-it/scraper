import asyncio
from playwright.async_api import async_playwright
import pandas as pd

BASE_URL = "https://www.fupa.net"

START_LEAGUES = [
    "/liga/bundesliga",
    "/liga/2-bundesliga",
    "/liga/3-liga",
    "/liga/regionalliga-bayern",
    "/liga/regionalliga-west"
]


async def scrape_league(page, league_url):
    full_url = BASE_URL + league_url
    print(f"📄 {full_url}")

    try:
        await page.goto(full_url, timeout=60000)

        # WICHTIG: warten bis alles geladen ist
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(5000)

        # 👉 versuche auf "Tabelle" zu klicken (wenn vorhanden)
        try:
            await page.click("text=Tabelle", timeout=3000)
            await page.wait_for_timeout(3000)
        except:
            pass

    except Exception as e:
        print("Fehler beim Laden:", e)
        return []

    teams = await page.evaluate("""
    () => {
        let data = [];

        // mehrere mögliche Tabellen-Selektoren
        const tables = document.querySelectorAll("table");

        tables.forEach(table => {
            const rows = table.querySelectorAll("tbody tr");

            rows.forEach(row => {
                const link = row.querySelector("a");

                if (link && link.innerText.trim().length > 0) {
                    data.push({
                        team_name: link.innerText.trim(),
                        team_url: link.href
                    });
                }
            });
        });

        return data;
    }
    """)

    print(f"   → {len(teams)} Teams gefunden")
    return teams


async def main():
    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )

        page = await browser.new_page()

        for league in START_LEAGUES:
            teams = await scrape_league(page, league)

            for t in teams:
                t["league"] = league

            results.extend(teams)

        await browser.close()

    df = pd.DataFrame(results)
    df.drop_duplicates(inplace=True)

    df.to_csv("fupa_export.csv", index=False)

    print(f"\n✅ {len(df)} Teams gespeichert")


if __name__ == "__main__":
    asyncio.run(main())
