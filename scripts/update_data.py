import requests, json, datetime
from bs4 import BeautifulSoup

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

print("🚀 Iniciando actualización de datos LIDOM...")

# ---- JUEGOS DEL DÍA (API oficial) ----
try:
    games_url = "https://estadisticas.lidom.com/Api/Juegos"
    print("🎯 Consultando juegos desde:", games_url)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://estadisticas.lidom.com/",
    }

    res = requests.get(games_url, headers=headers, timeout=30)
    res.raise_for_status()
    data = res.json()

    today = datetime.date.today().strftime("%Y-%m-%d")
    games_today = []

    for g in data:
        if g.get("Fecha", "").startswith(today):
            games_today.append({
                "Juego": f"{g.get('VisitanteNombre', '')} vs {g.get('HomeClubNombre', '')}",
                "Estado": g.get("EstadoJuego', '')",
                "Marcador": f"{g.get('CarrerasVisitante', 0)} - {g.get('CarrerasHomeClub', 0)}",
                "Estadio": g.get("EstadioNombre", "")
            })

    games = {
        "updated": datetime.datetime.utcnow().isoformat(),
        "games": games_today
    }

    save_json("data/games_live.json", games)
    print(f"✅ Juegos actualizados correctamente: {len(games_today)} encontrados")

except Exception as e:
    print("❌ Error al obtener juegos:", e)
    save_json("data/games_live.json", {
        "updated": datetime.datetime.utcnow().isoformat(),
        "games": [],
        "error": str(e)
    })

# ---- TABLA DE POSICIONES (API oficial) ----
try:
    url = "https://estadisticas.lidom.com/Api/TablaPosicion"
    print("📊 Consultando tabla de posiciones desde:", url)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://estadisticas.lidom.com/",
    }

    res = requests.get(url, headers=headers, timeout=30)
    res.raise_for_status()
    data = res.json()

    rows = []
    for item in data:
        rows.append({
            "Equipo": item.get("Equipo", ""),
            "JJ": item.get("JJ", ""),
            "G": item.get("G", ""),
            "P": item.get("P", ""),
            "PCT": item.get("PCT", ""),
            "DIF": item.get("DIF", ""),
            "Racha": item.get("Racha", ""),
            "U10": item.get("U10", "")
        })

    standings = {"updated": datetime.datetime.utcnow().isoformat(), "rows": rows}
    save_json("data/standings.json", standings)
    print(f"✅ Tabla de posiciones actualizada correctamente: {len(rows)} equipos")

except Exception as e:
    print("❌ Error al obtener posiciones:", e)
    save_json("data/standings.json", {
        "updated": datetime.datetime.utcnow().isoformat(),
        "rows": [],
        "error": str(e)
    })

print("🏁 Proceso finalizado correctamente.")
