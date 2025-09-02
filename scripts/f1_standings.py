
import json, urllib.request, datetime
from pathlib import Path

README = Path("README.md")
START = "<!--F1_STANDINGS_START-->"
END = "<!--F1_STANDINGS_END-->"

ERGAST_DRIVERS = "https://ergast.com/api/f1/current/driverStandings.json"
ERGAST_CONSTRUCTORS = "https://ergast.com/api/f1/current/constructorStandings.json"

def fetch_json(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))

def drivers_table():
    data = fetch_json(ERGAST_DRIVERS)
    standings = data["MRData"]["StandingsTable"]["StandingsLists"][0]["DriverStandings"]
    rows = []
    for s in standings[:10]:
        d = s["Driver"]
        name = f"{d['familyName']}, {d['givenName']}"
        team = s["Constructors"][0]["name"]
        rows.append((s["position"], name, team, s["points"]))
    out = ["| Pos | Piloto | Equipo | Pts |", "|:--:|:------|:------|---:|"]
    for p, name, team, pts in rows:
        out.append(f"| {p} | {name} | {team} | {pts} |")
    return "\n".join(out)

def constructors_table():
    data = fetch_json(ERGAST_CONSTRUCTORS)
    standings = data["MRData"]["StandingsTable"]["StandingsLists"][0]["ConstructorStandings"]
    rows = []
    for s in standings[:10]:
        rows.append((s["position"], s["Constructor"]["name"], s["points"]))
    out = ["| Pos | Constructor | Pts |", "|:--:|:-----------|---:|"]
    for p, team, pts in rows:
        out.append(f"| {p} | {team} | {pts} |")
    return "\n".join(out)

def build_block():
    now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    return (
        f"**Actualizado:** {now}\n\n"
        f"### Pilotos (Top 10)\n{drivers_table()}\n\n"
        f"### Constructores (Top 10)\n{constructors_table()}\n"
    )

def replace_block(md, new):
    i = md.find(START)
    j = md.find(END)
    if i == -1 or j == -1:
        return md
    return md[: i + len(START)] + "\n" + new + "\n" + md[j:]

def main():
    md = README.read_text(encoding="utf-8")
    new_md = replace_block(md, build_block())
    README.write_text(new_md, encoding="utf-8")
    print("F1 standings updated.")

if __name__ == "__main__":
    main()
