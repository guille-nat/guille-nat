
import json
import urllib.request
import urllib.error
import datetime
import time
from pathlib import Path

README = Path("README.md")
START = "<!--F1_STANDINGS_START-->"
END = "<!--F1_STANDINGS_END-->"

CACHE = Path("scripts/data/f1_cache.json")

URLS = [
    # primary HTTPS
    "https://ergast.com/api/f1/current/driverStandings.json",
    "https://ergast.com/api/f1/current/constructorStandings.json",
]

# alternate order variants (HTTP + read-only proxies)
ALT = [
    "http://ergast.com/api/f1/current/driverStandings.json",
    "http://ergast.com/api/f1/current/constructorStandings.json",
    # proxies that serve raw content (avoid CORS + TLS issues in some runners)
    "https://r.jina.ai/http://ergast.com/api/f1/current/driverStandings.json",
    "https://r.jina.ai/http://ergast.com/api/f1/current/constructorStandings.json",
]

UA = {"User-Agent": "Mozilla/5.0 (compatible; NataliUlla-F1-README/1.0)"}

def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=25) as r:
        data = r.read().decode("utf-8")
        # r.jina.ai returns text/plain already containing JSON
        return json.loads(data)

def get_json(primary, fallback_list, retries=4, sleep=6):
    last_err = None
    order = [primary] + fallback_list
    for attempt in range(min(retries, len(order))):
        url = order[attempt]
        try:
            return fetch(url)
        except Exception as e:
            last_err = e
            time.sleep(sleep)
    raise last_err

def load_cache():
    if CACHE.exists():
        try:
            return json.loads(CACHE.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None

def save_cache(drivers_json, constructors_json):
    payload = {
        "drivers": drivers_json,
        "constructors": constructors_json,
        "fetched_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
    CACHE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

def parse_drivers(drivers_json, top=10):
    standings = drivers_json["MRData"]["StandingsTable"]["StandingsLists"][0]["DriverStandings"]
    rows = []
    for s in standings[:top]:
        d = s["Driver"]
        name = f"{d['familyName']}, {d['givenName']}"
        team = s["Constructors"][0]["name"]
        rows.append((s["position"], name, team, s["points"]))
    out = ["| Pos | Piloto | Equipo | Pts |", "|:--:|:------|:------|---:|"]
    for p, name, team, pts in rows:
        out.append(f"| {p} | {name} | {team} | {pts} |")
    return "\n".join(out)

def parse_constructors(constructors_json, top=10):
    standings = constructors_json["MRData"]["StandingsTable"]["StandingsLists"][0]["ConstructorStandings"]
    out = ["| Pos | Constructor | Pts |", "|:--:|:-----------|---:|"]
    for s in standings[:top]:
        out.append(f"| {s['position']} | {s['Constructor']['name']} | {s['points']} |")
    return "\n".join(out)

def build_block():
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    source = "live"
    try:
        drivers_json = get_json(URLS[0], [ALT[0], ALT[2]])
        constructors_json = get_json(URLS[1], [ALT[1], ALT[3]])
        save_cache(drivers_json, constructors_json)
    except Exception as e:
        cached = load_cache()
        if cached:
            drivers_json = cached["drivers"]
            constructors_json = cached["constructors"]
            source = "cache"
        else:
            return (
                f"**Actualizado:** {now}\n\n"
                f"⚠️ No se pudo obtener la tabla de F1 por ahora (la API puede estar caída).\n"
                f"Intenta más tarde o corre el workflow manualmente.\n"
            )
    notice = "fuente: cache" if source == "cache" else "fuente: live"
    return (
        f"**Actualizado:** {now} ({notice})\n\n"
        f"### Pilotos (Top 10)\n{parse_drivers(drivers_json)}\n\n"
        f"### Constructores (Top 10)\n{parse_constructors(constructors_json)}\n"
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
