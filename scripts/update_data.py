import requests, json, datetime, re, sys
from bs4 import BeautifulSoup

# ---------------- Utilidades ----------------
def now():
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat()

def save_json(path, content):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False, indent=2)

def log_head(title, text, n=300):
    print(f"\n--- {title} (primeros {n} chars) ---")
    print(text[:n].replace("\n"," ") + " ...")
    print("--- fin ---\n")

# ---------------- JUEGOS (FlashScore) ----------------
def fetch_games():
    url = "https://www.flashscore.com/baseball/dominican-republic/lidom/"
    print("🔄 Cargando juegos desde:", url)
    try:
        html = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=30).text
        log_head("HTML FlashScore recibido", html)

        soup = BeautifulSoup(html, "html.parser")
        games = []
        for m in soup.select(".event__match"):
            teams = [t.get_text(strip=True) for t in m.select(".event__participant")]
            scores = [s.get_text(strip=True) for s in m.select(".event__score")]
            state_el = m.select_one(".event__stage--block")
            if len(teams) == 2:
                games.append({
                    "title": f"{teams[0]} vs {teams[1]}",
                    "state": state_el.get_text(strip=True) if state_el else "Próximo",
                    "score": f"{scores[0]} - {scores[1]}" if len(scores) == 2 else "—"
                })

        data = {"updated": now(), "games": games}
        save_json("data/games_live.json", data)
        print(f"✅ Juegos actualizados: {len(games)} encontrados")
        if games:
            print("   Ejemplo:", games[0])
    except Exception as e:
        print("❌ Error al cargar juegos:", repr(e))

# ---------------- POSICIONES (LIDOM OFICIAL) ----------------
def fetch_standings():
    # ¡IMPORTANTE! Usar SIEMPRE estadisticas.lidom.com (no lidom.com/estadisticas)
    url = "https://estadisticas.lidom.com/TablaPosicion"
    print("🔄 Cargando posiciones desde:", url)
    try:
        resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=30)
        html = resp.text
        log_head("HTML LIDOM recibido", html)

        soup = BeautifulSoup(html, "html.parser")
        table = soup.select_one("table")
        if not table:
            raise RuntimeError("No se encontró <table> en la página de posiciones")

        rows = []
        for tr in table.select("tbody tr"):
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

        # Validaciones útiles
        if not rows:
            raise RuntimeError("La tabla se parseó pero no devolvió filas")
        # Si JJ luce sospechoso (p. ej. 11 cuando apenas van 4), avisamos en logs
        try:
            jj_vals = [int(re.sub(r"\D", "", r["JJ"])) for r in rows if re.sub(r"\D","",r["JJ"])]
            if jj_vals:
                max_jj = max(jj_vals)
                print(f"ℹ️ JJ máximos detectados: {max_jj}")
        except Exception as _:
            pass

        data = {"updated": now(), "rows": rows}
        save_json("data/standings.json", data)
        print(f"✅ Posiciones actualizadas: {len(rows)} equipos")
        print("   Primera fila:", rows[0])
    except Exception as e:
        print("❌ Error al cargar posiciones:", repr(e))
        # Para no dejar datos viejos sin aviso, escribimos un JSON con error
        fallback = {
            "updated": now(),
            "rows": [],
            "error": f"Fallo al scrapear {url}: {repr(e)}"
        }
        save_json("data/standings.json", fallback)

# ---------------- Main ----------------
if __name__ == "__main__":
    print("🏁 Iniciando actualización automática LIDOM")
    fetch_games()
    fetch_standings()
    print("🚀 Finalizado")
