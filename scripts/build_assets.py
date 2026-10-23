"""Genera los SVG animados del perfil (header, telemetría, proyectos, divisor, footer).

Uso: python scripts/build_assets.py  (desde la raíz del repo)
Editá los textos de PROJECTS / TELEMETRY y volvé a correrlo.
"""
import base64
import textwrap
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"

# Paleta compartida por todas las piezas
BG_1 = "#070B14"
BG_2 = "#0F172A"
CYAN = "#00E5FF"
MAGENTA = "#FF00AA"
SOFT = "#8BE9FD"
TEXT = "#E2E8F0"
MUTED = "#94A3B8"
LINE = "#1E293B"
RED = "#FF1E1E"

SANS = "'Segoe UI', Ubuntu, 'Helvetica Neue', Arial, sans-serif"
MONO = "'JetBrains Mono', 'SF Mono', Consolas, 'Liberation Mono', monospace"

# Sin animaciones para quien las tenga desactivadas en el sistema
REDUCED_MOTION = "@media (prefers-reduced-motion: reduce) { * { animation: none !important; } }"

PROJECTS = [
    {
        "slug": "skinstudio",
        "pos": "P1",
        "title": "Skin Studio",
        "kicker": "PROYECTO PARA CLIENTE · EN PRODUCCIÓN",
        "desc": (
            "Plataforma de turnos online para una clínica estética: carrito multi-turno, "
            "señas con MercadoPago, gift cards, recordatorios automáticos y una agenda "
            "admin sincronizada con Google Calendar."
        ),
        "stack": ["Django", "Django Ninja", "React", "PostgreSQL", "Redis", "Celery", "Docker"],
        "cta": "micaskin.com",
        "badge": "CÓDIGO PRIVADO",
        "featured": True,
    },
    {
        "slug": "mensajeria-omnicanal",
        "pos": "P2",
        "title": "Mensajería omnicanal",
        "kicker": "CONFIDENCIAL · BACKEND LEAD",
        "desc": "Multi-tenant sobre WhatsApp para retail: 45 cuentas en una sola instancia y +500.000 mensajes por mes.",
        "stack": ["Rails", "PostgreSQL", "Sidekiq", "WhatsApp API"],
        "cta": "VER CASO",
    },
    {
        "slug": "vps-multi-app",
        "pos": "P3",
        "title": "VPS multi-app",
        "kicker": "INFRAESTRUCTURA PROPIA",
        "desc": "Seis apps en producción en un solo servidor: un compose por app, Nginx central y bases sin puertos expuestos.",
        "stack": ["Docker", "Nginx", "GitHub Actions"],
        "cta": "VER CASO",
    },
    {
        "slug": "gaucho-weather",
        "pos": "P4",
        "title": "Gaucho Weather",
        "kicker": "AGRO · CLIMA",
        "desc": "Pronóstico y riesgo de heladas para el campo argentino, con alertas 48 h antes.",
        "stack": ["Python", "JavaScript", "Docker"],
        "cta": "VER REPO",
    },
    {
        "slug": "spree-recommendations",
        "pos": "P5",
        "title": "Spree Recommendations",
        "kicker": "E-COMMERCE · EXTENSIÓN",
        "desc": "Recomendaciones por historial de compras para Spree, sin N+1 y con jobs en segundo plano.",
        "stack": ["Rails", "Redis", "Sidekiq"],
        "cta": "VER REPO",
    },
    {
        "slug": "api-compras",
        "pos": "P6",
        "title": "API Compras",
        "kicker": "API REST",
        "desc": "API de compras con JWT, documentación Swagger/ReDoc y comprobantes automatizados.",
        "stack": ["Django", "DRF", "JWT"],
        "cta": "VER REPO",
    },
    {
        "slug": "token-bar",
        "pos": "P7",
        "title": "token-bar",
        "kicker": "DEV TOOLING",
        "desc": "Mod para Claude Code: barra de estado con uso del plan, modelo y estado del repo.",
        "stack": ["TypeScript"],
        "cta": "VER REPO",
    },
]

TELEMETRY = [
    ("BACKEND", "Django · Django Ninja · DRF · Rails", 0.95),
    ("DATA", "PostgreSQL · Redis · MySQL", 0.90),
    ("ASYNC", "Celery · Sidekiq · Webhooks", 0.85),
    ("INFRA", "Docker · Nginx · Caddy · GitHub Actions", 0.85),
    ("FRONTEND", "React · Next.js · TypeScript", 0.65),
]


