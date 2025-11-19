"""
Script para añadir 5 usuarios y 10 canciones a musica.db.
Ejecución: python seed_db.py
"""
import sqlite3
from datetime import datetime
from passlib.context import CryptContext

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
DB_PATH = "musica.db"

usuarios = [
    ("Ana Perez", "ana.perez@example.com", "pass1234"),
    ("Carlos Ruiz", "carlos.ruiz@example.com", "pass1234"),
    ("Maria Gomez", "maria.gomez@example.com", "pass1234"),
    ("Jorge Herrera", "jorge.herrera@example.com", "pass1234"),
    ("Lucia Torres", "lucia.torres@example.com", "pass1234"),
]

canciones = [
    ("Cancion 1", "Artista A", "Album X", 210, 2018, "Pop"),
    ("Cancion 2", "Artista B", "Album Y", 185, 2019, "Rock"),
    ("Cancion 3", "Artista A", "Album Z", 240, 2020, "Pop"),
    ("Cancion 4", "Artista C", "Album X", 200, 2017, "Jazz"),
    ("Cancion 5", "Artista D", "Album W", 230, 2015, "Clasica"),
    ("Cancion 6", "Artista E", "Album V", 195, 2021, "Rock"),
    ("Cancion 7", "Artista F", "Album U", 205, 2016, "Pop"),
    ("Cancion 8", "Artista G", "Album T", 180, 2022, "Electronic"),
    ("Cancion 9", "Artista H", "Album S", 260, 2014, "Metal"),
    ("Cancion 10", "Artista I", "Album R", 175, 2023, "Indie"),
]

def insert_if_not_exists(conn, table, unique_col, values, cols):
    cur = conn.cursor()
    placeholders = ",".join("?" for _ in cols)
    for v in values:
        unique_value = v[cols.index(unique_col)]
        cur.execute(f"SELECT id FROM {table} WHERE {unique_col} = ?", (unique_value,))
        if cur.fetchone() is None:
            cur.execute(
                f"INSERT INTO {table} ({','.join(cols)}) VALUES ({placeholders})", v
            )
    conn.commit()

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Ajusta nombres de columnas según tu esquema real si difieren
    usuarios_vals = [(u[0], u[1], datetime.utcnow().isoformat(), pwd.hash(u[2])) for u in usuarios]
    try:
        insert_if_not_exists(conn, "usuarios", "correo", usuarios_vals, ["nombre", "correo", "fecha_registro", "hashed_password"])
    except Exception as e:
        print("Error insertando usuarios:", e)

    canciones_vals = [(c[0], c[1], c[2], c[3], c[4], c[5], datetime.utcnow().isoformat()) for c in canciones]
    try:
        insert_if_not_exists(conn, "canciones", "titulo", canciones_vals, ["titulo", "artista", "album", "duracion", "anio", "genero", "fecha_creacion"])
    except Exception as e:
        print("Error insertando canciones:", e)

    conn.close()
    print("Seed completo. Revisa la base de datos con DBeaver o sqlite3.")

if __name__ == "__main__":
    main()