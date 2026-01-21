import feedparser
import sqlite3
import time
from datetime import datetime
from time import mktime

# --- CONFIGURACIÓN: FUENTES DE ALTA CALIDAD (VERIFICADAS 2026) ---
rss_sources = [
    {"name": "BleepingComputer", "url": "https://www.bleepingcomputer.com/feed/"},
    {"name": "The Hacker News", "url": "https://feeds.feedburner.com/TheHackersNews"},
    {"name": "Dark Reading", "url": "https://www.darkreading.com/rss.xml"},
    {"name": "Security Week", "url": "https://www.securityweek.com/feed/"},
    {"name": "The Record", "url": "https://therecord.media/feed"}
]

# --- CONFIGURACIÓN DE BASE DE DATOS ---
DB_NAME = "ciber_inteligencia.db"

def setup_database():
    """Crea la tabla si no existe. Usamos 'link' como llave primaria para evitar duplicados."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS noticias (
            link TEXT PRIMARY KEY,
            title TEXT,
            source TEXT,
            published_date TEXT,
            summary TEXT,
            ai_processed BOOLEAN DEFAULT 0,
            ai_summary TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print(f"[SISTEMA] Base de datos '{DB_NAME}' verificada/creada.")

def es_reciente(entry, dias=3):
    """Filtra noticias más viejas de X días."""
    try:
        if hasattr(entry, 'published_parsed'):
            fecha_publicacion = datetime.fromtimestamp(mktime(entry.published_parsed))
            delta = datetime.now() - fecha_publicacion
            return delta.days <= dias
        return True # Si no tiene fecha, asumimos reciente por seguridad, luego filtramos.
    except:
        return False

def guardar_noticia(entry, source_name):
    """Intenta guardar la noticia en SQLite. Retorna True si es nueva, False si ya existía."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    try:
        # Preparamos datos
        title = entry.title
        link = entry.link
        summary = entry.get('summary', '')
        
        # Intentamos obtener fecha legible
        published = "N/A"
        if hasattr(entry, 'published'):
            published = entry.published
            
        # INSERT OR IGNORE: La magia de SQL para deduplicar automáticamente
        cursor.execute('''
            INSERT INTO noticias (link, title, source, published_date, summary)
            VALUES (?, ?, ?, ?, ?)
        ''', (link, title, source_name, published, summary))
        
        rows = cursor.rowcount
        conn.commit()
        return rows > 0 # Retorna 1 si se insertó, 0 si ya existía (duplicado)
        
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def ejecutar_ciclo_ingesta():
    print(f"\n--- INICIANDO CICLO DE INGESTA: {datetime.now()} ---")
    setup_database()
    
    total_nuevas = 0
    total_procesadas = 0
    
    for source in rss_sources:
        print(f"📡 Leyendo: {source['name']}...")
        try:
            feed = feedparser.parse(source['url'])
            
            for entry in feed.entries:
                total_procesadas += 1
                
                # 1. Filtro de Tiempo
                if not es_reciente(entry):
                    continue
                
                # 2. Guardado en DB (El filtro de duplicados ocurre aquí dentro)
                es_nueva = guardar_noticia(entry, source['name'])
                
                if es_nueva:
                    print(f"   [NUEVA] {entry.title[:50]}...")
                    total_nuevas += 1
                # Si no es nueva, no imprimimos nada para mantener limpio el log
                    
        except Exception as e:
            print(f"   [ERROR] Falló la fuente {source['name']}: {e}")

    print(f"-" * 50)
    print(f"RESUMEN FASE 1: {total_procesadas} analizadas. {total_nuevas} NUEVAS guardadas en DB.")
    print(f"Base de datos lista en: {DB_NAME}")

if __name__ == "__main__":
    ejecutar_ciclo_ingesta()