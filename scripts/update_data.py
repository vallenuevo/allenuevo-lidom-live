import requests, json, datetime
from bs4 import BeautifulSoup

def now():
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat()

def save_json(path, content):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False, indent=2)

# ---- JUEGOS LIDOM ----
try:
    fs_url = "https://www.flashscore.com/baseball/dominican-republic/lidom/"
    fs_html = requests.get(fs_url, headers={'User-Agent': 'Mozilla/5.0'}).text
    soup = BeautifulSoup(fs_html, "html.parser")

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
    games_data = {"updated": now(), "games": games}
    save_json("data/games_live.json", games_data)
    print("✅ Juegos actualizados:", len(games))
except Exception as e:
    print("Error al cargar juegos:", e)

# ---- TABLA DE POSICIONES ----
try:
    lidom_url = "https://lidom.com/estadisticas/posiciones.html"
    lidom_html = requests.get(lidom_url, headers={'User-Agent': 'Mozilla/5.0'}).text
    soup = BeautifulSoup(lidom_html, "html.parser")
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
    standings = {"updated": now(), "rows": rows}
    save_json("data/standings.json", standings)
    print("✅ Tabla de posiciones actualizada:", len(rows), "equipos")
except Exception as e:
    print("Error al cargar tabla:", e)
