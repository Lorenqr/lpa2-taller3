"""
Script para añadir 5 usuarios y 10 canciones a musica.db.
Ejecución: python seed_db.py
"""

import sqlite3
from datetime import datetime, timezone
from passlib.context import CryptContext

DB_PATH = "musica.db"

# Configurar bcrypt para hashear contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Usuarios con contraseña (requerido para autenticación)
usuarios = [
    ("Ana Perez", "ana.perez@example.com", pwd_context.hash("password123"), "usuario", 1),
    ("Carlos Ruiz", "carlos.ruiz@example.com", pwd_context.hash("password123"), "usuario", 1),
    ("Maria Gomez", "maria.gomez@example.com", pwd_context.hash("password123"), "usuario", 1),
    ("Jorge Herrera", "jorge.herrera@example.com", pwd_context.hash("password123"), "usuario", 1),
    ("Lucia Torres", "lucia.torres@example.com", pwd_context.hash("password123"), "usuario", 1),
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

    # Insertar usuarios con contraseña, rol y activo
    usuarios_vals = [(u[0], u[1], datetime.now(timezone.utc).isoformat(), u[2], u[3], u[4]) for u in usuarios]
    try:
        insert_if_not_exists(
            conn,
            "usuarios",
            "correo",
            usuarios_vals,
            ["nombre", "correo", "fecha_registro", "contraseña_hash", "rol", "activo"],
        )
        print(f"✓ Usuarios insertados: {len(usuarios)}")
        print("  Contraseña por defecto: password123")
    except Exception as e:
        print(f"✗ Error insertando usuarios: {e}")

    # Insertar canciones
    canciones_vals = [
        (c[0], c[1], c[2], c[3], c[4], c[5], datetime.now(timezone.utc).isoformat())
        for c in canciones
    ]
    try:
        insert_if_not_exists(
            conn,
            "canciones",
            "titulo",
            canciones_vals,
            [
                "titulo",
                "artista",
                "album",
                "duracion",
                "año",
                "genero",
                "fecha_creacion",
            ],
        )
        print(f"✓ Canciones insertadas: {len(canciones)}")
    except Exception as e:
        print(f"✗ Error insertando canciones: {e}")

    # Verificar totales
    cur.execute("SELECT COUNT(*) FROM usuarios")
    total_usuarios = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM canciones")
    total_canciones = cur.fetchone()[0]

    conn.close()
    print("\n📊 Totales en la base de datos:")
    print(f"   - Usuarios: {total_usuarios}")
    print(f"   - Canciones: {total_canciones}")
    print(
        "\n✅ Seed completo. Puedes verificar con: sqlite3 musica.db 'SELECT * FROM usuarios;'"
    )


if __name__ == "__main__":
    main()
