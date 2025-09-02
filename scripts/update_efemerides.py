import datetime
from pathlib import Path
import json
import os

# Static on-this-day programming/events. Add more as you like!
EVENTS = {
    "01-01": ["1970: Comienza la **Unix Epoch** (00:00:00 UTC), el punto de referencia temporal para sistemas operativos tipo Unix."],
    "01-24": ["1984: Apple lanza la **Macintosh**, el primer ordenador personal con una interfaz gráfica de usuario (GUI) exitosa."],
    "02-20": ["1991: **Guido van Rossum** anuncia la primera versión pública de **Python**, un lenguaje de programación de alto nivel."],
    "03-12": ["1989: **Tim Berners-Lee** presenta su propuesta para un sistema de gestión de información, sentando las bases de la **World Wide Web**."],
    "04-04": ["1975: **Microsoft** es fundado por Bill Gates y Paul Allen."],
    "04-30": ["1993: El **CERN** libera el código del **World Wide Web** al dominio público, permitiendo su libre uso y crecimiento."],
    "05-23": ["1995: **MySQL** es lanzado por primera vez. Se convierte en una de las bases de datos de código abierto más populares."],
    "06-15": ["1976: Se lanza el **Apple II**, un ordenador que tuvo un gran éxito en el mercado doméstico."],
    "07-01": ["1998: Nace la **Mozilla Foundation**, organización que promueve la apertura, innovación y oportunidad en la Web."],
    "08-12": ["1981: IBM presenta la **IBM PC 5150**, un hito en la estandarización de los ordenadores personales."],
    "09-09": ["1947: Se documenta el primer 'bug' real de computador por Grace Hopper: una polilla (moth) en el relé del Mark II. El término 'debugging' se populariza."],
    "10-29": ["1969: Se envía el primer mensaje entre dos computadoras en **ARPANET**, el precursor de Internet."],
    "12-09": ["1968: **Douglas Engelbart** realiza la 'Madre de Todas las Demos', presentando el ratón, la interfaz gráfica de usuario y el hipertexto."],
    "12-11": ["1995: Se lanza el lenguaje de programación **JavaScript** para Netscape Navigator."]
}

def today_key():
    # Use UTC to align with GitHub Actions schedule
    today = datetime.datetime.utcnow().date()
    return today.strftime("%m-%d")

def build_block():
    key = today_key()
    items = EVENTS.get(key, [])
    
    if items:
        return "\n".join([f"- {it}" for it in items])
    else:
        # Si no hay eventos para hoy, buscamos el más cercano en el pasado
        today_date = datetime.datetime.strptime(key, "%m-%d").date().replace(year=2000)
        
        sorted_keys = sorted(EVENTS.keys())
        
        # Encontramos la efeméride anterior más cercana
        closest_event_date = None
        closest_event_items = []
        
        for event_key in reversed(sorted_keys):
            event_date = datetime.datetime.strptime(event_key, "%m-%d").date().replace(year=2000)
            if event_date < today_date:
                closest_event_date = event_key
                closest_event_items = EVENTS[event_key]
                break

        if closest_event_items:
            message = f"No hay efemérides para el día de hoy ({key}). La efeméride anterior más cercana es del **{closest_event_date}**:"
            items_text = "\n".join([f"- {it}" for it in closest_event_items])
            return f"{message}\n{items_text}"
        else:
            # Si no se encuentra ninguna efeméride anterior (ej. si el día es 01-01)
            return f"No hay efemérides para el día de hoy ({key})."

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
    if not readme_path.is_file():
        # Crear un archivo README.md dummy si no existe
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write("\n")
    
    md = readme_path.read_text(encoding="utf-8")
    new_md = replace_block(md, build_block())
    readme_path.write_text(new_md, encoding="utf-8")
    print("README actualizado con efemérides para", today_key())