def svg(width, height, body, style="", label=""):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(label)}">
<style>
{style}
{REDUCED_MOTION}
</style>
{body}
</svg>
"""


def common_defs():
    return f"""<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="{BG_1}"/><stop offset="1" stop-color="{BG_2}"/>
</linearGradient>
<linearGradient id="neon" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{CYAN}"/><stop offset="1" stop-color="{MAGENTA}"/>
</linearGradient>
<filter id="glow" x="-20%" y="-50%" width="140%" height="200%">
  <feGaussianBlur stdDeviation="6" result="b"/>
  <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>"""


def build_header():
    w, h = 1200, 420
    logo = base64.b64encode((OUT / "logo-160.png").read_bytes()).decode()

    # Semáforo de largada: se encienden de a uno y se apagan juntos ("lights out")
    cycle = 9
    pods, light_css = [], []
    for i in range(5):
        x = 260 + i * 58
        on = (0.5 + i * 0.55) / cycle * 100
        out = 3.8 / cycle * 100
        light_css.append(
            f"@keyframes l{i} {{ 0%, {on:.1f}% {{ fill: #2A0A0A; }} {on + 0.1:.1f}%, {out:.1f}% {{ fill: {RED}; }} {out + 0.1:.1f}%, 100% {{ fill: #2A0A0A; }} }}"
            f" .l{i} {{ animation: l{i} {cycle}s infinite; }}"
        )
        pods.append(
            f'<rect x="{x}" y="28" width="44" height="74" rx="10" fill="#05070D" stroke="{LINE}" stroke-width="2"/>'
            f'<circle cx="{x + 22}" cy="48" r="12" fill="#1A1A1A"/>'
            f'<circle class="l{i}" cx="{x + 22}" cy="80" r="12" fill="#2A0A0A"/>'
        )
    out_pct = 3.8 / cycle * 100

    # Frases que rotan debajo del nombre
    lines = [
        "Software Engineer · Backend Lead",
        "Backend e infraestructura en producción",
        "Django · Rails · PostgreSQL · Docker",
        "Lights out and away we go",
    ]
    step = 100 / len(lines)
    taglines = "".join(
        f'<text class="tag" style="animation-delay:{i * 3}s" x="258" y="252">{escape(t)}</text>' for i, t in enumerate(lines)
    )

    # Piso tipo pista con perspectiva
    vx, vy = 600, 300
    grid = "".join(
        f'<line x1="{vx}" y1="{vy}" x2="{x}" y2="{h}" stroke="{CYAN}" stroke-opacity="0.18"/>' for x in range(-1200, 2401, 150)
    )
    rows = "".join(
        f'<line x1="0" y1="{y}" x2="{w}" y2="{y}" stroke="{MAGENTA}" stroke-opacity="0.22"/>' for y in range(300, h + 40, 20)
    )

    streaks = "".join(
        f'<rect class="streak" style="animation-duration:{d}s;animation-delay:{dl}s" x="-400" y="{y}" width="{ln}" height="2" fill="url(#streak)"/>'
        for y, d, dl, ln in [(118, 1.6, 0, 320), (166, 2.3, 0.7, 220), (208, 1.9, 1.3, 380), (276, 2.6, 0.4, 260), (140, 2.1, 1.8, 180)]
    )

    style = f"""
{" ".join(light_css)}
.title {{ font: 800 64px {SANS}; letter-spacing: 2px; }}
.burst {{ animation: burst {cycle}s infinite; }}
@keyframes burst {{ 0%, {out_pct:.1f}% {{ opacity: 0.5; }} {out_pct + 1:.1f}% {{ opacity: 1; height: 6px; }} {out_pct + 12:.1f}%, 100% {{ opacity: 0.5; height: 3px; }} }}
.tag {{ font: 500 26px {SANS}; fill: {SOFT}; opacity: 0; animation: tag 12s infinite; }}
@keyframes tag {{ 0% {{ opacity: 0; transform: translateX(-12px); }} 3% {{ opacity: 1; transform: translateX(0); }} {step - 3:.0f}% {{ opacity: 1; }} {step:.0f}% {{ opacity: 0; }} 100% {{ opacity: 0; }} }}
.streak {{ animation: streak linear infinite; }}
@keyframes streak {{ from {{ transform: translateX(0); }} to {{ transform: translateX(1700px); }} }}
.rows {{ animation: rows 0.8s linear infinite; }}
@keyframes rows {{ from {{ transform: translateY(0); }} to {{ transform: translateY(20px); }} }}
.meta {{ font: 600 15px {MONO}; fill: {MUTED}; letter-spacing: 3px; }}
.ring {{ animation: spin 8s linear infinite; transform-origin: 140px 175px; }}
@keyframes spin {{ to {{ transform: rotate(360deg); }} }}
.label {{ font: 700 13px {MONO}; fill: {RED}; letter-spacing: 3px; }}
"""
    body = f"""<defs>
{common_defs()}
<linearGradient id="streak" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{CYAN}" stop-opacity="0"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0.8"/>
</linearGradient>
<linearGradient id="fade" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="{BG_1}" stop-opacity="1"/><stop offset="1" stop-color="{BG_1}" stop-opacity="0"/>
</linearGradient>
<clipPath id="floor"><rect x="0" y="300" width="{w}" height="{h - 300}"/></clipPath>
<clipPath id="logo"><circle cx="140" cy="175" r="70"/></clipPath>
</defs>
<rect width="{w}" height="{h}" rx="18" fill="url(#bg)"/>
<g clip-path="url(#floor)">
  {grid}
  <g class="rows">{rows}</g>
  <rect x="0" y="300" width="{w}" height="70" fill="url(#fade)"/>
