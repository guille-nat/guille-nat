"""Genera assets/pitwall.svg con datos reales de la API de GitHub.

Uso: PITWALL_TOKEN=<token> python scripts/build_pitwall.py
Con un token personal (scope `repo`) se cuentan los repos privados y de organizaciones;
con el GITHUB_TOKEN de Actions solo se ven los públicos.
"""
import datetime
import json
import os
import urllib.request
from html import escape

from build_assets import BG_2, CYAN, LINE, MAGENTA, MONO, MUTED, OUT, SANS, SOFT, TEXT, common_defs, svg

USER = "guille-nat"
WEEKDAYS = ["LU", "MA", "MI", "JU", "VI", "SÁ", "DO"]
TOP_LANGS = 5


def graphql(query, **variables):
    token = os.environ.get("PITWALL_TOKEN") or os.environ.get("GITHUB_TOKEN") or os.environ["GH_TOKEN"]
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        body = json.load(resp)
    if body.get("errors"):
        raise RuntimeError(body["errors"])
    return body["data"]


def fetch():
    year = graphql(
        """query($login: String!) { user(login: $login) { createdAt contributionsCollection {
            totalCommitContributions totalPullRequestContributions totalPullRequestReviewContributions
            contributionCalendar { totalContributions weeks { contributionDays { date contributionCount } } }
            commitContributionsByRepository(maxRepositories: 100) {
              contributions { totalCount } repository { isFork primaryLanguage { name color } } } } } }""",
        login=USER,
    )["user"]

    # El calendario de la API va de a un año como máximo: para las rachas recorremos desde el alta
    days = {}
    start = datetime.date.fromisoformat(year["createdAt"][:10])
    today = datetime.datetime.now(datetime.timezone.utc).date()
    cursor = start
    while cursor <= today:
        end = min(cursor + datetime.timedelta(days=364), today)
        cal = graphql(
            """query($login: String!, $from: DateTime!, $to: DateTime!) { user(login: $login) {
                contributionsCollection(from: $from, to: $to) { contributionCalendar {
                  weeks { contributionDays { date contributionCount } } } } } }""",
            login=USER,
            **{"from": f"{cursor}T00:00:00Z", "to": f"{end}T23:59:59Z"},
        )["user"]["contributionsCollection"]["contributionCalendar"]
        for week in cal["weeks"]:
            for d in week["contributionDays"]:
                days[d["date"]] = d["contributionCount"]
        cursor = end + datetime.timedelta(days=1)
    return year, days, today


def streaks(days, today):
    ordered = sorted(days.items())
    longest = run = 0
    for _, count in ordered:
        run = run + 1 if count else 0
        longest = max(longest, run)

    # Hoy sin contribuciones todavía no corta la racha
    current = 0
    day = today if days.get(today.isoformat()) else today - datetime.timedelta(days=1)
    while days.get(day.isoformat()):
        current += 1
        day -= datetime.timedelta(days=1)
    return current, longest


def languages(year):
    totals, colors = {}, {}
    for item in year["contributionsCollection"]["commitContributionsByRepository"]:
        repo = item["repository"]
        lang = repo["primaryLanguage"]
        if repo["isFork"] or not lang:
            continue
        totals[lang["name"]] = totals.get(lang["name"], 0) + item["contributions"]["totalCount"]
        colors[lang["name"]] = lang["color"] or MUTED
    ranked = sorted(totals.items(), key=lambda kv: -kv[1])
    top = ranked[:TOP_LANGS]
    rest = sum(v for _, v in ranked[TOP_LANGS:])
    if rest:
        top.append(("Otros", rest))
        colors["Otros"] = "#475569"
    total = sum(v for _, v in top) or 1
    return [(name, count / total, colors[name]) for name, count in top]


def weekday_totals(year):
    totals = [0] * 7
    for week in year["contributionsCollection"]["contributionCalendar"]["weeks"]:
        for d in week["contributionDays"]:
            totals[datetime.date.fromisoformat(d["date"]).weekday()] += d["contributionCount"]
    return totals


def fmt(n):
    return f"{n:,}".replace(",", ".")


