
import json
import urllib.request
import urllib.error
import datetime
import time
from pathlib import Path

README = Path("README.md")
START = "<!--F1_STANDINGS_START-->"
END = "<!--F1_STANDINGS_END-->"

URLS = {
    "drivers_https": "https://ergast.com/api/f1/current/driverStandings.json",
    "drivers_http":  "http://ergast.com/api/f1/current/driverStandings.json",
    "teams_https":   "https://ergast.com/api/f1/current/constructorStandings.json",
    "teams_http":    "http://ergast.com/api/f1/current/constructorStandings.json",
}

def fetch_json_with_fallback(primary, fallback, retries=3, backoff=5):
    urls = [primary, fallback]
    last_err = None
    for attempt in range(retries):
        url = urls[attempt % 2] if attempt < 2 else urls[0]  # try primary, then fallback, then primary
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
            last_err = e
            time.sleep(backoff)
    raise last_err

def drivers_table():
    data = fetch_json_with_fallback(URLS["drivers_https"], URLS["drivers_http"])
    standings = data["MRData"]["StandingsTable"]["StandingsLists"][0]["DriverStandings"]
    out = ["| Pos | Piloto | Equipo | Pts |", "|:--:|:------|:------|---:|"]
    for s in standings[:10]:
        d = s["Driver"]
        name = f"{d['familyName']}, {d['givenName']}"
        team = s["Constructors"][0]["name"]
        out.append(f"| {s['position']} | {name} | {team} | {s['points']} |")
    return "\n".join(out)

def constructors_table():
    data = fetch_json_with_fallback(URLS["teams_https"], URLS["teams_http"])
    standings = data["MRData"]["StandingsTable"]["StandingsLists"][0]["ConstructorStandings"]
    out = ["| Pos | Constructor | Pts |", "|:--:|:-----------|---:|"]
    for s in standings[:10]:
        out.append(f"| {s['position']} | {s['Constructor']['name']} | {s['points']} |")
    return "\n".join(out)

def build_block():
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    try:
        drivers = drivers_table()
        teams = constructors_table()
        return (
            f"**Actualizado:** {now}\n\n"
            f"### Pilotos (Top 10)\n{drivers}\n\n"
            f"### Constructores (Top 10)\n{teams}\n"
        )
    except Exception as e:
        return (
            f"**Actualizado:** {now}\n\n"
            f"⚠️ No se pudo obtener la tabla de F1 por ahora (posible caída temporal de la API).\n"
            f"Error: `{type(e).__name__}: {e}`\n"
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
