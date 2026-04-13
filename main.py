def scrape_league(code, league_name):
    url = f"https://www.transfermarkt.de/{league_name}/startseite/wettbewerb/{code}"

    print(f"👉 {league_name} ({code})")

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "de-DE,de;q=0.9"
    })

    session.get("https://www.transfermarkt.de")

    res = session.get(url)

    print(res.text[:500])  # DEBUG

    soup = BeautifulSoup(res.text, "html.parser")

    teams = []

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
