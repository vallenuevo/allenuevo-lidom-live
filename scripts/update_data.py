import requests, json, datetime, re
from bs4 import BeautifulSoup

DATA_DIR = "data"

def iso_now():
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def save_json(name, payload):
    with open(f"{DATA_DIR}/{name}", "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

print("🚀 Iniciando actualización...")

# ------------------ JUEGOS DEL DÍA (Flashscore) ------------------
# Más estable para jornada del día. Filtramos por fecha visible en la tarjeta.
try:
    url = "https://www.flashscore.com/baseball/dominican-republic/lidom/"
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0 Safari/537.36"}
    html = requests.get(url, headers=headers, timeout=40).text
    soup = BeautifulSoup(html, "lxml")

    today_games = []
    # Cada bloque de fecha -> lista de partidos
    today = datetime.date.today().strftime("%d %b")  # ej: "20 Oct"
    # Flashscore usa separadores de día con clase event__title--type
    for day in soup.select(".event__header, .event__title--type"):
        label = day.get_text(strip=True)
        container = day.find_next_sibling()
        if not container: 
            continue
        # Si el encabezado contiene el mes/día de hoy, tomamos sus matches siguientes
        if any(x in label for x in [today.split()[0], today.split()[1]]):
            for m in container.select(".event__match"):
                teams = [t.get_text(strip=True) for t in m.select(".event__participant")]
                scores = [s.get_text(strip=True) for s in m.select(".event__score")]
                state_el = m.select_one(".event__stage, .event__stage--block")
                state = state_el.get_text(strip=True) if state_el else "Próximo"
                score = "—"
                if len(scores) >= 2 and scores[0] and scores[1]:
                    score = f"{scores[0]} - {scores[1]}"
                if len(teams)==2:
                    today_games.append({
                        "Juego": f"{teams[0]} vs {teams[1]}",
                        "Estado": state,
                        "Marcador": score,
                        "Estadio": ""  # flashscore no siempre muestra estadio
                    })
            break  # encontramos el bloque de hoy; salimos

    save_json("games_live.json", {"updated": iso_now(), "games": today_games})
    print(f"✅ Juegos: {len(today_games)} encontrados para hoy")
except Exception as e:
    print("❌ Error juegos:", e)
    save_json("games_live.json", {"updated": iso_now(), "games": [], "error": str(e)})

# ------------------ POSICIONES (API oficial LIDOM) ------------------
try:
    lidom_api = "https://estadisticas.lidom.com/Api/TablaPosicion"
    headers = {
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept":"application/json, text/plain, */*",
        "Referer":"https://estadisticas.lidom.com/",
    }
    r = requests.get(lidom_api, headers=headers, timeout=40)
    r.raise_for_status()
    data = r.json()

    rows = []
    for it in data:
        rows.append({
            "Equipo": it.get("Equipo",""),
            "JJ": it.get("JJ",""),
            "G": it.get("G",""),
            "P": it.get("P",""),
            "PCT": it.get("PCT",""),
            "DIF": it.get("DIF",""),
            "Racha": it.get("Racha",""),
            "U10": it.get("U10","")
        })
    save_json("standings.json", {"updated": iso_now(), "rows": rows})
    print(f"✅ Posiciones: {len(rows)} equipos")
except Exception as e:
    print("❌ Error posiciones:", e)
    save_json("standings.json", {"updated": iso_now(), "rows": [], "error": str(e)})

# ------------------ CARICATURAS (WordPress feed) ------------------
# Lee las imágenes más recientes de la categoría Caricaturas de tu sitio.
try:
    feed = "https://vallenuevotv.com/category/caricaturas/feed/"
    xml = requests.get(feed, timeout=40, headers={"User-Agent":"Mozilla/5.0"}).text
    soup = BeautifulSoup(xml, "xml")  # parse RSS
    items = soup.select("item")[:8]
    imgs = []
    for it in items:
        content = it.find("content:encoded")
        if content and content.text:
            # busca primera imagen en el HTML del contenido
            img = re.search(r'src="([^"]+)"', content.text)
            if img:
                imgs.append({"title": it.title.text if it.title else "", "src": img.group(1)})
    save_json("caricaturas.json", {"updated": iso_now(), "items": imgs})
    print(f"✅ Caricaturas: {len(imgs)} imágenes")
except Exception as e:
    print("⚠️ Caricaturas no disponibles:", e)
    # deja el archivo si falla para no romper la app
    save_json("caricaturas.json", {"updated": iso_now(), "items": []})
    
# ------------------ VIDEOS (lista simple editable) ------------------
# Si quieres auto-YouTube luego, me pasas channel_id o playlist_id y lo automatizo.
try:
    # Si ya existe videos.json no lo sobrescribimos
    import os, json as _json
    path = f"{DATA_DIR}/videos.json"
    if not os.path.exists(path):
        default = {
          "updated": iso_now(),
          "videos": [
            {"id":"uEPPV8E04EE","title":"Miguel Sanó comanda a las Estrellas"},
            {"id":"7gDp0SRu1Yc","title":"Francisco Mejía guía triunfo del Licey"},
            {"id":"7m1jai13rVM","title":"Toros apabullan a las Águilas"},
            {"id":"g4jRYrr2XzA","title":"Estrellas dejan en el terreno a Leones"}
          ]
        }
        save_json("videos.json", default)
        print("✅ videos.json inicial creado")
    else:
        # sólo actualiza timestamp para que tu app muestre 'última actualización'
        with open(path,"r+",encoding="utf-8") as f:
            obj=_json.load(f)
            obj["updated"]=iso_now()
            f.seek(0); _json.dump(obj,f,ensure_ascii=False,indent=2); f.truncate()
        print("ℹ️ videos.json existente conservado")
except Exception as e:
    print("⚠️ No se pudo preparar videos.json:", e)

print("🏁 Listo")
