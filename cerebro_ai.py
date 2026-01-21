import sqlite3
from google import genai
import time
import re

# --- CONFIGURACIÓN ---
API_KEY = "AIzaSyAOQwZOq7k4nIJvlZoe7jlRDzaWg15EIVw" 
DB_NAME = "ciber_inteligencia.db"

client = genai.Client(api_key=API_KEY)

def limpiar_texto(texto):
    if not texto: return "Sin detalles."
    return re.sub('<[^<]+?>', '', texto).strip()

def get_unprocessed_news():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM noticias WHERE ai_processed = 0 LIMIT 5")
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_news_with_ai(link, ai_summary, relevance_score):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE noticias 
        SET ai_summary = ?, ai_processed = 1
        WHERE link = ?
    ''', (f"SCORE: {relevance_score}\n\n{ai_summary}", link))
    conn.commit()
    conn.close()

def analyze_with_gemini(title, summary):
    summary_clean = limpiar_texto(summary)
    
    prompt = f"""
    Analyze this cybersecurity news item.
    Title: {title}
    Summary: {summary_clean}

    Task:
    1. Score RELEVANCE (0-10) for a Critical Threat Intelligence Report.
    2. If Score < 6, return ONLY: "DESCARTAR"
    3. If Score >= 6, provide analysis in English:
       - Headline
       - Threat
       - Impact

    Output Format:
    SCORE: [Number]
    ANALISIS: [Text]
    """
    
    try:
        # VOLVEMOS AL MODELO QUE SÍ EXISTE EN TU LISTA
        response = client.models.generate_content(
            model='gemini-2.0-flash', 
            contents=prompt
        )
        return response.text
    except Exception as e:
        # Si falla por cuota, devolvemos un código especial
        error_msg = str(e)
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            return "ERROR_QUOTA"
        print(f"     ❌ Error técnico: {e}")
        return "ERROR_API"

def run_brain_cycle():
    news = get_unprocessed_news()
    
    if not news:
        print("✅ No hay noticias pendientes.")
        return

    print(f"🧠 Iniciando análisis con Gemini 2.0 Flash (Modo Lento 30s)...")
    
    for item in news:
        print(f"   > Analizando: {item['title'][:30]}...")
        
        ai_result = analyze_with_gemini(item['title'], item['summary'])
        
        # MANEJO DE ERROR DE CUOTA (429)
        if ai_result == "ERROR_QUOTA":
            print("🚨 Límite de Google alcanzado. Esperando 60 segundos extra...")
            time.sleep(60)
            # No guardamos nada, el ciclo siguiente reintentará esta noticia
            continue
            
        if ai_result == "ERROR_API":
            print("     Falló. Saltando...")
            time.sleep(5)
            continue

        # PROCESAMIENTO EXITOSO
        if "SCORE:" in ai_result:
            print(f"     Status: OK")
            try:
                score = int(ai_result.split("SCORE:")[1].split("\n")[0].strip())
            except:
                score = 0
            update_news_with_ai(item['link'], ai_result, score)
        else:
            print(f"     Status: {ai_result[:30]}...")
            update_news_with_ai(item['link'], ai_result, 0)
        
        # PAUSA OBLIGATORIA PARA EVITAR EL ERROR 429
        # El error anterior pedía 24s. Damos 30s para asegurar.
        print("     💤 Enfriando motor (30s)...")
        time.sleep(30)

    print("🏁 Ciclo completado.")

if __name__ == "__main__":
    run_brain_cycle()