
import datetime
from pathlib import Path
import json
import os

# Static on-this-day programming/events. Add more as you like!
EVENTS = {
  "01-01": ["1970: Comienza la **Unix Epoch** (00:00:00 UTC)."],
  "02-20": ["1991: **Guido van Rossum** anuncia la primera versión pública de **Python**."],
  "08-12": ["1981: IBM presenta la **IBM PC 5150**."],
  "09-09": ["1947: Se documenta el primer 'bug' de computador (polilla en el Mark II)."],
  "10-29": ["1969: Se envía el primer mensaje entre computadoras ARPANET (precursor de Internet)."],
  "02-01": ["2004: Se lanza **Facebook** (TheFacebook) en Harvard."],
  "04-30": ["1993: CERN libera el **World Wide Web** al dominio público."],
  "05-23": ["1995: **MySQL** es lanzado por primera vez."],
  "10-05": ["2011: Fallece **Steve Jobs**, cofundador de Apple."],
  "12-03": ["1992: Se envía el primer **SMS** (‘Merry Christmas’)."]
}

def today_key():
    # Use UTC to align with GitHub Actions schedule
    today = datetime.datetime.utcnow().date()
    return today.strftime("%m-%d")

def build_block():
    key = today_key()
    items = EVENTS.get(key, [])
    if not items:
        return f"No hay eventos cargados para hoy ({key}). ¡Agrega más en scripts/update_efemerides.py!"
    return "\n".join([f"- {it}" for it in items])

def replace_block(md: str, new_block: str) -> str:
    start = "<!--EFEMERIDES_START-->"
    end = "<!--EFEMERIDES_END-->"
    i = md.find(start)
    j = md.find(end)
    if i == -1 or j == -1:
        return md
    return md[: i + len(start)] + "\n" + new_block + "\n" + md[j:]

if __name__ == "__main__":
    readme_path = Path("README.md")
    md = readme_path.read_text(encoding="utf-8")
    new_md = replace_block(md, build_block())
    readme_path.write_text(new_md, encoding="utf-8")
    print("README actualizado con efemérides para", today_key())
