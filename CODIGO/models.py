import sqlite3
from werkzeug.security import generate_password_hash

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # Tabla de usuarios
    c.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            contraseña TEXT NOT NULL,
            rol TEXT CHECK(rol IN ('dueño','inquilino')) NOT NULL
        )
    ''')

    # Tabla de habitaciones
    c.execute('''
        CREATE TABLE IF NOT EXISTS habitaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            nombre TEXT,
            estado TEXT CHECK(estado IN ('on','off')) DEFAULT 'off',
            intensidad INTEGER DEFAULT 100,
            color TEXT DEFAULT 'white',
            modo TEXT CHECK(modo IN ('manual','automatico')) DEFAULT 'manual',
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id),
            UNIQUE(usuario_id, nombre)
        )
    ''')

    conn.commit()
    conn.close()

def create_user(usuario, contraseña, rol):
    """Crear usuario con contraseña hasheada"""
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    hashed_password = generate_password_hash(contraseña)
    c.execute("INSERT INTO usuarios (usuario, contraseña, rol) VALUES (?, ?, ?)",
              (usuario, hashed_password, rol))
    conn.commit()
    conn.close()