def build(year, days, today):
    w, h = 1200, 470
    coll = year["contributionsCollection"]
    current, longest = streaks(days, today)
    review_count = coll["totalPullRequestReviewContributions"]
    reviews = f"+ {fmt(review_count)} reviews" if review_count else "últimos 12 meses"
    tiles = [
        ("CONTRIBUCIONES", fmt(coll["contributionCalendar"]["totalContributions"]), "últimos 12 meses"),
        ("COMMITS", fmt(coll["totalCommitContributions"]), "últimos 12 meses"),
        ("PULL REQUESTS", fmt(coll["totalPullRequestContributions"]), reviews),
        ("RACHA ACTUAL", f"{current} d", "días seguidos"),
        ("MEJOR RACHA", f"{longest} d", f"desde {year['createdAt'][:4]}"),
    ]
    tile_w, gap = 212, 15
    tile_svg = "".join(
        f'<g class="tile" style="animation-delay:{i * 0.12:.2f}s">'
        f'<rect x="{40 + i * (tile_w + gap)}" y="70" width="{tile_w}" height="118" rx="14" fill="{BG_2}" stroke="{LINE}"/>'
        f'<text class="tk" x="{60 + i * (tile_w + gap)}" y="102">{label}</text>'
        f'<text class="tv" x="{60 + i * (tile_w + gap)}" y="150">{escape(value)}</text>'
        f'<text class="ts" x="{60 + i * (tile_w + gap)}" y="174">{escape(sub)}</text></g>'
        for i, (label, value, sub) in enumerate(tiles)
    )

    # Lenguajes: barra apilada + leyenda en dos columnas
    langs = languages(year)
    bar, x = [], 40.0
    for i, (name, share, color) in enumerate(langs):
        seg = 600 * share
        bar.append(f'<rect class="seg" style="animation-delay:{0.4 + i * 0.12:.2f}s" x="{x:.1f}" y="262" width="{seg:.1f}" height="14" fill="{color}"/>')
        x += seg
    legend = "".join(
        f'<circle cx="{48 + (i % 2) * 300}" cy="{312 + (i // 2) * 34}" r="6" fill="{color}"/>'
        f'<text class="ln" x="{64 + (i % 2) * 300}" y="{317 + (i // 2) * 34}">{escape(name)}</text>'
        f'<text class="lp" x="{320 + (i % 2) * 300}" y="{317 + (i // 2) * 34}" text-anchor="end">{share * 100:.1f}%</text>'
        for i, (name, share, color) in enumerate(langs)
    )

    # Actividad por día de la semana
    week = weekday_totals(year)
    peak = max(week) or 1
    cols = []
    for i, count in enumerate(week):
        bh = 125 * count / peak
        cx = 730 + i * 62
        hot = count == peak
        cols.append(
            f'<rect x="{cx}" y="{410 - 125}" width="36" height="125" rx="6" fill="{BG_2}"/>'
            f'<rect class="col" style="animation-delay:{0.5 + i * 0.08:.2f}s" x="{cx}" y="{410 - bh:.1f}" width="36" height="{bh:.1f}" rx="6" fill="{MAGENTA if hot else "url(#vneon)"}"/>'
            f'<text class="wd" x="{cx + 18}" y="436" text-anchor="middle">{WEEKDAYS[i]}</text>'
            f'<text class="wc" x="{cx + 18}" y="{402 - bh:.1f}" text-anchor="middle">{fmt(count)}</text>'
        )

    style = f"""
.h {{ font: 700 13px {MONO}; fill: {MAGENTA}; letter-spacing: 4px; }}
.upd {{ font: 400 13px {MONO}; fill: {MUTED}; }}
.tk {{ font: 700 12px {MONO}; fill: {SOFT}; letter-spacing: 2px; }}
.tv {{ font: 800 40px {SANS}; fill: {TEXT}; }}
.ts {{ font: 400 13px {SANS}; fill: {MUTED}; }}
.ln {{ font: 600 15px {SANS}; fill: {TEXT}; }}
.lp {{ font: 500 14px {MONO}; fill: {MUTED}; }}
.wd {{ font: 700 12px {MONO}; fill: {SOFT}; letter-spacing: 1px; }}
.wc {{ font: 500 11px {MONO}; fill: {MUTED}; }}
.tile {{ opacity: 0; animation: rise .7s ease-out forwards; }}
@keyframes rise {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
.seg {{ transform-box: fill-box; transform-origin: left; transform: scaleX(0); animation: grow .9s ease-out forwards; }}
.col {{ transform-box: fill-box; transform-origin: bottom; transform: scaleY(0); animation: grow .9s cubic-bezier(.2,.8,.2,1) forwards; }}
@keyframes grow {{ to {{ transform: scale(1); }} }}
.live {{ animation: blink 1.2s steps(2, start) infinite; }}
@keyframes blink {{ to {{ visibility: hidden; }} }}
"""
    body = f"""<defs>{common_defs()}
<linearGradient id="vneon" x1="0" y1="1" x2="0" y2="0">
  <stop offset="0" stop-color="{CYAN}" stop-opacity="0.35"/><stop offset="1" stop-color="{CYAN}"/>
</linearGradient>
<clipPath id="barclip"><rect x="40" y="262" width="600" height="14" rx="7"/></clipPath>
</defs>
<rect width="{w}" height="{h}" rx="18" fill="url(#bg)"/>
<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="17" fill="none" stroke="{LINE}" stroke-width="2"/>
<circle class="live" cx="46" cy="43" r="5" fill="#22C55E"/>
<text class="h" x="60" y="48">PIT WALL · DATOS EN VIVO</text>
<text class="upd" x="{w - 40}" y="48" text-anchor="end">actualizado {today.isoformat()} UTC</text>
{tile_svg}
<text class="h" x="40" y="240">LENGUAJES · POR COMMITS</text>
<rect x="40" y="262" width="600" height="14" rx="7" fill="{BG_2}"/>
<g clip-path="url(#barclip)">{"".join(bar)}</g>
{legend}
<line x1="680" y1="226" x2="680" y2="440" stroke="{LINE}" stroke-width="2"/>
<text class="h" x="730" y="240">ACTIVIDAD POR DÍA</text>
{"".join(cols)}
"""
    total = coll["contributionCalendar"]["totalContributions"]
    return svg(w, h, body, style, f"Stats de GitHub: {total} contribuciones en los últimos 12 meses, racha actual {current} días, mejor racha {longest} días")


if __name__ == "__main__":
    year, days, today = fetch()
    (OUT / "pitwall.svg").write_text(build(year, days, today), encoding="utf-8")
    print("escrito", OUT / "pitwall.svg")
