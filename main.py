import asyncio
from playwright.async_api import async_playwright
import pandas as pd

BASE_URL = "https://www.fupa.net"

# Startseiten mit echten Tabellen
START_LEAGUES = [
    "/liga/bundesliga",
    "/liga/2-bundesliga",
    "/liga/3-liga",
    "/liga/regionalliga-bayern",
    "/liga/regionalliga-west",
    "/liga/regionalliga-nordost",
    "/liga/regionalliga-nord",
    "/liga/regionalliga-suedwest"
]


async def scrape_league(page, league_url):
    full_url = BASE_URL + league_url
    print(f"📄 {full_url}")

    try:
        await page.goto(full_url, timeout=60000)
        await page.wait_for_timeout(3000)
    except:
        return []

    teams = await page.evaluate("""
    () => {
        const rows = document.querySelectorAll("table tbody tr");
        let data = [];

        rows.forEach(row => {
            const link = row.querySelector("a");
            if (link) {
                data.push({
                    team_name: link.innerText.trim(),
                    team_url: link.href
                });
            }
        });

        return data;
    }
    """)

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
