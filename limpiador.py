import sqlite3

DB_NAME = "ciber_inteligencia.db"

def resetear_errores():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Buscamos filas que contengan el error de API y las reseteamos
    cursor.execute('''
        UPDATE noticias 
        SET ai_processed = 0, ai_summary = NULL 
        WHERE ai_summary LIKE '%Error API%'
    ''')
    
    filas_afectadas = cursor.rowcount
    conn.commit()
    conn.close()
    
    print(f"✅ Se han reseteado {filas_afectadas} noticias con errores.")
    print("Ahora están listas para ser procesadas de nuevo correctamente.")

if __name__ == "__main__":
    resetear_errores()