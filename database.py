import sqlite3

def conectar():
    conn = sqlite3.connect("inventario.db")
    return conn

def crear_tabla():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            precio REAL NOT NULL
        )
    """)

    conn.commit()
    conn.close()