</g>
<rect class="burst" x="0" y="298" width="{w}" height="3" fill="url(#neon)" filter="url(#glow)"/>
{streaks}
<g>{"".join(pods)}</g>
<text class="label" x="560" y="70">LIGHTS OUT</text>
<circle cx="140" cy="175" r="84" fill="none" stroke="url(#neon)" stroke-width="3" stroke-dasharray="40 14" class="ring"/>
<circle cx="140" cy="175" r="72" fill="{BG_1}" stroke="{LINE}" stroke-width="2"/>
<image href="data:image/png;base64,{logo}" x="70" y="105" width="140" height="140" clip-path="url(#logo)"/>
<g>
  <text class="title" x="256" y="190" fill="url(#neon)" filter="url(#glow)">GUILLERMO NATALI ULLA</text>
</g>
{taglines}
<text class="meta" x="40" y="400">ROSARIO · AR</text>
<text class="meta" x="{w - 40}" y="400" text-anchor="end">DRIVER CODE: NAT</text>
"""
    return svg(w, h, body, style, "Guillermo Natali Ulla — Software Engineer · Backend Lead")


def build_telemetry():
    w, h = 1200, 350
    rows = []
    for i, (name, detail, value) in enumerate(TELEMETRY):
        y = 96 + i * 50
        rows.append(
            f'<text class="k" x="560" y="{y}">{escape(name)}</text>'
            f'<text class="d" x="1160" y="{y}" text-anchor="end">{escape(detail)}</text>'
            f'<rect x="560" y="{y + 10}" width="600" height="8" rx="4" fill="{LINE}"/>'
            f'<rect class="bar" style="animation-delay:{0.3 + i * 0.25}s" x="560" y="{y + 10}" width="{600 * value:.0f}" height="8" rx="4" fill="url(#neon)"/>'
        )

    # Traza de velocidad que se dibuja en loop
    trace = "M40 330 C 90 330, 110 312, 150 314 S 210 336, 250 326 S 300 306, 340 310 S 400 334, 440 324 S 480 314, 500 316"

    style = f"""
