import requests, json, re
from bs4 import BeautifulSoup
from datetime import datetime

URL_STANDINGS = "https://www.flashscore.com/baseball/dominican-republic/lidom/#/YgwOVy35/standings/overall/"
URL_LIVE = "https://www.flashscore.com/baseball/dominican-republic/lidom/"

def scrape_standings():
    print("📊 Obteniendo standings...")
    html = requests.get(URL_STANDINGS, headers={"User-Agent":"Mozilla/5.0"}).text
    soup = BeautifulSoup(html, "lxml")
    teams, rows = [], []

    for row in soup.select("div.table__row--static"):
        cols = [c.text.strip() for c in row.select("div.table__cell")]
        if len(cols) >= 8:
            rows.append({
                "Equipo": cols[1],
                "JJ": cols[2],
                "G": cols[3],
                "P": cols[4],
                "PCT": cols[5],
                "DIF": cols[6],
                "Racha": cols[7],
                "U10": cols[8] if len(cols) > 8 else ""
            })
    with open("data/standings.json", "w", encoding="utf-8") as f:
        json.dump({"updated": datetime.utcnow().isoformat(), "rows": rows}, f, indent=2, ensure_ascii=False)
    print(f"✅ {len(rows)} equipos guardados.")


def scrape_games():
    print("⚾ Obteniendo juegos...")
    html = requests.get(URL_LIVE, headers={"User-Agent":"Mozilla/5.0"}).text
    soup = BeautifulSoup(html, "lxml")
    games = []

    for match in soup.select("div.event__match"):
        teams = [t.text.strip() for t in match.select("div.event__participant")]
        scores = [s.text.strip() for s in match.select("div.event__scores")]
        state = match.select_one("div.event__stage--block")
        state = state.text.strip() if state else "Programado"

        if len(teams) == 2:
            score = " - ".join(scores) if scores else "-"
            games.append({
                "title": f"{teams[0]} vs {teams[1]}",
                "state": state,
                "score": score,
                "play_by_play": [f"{teams[0]} y {teams[1]} en {state}"]
            })

    with open("data/games_live.json", "w", encoding="utf-8") as f:
        json.dump({"updated": datetime.utcnow().isoformat(), "games": games}, f, indent=2, ensure_ascii=False)
    print(f"✅ {len(games)} juegos guardados.")


if __name__ == "__main__":
    scrape_standings()
    scrape_games()
