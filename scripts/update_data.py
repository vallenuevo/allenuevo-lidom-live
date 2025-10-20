import requests, json, datetime
from bs4 import BeautifulSoup

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ---- JUEGOS EN VIVO (pendiente a integrar) ----
try:
    print("🕹️ Cargando datos de juegos (placeholder temporal)...")
    games = {
        "updated": datetime.datetime.utcnow().isoformat(),
        "games": [
            {"title": "Esperando API LIDOM", "state": "Pendiente", "score": "—"}
        ]
    }
    save_json("data/games_live.json", games)
except Exception as e:
    print("❌ Error al guardar juegos:", e)

# ---- TABLA DE POSICIONES (fuente oficial LIDOM JSON) ----
try:
    url = "https://estadisticas.lidom.com/Api/TablaPosicion"
    print("📊 Obteniendo tabla de posiciones desde API:", url)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0 Safari/537.36",
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
    print(f"✅ Tabla actualizada correctamente: {len(rows)} equipos")

except Exception as e:
    print("❌ Error al obtener posiciones desde API:", e)