.h {{ font: 700 13px {MONO}; fill: {MAGENTA}; letter-spacing: 4px; }}
.name {{ font: 800 34px {SANS}; fill: {TEXT}; }}
.code {{ font: 800 76px {MONO}; fill: url(#neon); }}
.k {{ font: 700 14px {MONO}; fill: {SOFT}; letter-spacing: 3px; }}
.d {{ font: 400 14px {MONO}; fill: {MUTED}; }}
.f {{ font: 400 16px {SANS}; fill: {TEXT}; }}
.fm {{ font: 400 15px {SANS}; fill: {MUTED}; }}
.bar {{ transform-box: fill-box; transform-origin: left; transform: scaleX(0); animation: fill 1.4s cubic-bezier(.2,.8,.2,1) forwards; }}
@keyframes fill {{ to {{ transform: scaleX(1); }} }}
.dot {{ animation: blink 1.2s steps(2, start) infinite; }}
@keyframes blink {{ to {{ visibility: hidden; }} }}
.trace {{ stroke-dasharray: 700; stroke-dashoffset: 700; animation: draw 4s ease-in-out infinite; }}
@keyframes draw {{ 0% {{ stroke-dashoffset: 700; }} 60%, 100% {{ stroke-dashoffset: 0; }} }}
"""
    body = f"""<defs>{common_defs()}</defs>
<rect width="{w}" height="{h}" rx="18" fill="url(#bg)"/>
<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="17" fill="none" stroke="{LINE}" stroke-width="2"/>
<text class="h" x="40" y="48">DRIVER PROFILE</text>
<text class="code" x="36" y="132">NAT</text>
<text class="name" x="40" y="176">Guillermo Natali Ulla</text>
<text class="f" x="40" y="210">Software Engineer · Backend Lead (remoto)</text>
<text class="fm" x="40" y="238">Ing. en Sistemas Informáticos · último año (UAI)</text>
<text class="fm" x="40" y="262">Téc. Sup. en Desarrollo de Software (ISBL, 2024)</text>
<circle class="dot" cx="46" cy="290" r="5" fill="#22C55E"/>
<text class="fm" x="58" y="295">En pista: abierto a sistemas a medida</text>
<path class="trace" d="{trace}" fill="none" stroke="url(#neon)" stroke-width="2" opacity="0.7"/>
<line x1="520" y1="40" x2="520" y2="310" stroke="{LINE}" stroke-width="2"/>
<text class="h" x="560" y="48">TELEMETRY</text>
{"".join(rows)}
"""
    return svg(w, h, body, style, "Perfil de Guillermo Natali Ulla y stack principal")


def build_project(p):
    featured = p.get("featured", False)
    w, h = (1200, 270) if featured else (590, 270)
    wrap = 118 if featured else 64
    desc_lines = textwrap.wrap(p["desc"], wrap)
    # Más de dos líneas pisan los chips de stack
    assert len(desc_lines) <= 2, f"descripción demasiado larga: {p['slug']}"

    chips, cx = [], 32
    for tech in p["stack"]:
        cw = len(tech) * 8.4 + 26
        chips.append(
            f'<rect x="{cx}" y="{h - 70}" width="{cw:.0f}" height="28" rx="14" fill="{BG_2}" stroke="{LINE}"/>'
            f'<text class="chip" x="{cx + cw / 2:.0f}" y="{h - 51}" text-anchor="middle">{escape(tech)}</text>'
        )
        cx += cw + 10

    desc = "".join(
        f'<text class="desc" x="32" y="{(150 if featured else 140) + i * 24}">{escape(line)}</text>' for i, line in enumerate(desc_lines)
    )
    badge = ""
    if p.get("badge"):
        bw = len(p["badge"]) * 8.6 + 28
        badge = (
            f'<rect x="{w - 32 - bw:.0f}" y="30" width="{bw:.0f}" height="28" rx="6" fill="none" stroke="{MAGENTA}"/>'
            f'<text class="badge" x="{w - 32 - bw / 2:.0f}" y="49" text-anchor="middle">{escape(p["badge"])}</text>'
        )

    style = f"""
.pos {{ font: 800 {44 if featured else 36}px {MONO}; fill: url(#neon); }}
.kick {{ font: 700 12px {MONO}; fill: {MAGENTA}; letter-spacing: 3px; }}
.title {{ font: 800 {38 if featured else 28}px {SANS}; fill: {TEXT}; }}
.desc {{ font: 400 {17 if featured else 15}px {SANS}; fill: {MUTED}; }}
.chip {{ font: 600 13px {MONO}; fill: {SOFT}; }}
.badge {{ font: 700 12px {MONO}; fill: {MAGENTA}; letter-spacing: 2px; }}
.link {{ font: 600 14px {MONO}; fill: {CYAN}; }}
.border {{ stroke-dasharray: 120 {2 * (w + h)}; animation: lap {6 if featured else 5}s linear infinite; }}
@keyframes lap {{ to {{ stroke-dashoffset: -{2 * (w + h) + 120}; }} }}
.sweep {{ animation: sweep 5s ease-in-out infinite; }}
@keyframes sweep {{ 0%, 60% {{ transform: translateX(-{w}px); }} 100% {{ transform: translateX({w}px); }} }}
"""
    title_y = 108 if featured else 100
    pos_w = 88 if featured else 72
    body = f"""<defs>{common_defs()}
<linearGradient id="shine" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="0.5" stop-color="#fff" stop-opacity="0.05"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
</linearGradient>
<clipPath id="card"><rect width="{w}" height="{h}" rx="18"/></clipPath>
</defs>
<rect width="{w}" height="{h}" rx="18" fill="url(#bg)"/>
<g clip-path="url(#card)"><rect class="sweep" x="0" y="0" width="{w // 2}" height="{h}" fill="url(#shine)"/></g>
<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="17" fill="none" stroke="{LINE}" stroke-width="2"/>
<rect class="border" x="1" y="1" width="{w - 2}" height="{h - 2}" rx="17" fill="none" stroke="url(#neon)" stroke-width="3" filter="url(#glow)"/>
<text class="kick" x="32" y="50">{escape(p["kicker"])}</text>
<text class="pos" x="32" y="{title_y}">{p["pos"]}</text>
<text class="title" x="{32 + pos_w}" y="{title_y}">{escape(p["title"])}</text>
{badge}
{desc}
{"".join(chips)}
<text class="link" x="{w - 32}" y="{h - 51 if featured else 50}" text-anchor="end">{escape(p["cta"])} →</text>
"""
    return svg(w, h, body, style, f'{p["title"]}: {p["desc"]}')


def build_divider():
    w, h = 1200, 24
    style = f"""
.pulse {{ animation: pulse 3.5s ease-in-out infinite; }}
@keyframes pulse {{ from {{ transform: translateX(-200px); }} to {{ transform: translateX({w}px); }} }}
"""
    body = f"""<defs>{common_defs()}
<linearGradient id="p" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{MAGENTA}" stop-opacity="0"/><stop offset="0.5" stop-color="{MAGENTA}"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/>
</linearGradient></defs>
<rect x="0" y="11" width="{w}" height="2" fill="{LINE}"/>
<rect class="pulse" x="0" y="10" width="200" height="4" rx="2" fill="url(#p)" filter="url(#glow)"/>
"""
    return svg(w, h, body, style, "")


def build_footer():
    w, h = 1200, 150
    sq = 15
    checks = "".join(
        f'<rect x="{x * sq}" y="{y * sq}" width="{sq}" height="{sq}" fill="{TEXT}"/>'
        for y in range(2) for x in range(0, (w + 2 * sq) // sq + 2) if (x + y) % 2 == 0
    )
    style = f"""
.flag {{ animation: flag 1.2s linear infinite; }}
@keyframes flag {{ to {{ transform: translateX(-{2 * sq}px); }} }}
.big {{ font: 800 30px {SANS}; }}
.small {{ font: 500 15px {MONO}; fill: {MUTED}; letter-spacing: 3px; }}
"""
    body = f"""<defs>{common_defs()}<clipPath id="c"><rect width="{w}" height="{h}" rx="18"/></clipPath></defs>
<g clip-path="url(#c)">
<rect width="{w}" height="{h}" fill="url(#bg)"/>
<g class="flag" opacity="0.9">{checks}</g>
<text class="big" x="{w / 2}" y="88" text-anchor="middle" fill="url(#neon)" filter="url(#glow)">Gracias por pasar por el pit lane</text>
<text class="small" x="{w / 2}" y="122" text-anchor="middle">NOS VEMOS EN LA PRÓXIMA VUELTA · BOX, BOX</text>
</g>
"""
    return svg(w, h, body, style, "Gracias por pasar por el pit lane")


if __name__ == "__main__":
    files = {
        "header.svg": build_header(),
        "telemetry.svg": build_telemetry(),
        "divider.svg": build_divider(),
        "footer.svg": build_footer(),
    }
    for p in PROJECTS:
        files[f"projects/{p['slug']}.svg"] = build_project(p)
    for name, content in files.items():
        (OUT / name).write_text(content, encoding="utf-8")
        print("escrito", OUT / name)
