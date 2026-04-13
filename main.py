import requests
import pandas as pd

# 👉 Beispiel: Bundesliga Staffel-ID
LEAGUES = {
    "bundesliga": "02TKC4CR0O00001BVS5489BUVUD1610F-G"
}

def get_teams(staffel_id, league_name):
    url = f"https://www.fussball.de/ajax.teamlist/-/staffel/{staffel_id}"

    res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})

    teams = []

    # 👉 einfacher Extract (ohne bs4)
    for line in res.text.split("\n"):
        if "/verein/" in line:
            name = line.strip().split(">")[-2].split("<")[0]

            if name and len(name) < 50:
                teams.append({
                    "league": league_name,
                    "team": name
                })

    return teams


all_teams = []

for league, sid in LEAGUES.items():
    print(f"👉 {league}")
    teams = get_teams(sid, league)
    print(f"   ✅ {len(teams)} Teams")
    all_teams.extend(teams)

df = pd.DataFrame(all_teams)
df.to_csv("teams.csv", index=False)

print("\n🎉 fertig")
