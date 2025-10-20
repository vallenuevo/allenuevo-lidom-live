import requests, json, datetime
from bs4 import BeautifulSoup

# ---------------- FUNCIONES BASE ----------------

def now():
    """Devuelve la hora actual en formato ISO (UTC)."""
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat()

def save_json(path, content):
    """Guarda un archivo JSON con codificación UTF-8."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False, indent=2)

# ---------------- JUEGOS EN VIVO (FLASH SCORE) ----------------

def fetch_games():
    url = "https://www.flashscore.com/baseball/dominican-republic/lidom/"
    print("🔄 Cargando juegos desde FlashScore...")
    try:
        html = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).text
        soup = BeautifulSoup(html, "html.parser")

        games = []
        for m in soup.select(".event__match"):
            teams = [t.text for t in m.select(".event__participant")]
            scores = [s.text for s in m.select(".event__score")]
            state = m.select_one(".event__stage--block")
            if len(teams) == 2:
                games.append({
                    "title": f"{teams[0]} vs {teams[1]}",
                    "state": state.text if state else "Próximo",
                    "score": f"{scores[0]} - {scores[1]}" if scores else "—"
                })

        data = {"updated": now(), "games": games}
        save_json("data/games_live.json", data)
        print(f"✅ Juegos actualizados correctamente: {len(games)} encontrados.")
    except Exception as e:
        print("❌ Error al cargar juegos:", e)

# ---------------- TABLA DE POSICIONES (LIDOM OFICIAL) ----------------

def fetch_standings():
    url = "https://estadisticas.lidom.com/TablaPosicion"
    print("🔄 Cargando tabla desde LIDOM.com...")
    try:
        html = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).text
        soup = BeautifulSoup(html, "html.parser")

        rows = []
        for tr in soup.select("table tbody tr"):
            cols = [td.get_text(strip=True) for td in tr.select("td")]
            if len(cols) >= 8:
                rows.append({
                    "Equipo": cols[0],
                    "JJ": cols[1],
                    "G": cols[2],
                    "P": cols[3],
                    "PCT": cols[4],
                    "DIF": cols[5],
                    "Racha": cols[6],
                    "U10": cols[7],
                })

        data = {"updated": now(), "rows": rows}
        save_json("data/standings.json", data)
        print(f"✅ Tabla de posiciones actualizada: {len(rows)} equipos encontrados.")
    except Exception as e:
        print("❌ Error al cargar tabla:", e)

# ---------------- PROCESO PRINCIPAL ----------------

if __name__ == "__main__":
    print("🏁 Iniciando actualización automática de datos LIDOM...")
    fetch_games()
    fetch_standings()
    print("🚀 Actualización completada correctamente.")
