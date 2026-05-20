import requests
import xml.etree.ElementTree as ET
from datetime import datetime

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; BarcelonaNewsBot/1.0)"}

FEEDS = {
    "ciudad": [
        "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/espana/portada",
        "https://elpais.com/rss/elpais/portada_completo.xml",
    ],
    "deportes": "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/deportes/portada",
}

KEYWORDS_CIUDAD = {"barcelona", "cataluña", "catalunya", "catalán", "catalan"}

KEYWORDS_BARCA = {"barcelona", "barça", "barca", "blaugrana", "culé", "cule"}
FICHERO_SALIDA = "noticias_barcelona.md"


def obtener_items_rss(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        r.raise_for_status()
        root = ET.fromstring(r.content)
        return root.findall(".//item")
    except Exception as e:
        print(f"  ❌ Error al obtener feed: {e}")
        return []


def extraer_titulo_y_link(item):
    titulo = item.findtext("title", "").strip()
    link = item.findtext("link", "").strip()
    return titulo, link


def contiene_barcelona(titulo, descripcion=""):
    texto = (titulo + " " + descripcion).lower()
    return any(kw in texto for kw in KEYWORDS_BARCA)


def construir_seccion_md(titulo_seccion, noticias):
    lineas = [f"\n## {titulo_seccion}\n"]
    if not noticias:
        lineas.append("_Sin noticias encontradas._\n")
    else:
        for titulo, link in noticias:
            if link:
                lineas.append(f"- [{titulo}]({link})")
            else:
                lineas.append(f"- {titulo}")
    return "\n".join(lineas)


def main():
    ahora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print(f"\n🗞️  NOTICIAS DE BARCELONA — El País")
    print(f"   Generado: {ahora}\n")

    noticias_ciudad = []
    vistos = set()
    for feed_url in FEEDS["ciudad"]:
        for item in obtener_items_rss(feed_url):
            titulo, link = extraer_titulo_y_link(item)
            descripcion = item.findtext("description", "")
            if titulo and link not in vistos and any(kw in (titulo + " " + descripcion).lower() for kw in KEYWORDS_CIUDAD):
                noticias_ciudad.append((titulo, link))
                vistos.add(link)

    items_deportes = obtener_items_rss(FEEDS["deportes"])
    noticias_barca = []
    for item in items_deportes:
        titulo, link = extraer_titulo_y_link(item)
        descripcion = item.findtext("description", "")
        if titulo and contiene_barcelona(titulo, descripcion):
            noticias_barca.append((titulo, link))

    # Construir markdown
    contenido_md = f"# 🗞️ Noticias de Barcelona — El País\n\n> Actualizado: {ahora}\n"
    contenido_md += construir_seccion_md("🏙️ Ciudad de Barcelona / Cataluña", noticias_ciudad)
    contenido_md += "\n"
    contenido_md += construir_seccion_md("⚽ FC Barcelona", noticias_barca)
    contenido_md += f"\n\n---\n_Total: {len(noticias_ciudad)} noticias de ciudad · {len(noticias_barca)} del Barça_\n"

    with open(FICHERO_SALIDA, "w", encoding="utf-8") as f:
        f.write(contenido_md)

    print(contenido_md)
    print(f"✅ Fichero guardado: {FICHERO_SALIDA}")


if __name__ == "__main__":
    main()
