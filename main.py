tmpimport asyncio
from playwright.async_api import async_playwright
import pandas as pd

BASE_URL = "https://www.fupa.net"

# Beispiel-Ligen (kannst du erweitern)
LEAGUES = [
    "/liga/bundesliga",
    "/liga/2-bundesliga",
    "/liga/3-liga",
    "/liga/regionalliga-bayern",
    "/liga/regionalliga-west",
    "/liga/kreisliga-a"
]

async def scrape_league(page, league_url):
    full_url = BASE_URL + league_url
    print(f"Lade {full_url}")
    
    await page.goto(full_url, timeout=60000)
    await page.wait_for_selector("table", timeout=10000)

    teams = await page.evaluate("""
    () => {
        const rows = document.querySelectorAll("table tbody tr");
        let data = [];
        
        rows.forEach(row => {
            const team = row.querySelector("a");
            if(team){
                data.push({
                    name: team.innerText.trim(),
                    url: team.href
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
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        for league in LEAGUES:
            try:
                teams = await scrape_league(page, league)
                
                for t in teams:
                    t["league"] = league
                
                results.extend(teams)

            except Exception as e:
                print(f"Fehler bei {league}: {e}")

        await browser.close()

    df = pd.DataFrame(results)
    df.drop_duplicates(inplace=True)
    df.to_csv("fupa_export.csv", index=False)

    print("✅ Export fertig: fupa_export.csv")


if __name__ == "__main__":
    asyncio.run(main())
