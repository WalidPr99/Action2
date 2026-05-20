import requests
import xml.etree.ElementTree as ET
from datetime import datetime

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; BarcelonaNewsBot/1.0)"}

FEEDS = {
    "ciudad": "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/seccion/espana/catalunya/portada",
    "deportes": "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/seccion/deportes/portada",
}

KEYWORDS_BARCA = {"barcelona", "barça", "barca", "blaugrana", "culé", "cule"}


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


def imprimir_seccion(titulo_seccion, noticias):
    print(f"\n{'='*60}")
    print(f"  {titulo_seccion}")
    print(f"{'='*60}")
    if not noticias:
        print("  Sin noticias encontradas.")
        return
    for i, (titulo, link) in enumerate(noticias, 1):
        print(f"\n  {i}. {titulo}")
        if link:
            print(f"     🔗 {link}")


def main():
    print(f"\n🗞️  NOTICIAS DE BARCELONA — El País")
    print(f"   Generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

    # Noticias de la ciudad (feed Cataluña completo, sin filtro)
    items_ciudad = obtener_items_rss(FEEDS["ciudad"])
    noticias_ciudad = [extraer_titulo_y_link(i) for i in items_ciudad if extraer_titulo_y_link(i)[0]]

    # Noticias del Barça (feed Deportes filtrado por keywords)
    items_deportes = obtener_items_rss(FEEDS["deportes"])
    noticias_barca = []
    for item in items_deportes:
        titulo, link = extraer_titulo_y_link(item)
        descripcion = item.findtext("description", "")
        if titulo and contiene_barcelona(titulo, descripcion):
            noticias_barca.append((titulo, link))

    imprimir_seccion("🏙️  CIUDAD DE BARCELONA / CATALUÑA", noticias_ciudad)
    imprimir_seccion("⚽  FC BARCELONA", noticias_barca)

    total = len(noticias_ciudad) + len(noticias_barca)
    print(f"\n{'='*60}")
    print(f"  ✅ Total: {len(noticias_ciudad)} noticias de ciudad · {len(noticias_barca)} del Barça")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
