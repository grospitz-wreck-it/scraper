import requests
import pandas as pd
import time

BASE_URL = "https://www.fupa.net/api/competition"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def fetch_teams(comp_id):
    url = f"{BASE_URL}/{comp_id}/teams"

    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        r.raise_for_status()
        data = r.json()

        teams = []

        for t in data.get("teams", []):
            teams.append({
                "team_id": t.get("id"),
                "team_name": t.get("name"),
                "club": t.get("clubName"),
                "competition_id": comp_id
            })

        return teams

    except Exception as e:
        print(f"Fehler bei {comp_id}: {e}")
        return []


def main():
    comps = pd.read_csv("competitions_rows (1).csv")

    all_teams = []

    for i, row in comps.iterrows():
        comp_id = row["id"]
        name = row.get("name")

        print(f"[{i}] Lade {name}")

        teams = fetch_teams(comp_id)

        for t in teams:
            t["league_name"] = name

        all_teams.extend(teams)

        time.sleep(0.3)

    df = pd.DataFrame(all_teams)
    df.drop_duplicates(inplace=True)

    df.to_csv("fupa_full_export.csv", index=False)

    print(f"\n✅ {len(df)} Teams gespeichert")


if __name__ == "__main__":
    main()
