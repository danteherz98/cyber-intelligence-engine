import sqlite3

DB_NAME = "ciber_inteligencia.db"

def generar_reporte():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Seleccionamos todo lo procesado
    cursor.execute("SELECT * FROM noticias WHERE ai_processed = 1")
    rows = cursor.fetchall()
    
    print(f"\n--- REPORTE DE INTELIGENCIA PRELIMINAR ---")
    print(f"Noticias procesadas: {len(rows)}")
    print("=" * 60)
    
    contador_valioso = 0
    
    for row in rows:
        ai_text = row['ai_summary']
        title = row['title']
        link = row['link']
        
        # Filtramos visualmente: Si la IA dijo "DESCARTAR", no lo mostramos
        if "DESCARTAR" in ai_text:
            continue
            
        # Si pasó el filtro, lo mostramos bonito
        contador_valioso += 1
        print(f"🔴 AMENAZA DETECTADA (Link: {link})")
        print(f"TITULO ORIGINAL: {title}")
        print("-" * 20)
        print(f"{ai_text}") # Aquí sale el resumen de la IA
        print("=" * 60)
        print("\n")

    if contador_valioso == 0:
        print("Resultado: La IA descartó todo. (Ojo: Revisa si el prompt fue muy estricto o las noticias eran malas).")
    else:
        print(f"✅ Se encontraron {contador_valioso} noticias dignas de ser vendidas.")

    conn.close()

if __name__ == "__main__":
    generar_reporte()