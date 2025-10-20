# ---- TABLA DE POSICIONES (LIDOM OFICIAL 2025) ----
try:
    lidom_url = "https://estadisticas.lidom.com/TablaPosicion"
    print("🔄 Cargando tabla desde estadisticas.lidom.com...")
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
    print("✅ Tabla de posiciones actualizada correctamente:", len(rows), "equipos")
except Exception as e:
    print("❌ Error al cargar tabla:", e)
