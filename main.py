import asyncio
from playwright.async_api import async_playwright
import pandas as pd

BASE_URL = "https://www.fupa.net"

async def get_all_league_links(page):
    print("🔍 Lade Ligenübersicht...")
    await page.goto(f"{BASE_URL}/ligen", timeout=60000)
    await page.wait_for_selector("a", timeout=10000)

    links = await page.evaluate("""
    () => {
        const anchors = document.querySelectorAll("a");
        let leagues = new Set();

        anchors.forEach(a => {
            if (a.href.includes("/liga/")) {
                leagues.add(a.getAttribute("href"));
            }
        });

        return Array.from(leagues);
    }
    """)

    print(f"➡️ {len(links)} Ligen gefunden")
    return links


async def scrape_teams_from_league(page, league_url):
    full_url = BASE_URL + league_url
    print(f"📄 {full_url}")

    try:
        await page.goto(full_url, timeout=60000)
        await page.wait_for_selector("table", timeout=8000)
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
    all_results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # 1. alle Ligen holen
        leagues = await get_all_league_links(page)

        # optional: filtern (z.B. nur Deutschland)
        leagues = [l for l in leagues if l.startswith("/liga/")]

        print(f"🚀 Starte Scraping von {len(leagues)} Ligen...\n")

        # 2. jede Liga scrapen
        for i, league in enumerate(leagues):
            print(f"[{i+1}/{len(leagues)}]")

            teams = await scrape_teams_from_league(page, league)

            for t in teams:
                t["league"] = league

            all_results.extend(teams)

            await asyncio.sleep(0.5)  # freundlich bleiben :)

        await browser.close()

    # 3. DataFrame + Export
    df = pd.DataFrame(all_results)

    df.drop_duplicates(inplace=True)

    df.to_csv("fupa_full_export.csv", index=False)

    print("\n✅ Fertig!")
    print(f"📦 {len(df)} Teams gespeichert in fupa_full_export.csv")


if __name__ == "__main__":
    asyncio.run(main())
