import sqlite3
from werkzeug.security import generate_password_hash

# Conectamos a la base de datos
conn = sqlite3.connect('database.db')
c = conn.cursor()

# Datos del dueño
usuario = 'Equipo'
contraseña = 'admin124'
rol = 'dueño'


# Insertamos el usuario
c.execute("INSERT INTO usuarios (usuario, contraseña, rol) VALUES (?, ?, ?)",
          (usuario, contraseña, rol))

conn.commit()
conn.close()

print("Usuario dueño creado correctamente")
