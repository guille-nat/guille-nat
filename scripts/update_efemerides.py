import datetime
from pathlib import Path

# Static on-this-day programming/events. Add more as you like!
EVENTS = {
    "01-01": ["1970: Comienza la **Unix Epoch** (00:00:00 UTC), el punto de referencia temporal para sistemas operativos tipo Unix."],
    "01-09": ["2007: Steve Jobs presenta el **iPhone** en la Macworld de San Francisco."],
    "01-15": ["2001: Se lanza **Wikipedia**, la enciclopedia libre construida de forma colaborativa."],
    "01-24": ["1984: Apple lanza la **Macintosh**, el primer ordenador personal con una interfaz gráfica de usuario (GUI) exitosa."],
    "02-04": ["2004: Mark Zuckerberg lanza **TheFacebook** desde su dormitorio en Harvard."],
    "02-15": ["1946: Se presenta públicamente la **ENIAC**, una de las primeras computadoras electrónicas de propósito general."],
    "02-20": ["1991: **Guido van Rossum** publica la primera versión de **Python** (0.9.0) en alt.sources."],
    "03-12": ["1989: **Tim Berners-Lee** presenta su propuesta para un sistema de gestión de información, sentando las bases de la **World Wide Web**."],
    "03-15": ["1985: Se registra **symbolics.com**, el primer dominio `.com` de la historia."],
    "03-24": ["2001: Apple lanza **Mac OS X 10.0**, basado en un núcleo Unix (Darwin)."],
    "03-25": ["1995: Ward Cunningham publica **WikiWikiWeb**, la primera wiki."],
    "04-03": ["1973: Martin Cooper (Motorola) realiza la primera llamada desde un **teléfono móvil**."],
    "04-04": ["1975: **Microsoft** es fundado por Bill Gates y Paul Allen."],
    "04-07": ["2005: **Git** pasa a gestionar su propio código fuente, pocos días después de que Linus Torvalds empezara a escribirlo."],
    "04-10": ["2008: Se lanza oficialmente **GitHub**."],
    "04-30": ["1993: El **CERN** libera el código del **World Wide Web** al dominio público, permitiendo su libre uso y crecimiento."],
    "05-11": ["1997: **Deep Blue** (IBM) le gana un match de ajedrez a Garry Kasparov, campeón mundial."],
    "05-22": ["1980: Namco lanza **Pac-Man** en Japón."],
    "05-23": ["1995: **MySQL** es lanzado por primera vez. Se convierte en una de las bases de datos de código abierto más populares."],
    "06-08": ["1978: Intel lanza el **8086**, origen de la arquitectura x86."],
    "06-15": ["1976: Se lanza el **Apple II**, un ordenador que tuvo un gran éxito en el mercado doméstico."],
    "06-23": ["1912: Nace **Alan Turing**, padre de la computación teórica y la inteligencia artificial."],
    "07-01": ["1998: Nace la **Mozilla Foundation**, organización que promueve la apertura, innovación y oportunidad en la Web."],
    "07-05": ["1994: Jeff Bezos funda **Amazon**, que empezó como una librería online."],
    "07-20": ["1969: El **Apollo 11** llega a la Luna guiado por el Apollo Guidance Computer, cuyo software lideró Margaret Hamilton."],
    "08-06": ["1991: Tim Berners-Lee hace pública la **World Wide Web** y publica el primer sitio web."],
    "08-12": ["1981: IBM presenta la **IBM PC 5150**, un hito en la estandarización de los ordenadores personales."],
    "08-24": ["1995: Microsoft lanza **Windows 95**, que estrena el menú Inicio y la barra de tareas."],
    "08-25": ["1991: **Linus Torvalds** anuncia en comp.os.minix que está escribiendo un sistema operativo libre: nace **Linux**."],
    "09-04": ["1998: Larry Page y Sergey Brin fundan **Google**."],
    "09-09": ["1947: Se documenta el primer 'bug' real de computador por Grace Hopper: una polilla (moth) en el relé del Mark II. El término 'debugging' se populariza."],
    "09-17": ["1991: Linus Torvalds sube la versión **0.01 de Linux** a un servidor FTP."],
    "09-27": ["1983: **Richard Stallman** anuncia el proyecto **GNU**."],
    "10-29": ["1969: Se envía el primer mensaje entre dos computadoras en **ARPANET**, el precursor de Internet."],
    "11-15": ["1971: Intel anuncia el **4004**, el primer microprocesador comercial."],
    "11-20": ["1985: Microsoft lanza **Windows 1.0**."],
    "12-04": ["1995: Netscape y Sun anuncian **JavaScript**, el lenguaje que terminaría dominando la web."],
    "12-09": [
        "1906: Nace **Grace Hopper**, pionera de los compiladores y madre de COBOL.",
        "1968: **Douglas Engelbart** realiza la 'Madre de Todas las Demos', presentando el ratón, la interfaz gráfica de usuario y el hipertexto.",
    ],
    "12-10": ["1815: Nace **Ada Lovelace**, autora del primer algoritmo pensado para una máquina."],
}

def today_key():
    # Use UTC to align with GitHub Actions schedule
    today = datetime.datetime.now(datetime.timezone.utc).date()
    return today.strftime("%m-%d")

def format_items(items):
    return "\n".join([f"- {it}" for it in items])

def build_block():
    key = today_key()
    items = EVENTS.get(key, [])

    if items:
        return f"**Un día como hoy ({key}):**\n{format_items(items)}"

    # Si no hay eventos para hoy, buscamos el más cercano en el pasado.
    # Las claves "MM-DD" ordenan bien como texto; si no hay ninguna anterior
    # en el año (ej. 01-05), damos la vuelta y usamos la última del año.
    previous = [k for k in sorted(EVENTS) if k < key]
    closest = previous[-1] if previous else max(EVENTS)

    message = f"No hay efemérides para hoy ({key}). La más cercana es del **{closest}**:"
    return f"{message}\n{format_items(EVENTS[closest])}"

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
