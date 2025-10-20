import requests, json, datetime, re
from bs4 import BeautifulSoup

def iso_now():
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def save_json(name, payload):
    with open(f"data/{name}", "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

print("🚀 Actualizando datos Valle Nuevo TV en Pelota...")

# ======================================================
# 🏟️ JUEGOS DEL DÍA - Fuente: Flashscore
# ======================================================
try:
    url = "https://www.flashscore.com/baseball/dominican-republic/lidom/"
    headers = {"User-Agent":"Mozilla/5.0"}
    html = requests.get(url, headers=headers, timeout=30).text
    soup = BeautifulSoup(html, "html.parser")

    games = []
    for g in soup.select(".event__match"):
        teams = [t.get_text(strip=True) for t in g.select(".event__participant")]
        scores = [s.get_text(strip=True) for s in g.select(".event__score")]
        status = g.select_one(".event__stage, .event__stage--block")
        state = status.get_text(strip=True) if status else "Próximo"
        if len(teams) == 2:
            games.append({
                "Juego": f"{teams[0]} vs {teams[1]}",
                "Estado": state,
                "Marcador": f"{scores[0]}-{scores[1]}" if len(scores) == 2 else "—",
                "Estadio": ""
            })

    save_json("games_live.json", {"updated": iso_now(), "games": games})
    print(f"✅ {len(games)} juegos cargados.")
except Exception as e:
    print("❌ Error en juegos:", e)
    save_json("games_live.json", {"updated": iso_now(), "games": []})


# ======================================================
# 📊 TABLA DE POSICIONES - Fuente: API oficial LIDOM
# ======================================================
try:
    lidom_api = "https://estadisticas.lidom.com/Api/TablaPosicion"
    data = requests.get(lidom_api, headers={"User-Agent":"Mozilla/5.0"}).json()

    rows = []
    for r in data:
        rows.append({
            "Equipo": r.get("Equipo", ""),
            "JJ": r.get("JJ", ""),
            "G": r.get("G", ""),
            "P": r.get("P", ""),
            "PCT": r.get("PCT", ""),
            "DIF": r.get("DIF", ""),
            "Racha": r.get("Racha", ""),
            "U10": r.get("U10", "")
        })
    save_json("standings.json", {"updated": iso_now(), "rows": rows})
    print("✅ Posiciones actualizadas.")
except Exception as e:
    print("❌ Error en posiciones:", e)
    save_json("standings.json", {"updated": iso_now(), "rows": []})


# ======================================================
# 📰 CARICATURAS - Fuente: RSS WordPress
# ======================================================
try:
    feed = "https://vallenuevotv.com/category/caricaturas/feed/"
    xml = requests.get(feed, headers={"User-Agent":"Mozilla/5.0"}).text
    soup = BeautifulSoup(xml, "xml")

    caricaturas = []
    for item in soup.find_all("item")[:8]:
        title = item.title.text
        content = item.find("content:encoded")
        if content:
            match = re.search(r'src="([^"]+)"', content.text)
            if match:
                caricaturas.append({"title": title, "src": match.group(1)})

    save_json("caricaturas.json", {"updated": iso_now(), "items": caricaturas})
    print(f"✅ {len(caricaturas)} caricaturas actualizadas.")
except Exception as e:
    print("❌ Error en caricaturas:", e)
    save_json("caricaturas.json", {"updated": iso_now(), "items": []})


# ======================================================
# 🎥 VIDEOS - Manual o JSON persistente
# ======================================================
try:
    with open("data/videos.json", "r", encoding="utf-8") as f:
        videos = json.load(f)
    videos["updated"] = iso_now()
    save_json("videos.json", videos)
    print("✅ Videos actualizados.")
except Exception as e:
    print("⚠️ No se encontró videos.json, creando base.")
    save_json("videos.json", {
        "updated": iso_now(),
        "videos": [
            {"id": "uEPPV8E04EE", "title": "Miguel Sanó comanda a las Estrellas"},
            {"id": "7gDp0SRu1Yc", "title": "Francisco Mejía guía triunfo del Licey"},
            {"id": "7m1jai13rVM", "title": "Toros apabullan a las Águilas"},
            {"id": "g4jRYrr2XzA", "title": "Estrellas dejan en el terreno a Leones"}
        ]
    })
