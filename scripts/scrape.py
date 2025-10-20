import json, datetime, requests
from lxml import html

def now():
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat()

def save(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

# --- Juegos (ejemplo placeholder; cámbialo por tu fuente real) ---
# Aquí puedes scrapear Flashscore o tu fuente preferida.
games = {
  "updated": now(),
  "games": [
    # Rellena con scraping o API real:
    # {"title": "Licey vs Águilas", "state": "Próximo", "score": "—"}
  ]
}
save("data/games_live.json", games)

# --- Posiciones desde LIDOM (ejemplo mínima estructura a rellenar) ---
# Puedes hacer requests.get("https://lidom.com/estadisticas/posiciones.html")
# y parsear la tabla con lxml. Aquí dejamos un esqueleto:
rows = [
  # {"Equipo":"...", "JJ":0, "G":0, "P":0, "PCT":".000", "DIF":"—", "Racha":"", "U10":""}
]
standings = {"updated": now(), "rows": rows}
save("data/standings.json", standings)
