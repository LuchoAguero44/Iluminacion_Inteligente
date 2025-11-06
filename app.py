# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import subprocess
import modoauto
import time

app = Flask(__name__)
app.secret_key = 'clave_super_secreta_para_sesiones'

# ------------------- DB -------------------
def get_db():
    """Conexión SQLite segura"""
    conn = sqlite3.connect('database.db', check_same_thread=False, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

def ejecutar_query(query, params=(), fetch=False):
    """Ejecuta query y cierra conexión automáticamente"""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(query, params)
        if fetch:
            return cur.fetchall()
        conn.commit()

# ------------------- IR -------------------
def enviar_ir(comando):
    """Envía comando IR con LIRC"""
    try:
        subprocess.run(["irsend", "SEND_ONCE", "CONTROL_INT", comando], check=True)
        print(f"[IR] Enviado: {comando}")
    except subprocess.CalledProcessError:
        print(f"[IR] Error: {comando}")

def enviar_automatico():
    """Enciende + blanco al activar modo automático"""
    enviar_ir("KEY_POWER")
    time.sleep(0.5)
    enviar_ir("KEY_WHITE")

# ------------------- LOGS -------------------
def registrar_intento_login(usuario, exito):
    """Registra intento de login"""
    ip = request.remote_addr
    tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
    exito_val = 1 if exito else 0
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO logs_acceso (usuario, exito, tiempo, ip) VALUES (?, ?, ?, ?)",
            (usuario, exito_val, tiempo, ip)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[ERROR LOG] {e}")

# ------------------- HOME -------------------
@app.route('/')
def home():
    print(f"[DEBUG HOME] Sesión: {dict(session)}")  # ← VERÁS EL ROL
    if 'usuario' in session:
        if session.get('rol') == 'dueño':
            return redirect(url_for('panel_dueño'))
        else:
            return redirect(url_for('panel_inquilino'))
    return redirect(url_for('login'))

# ------------------- LOGIN -------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contraseña = request.form['contraseña']

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM usuarios WHERE usuario = ? AND contraseña = ?",
            (usuario, contraseña)
        ).fetchone()
        conn.close()

        if user:
            # → CONVIERTE sqlite3.Row A dict (SERIALIZABLE)
            user_dict = dict(user)
            
            # → LIMPIA Y GUARDA SESIÓN
            session.clear()
            session['usuario_id'] = user_dict['id']
            session['usuario'] = user_dict['usuario']
            session['nombre'] = user_dict.get('nombre') or user_dict['usuario']
            session['rol'] = user_dict.get('rol', 'inquilino')  # ← ¡AHORA SÍ!

            print(f"[LOGIN] Usuario: {usuario}, Rol: {session['rol']}, Sesión: {dict(session)}")

            registrar_intento_login(usuario, exito=True)
            flash("Login exitoso", "success")

            if session['rol'] == 'dueño':
                return redirect(url_for('panel_dueño'))
            else:
                return redirect(url_for('panel_inquilino'))
        else:
            registrar_intento_login(usuario, exito=False)
            flash("Usuario o contraseña incorrectos", "danger")

    return render_template('login.html')

# ------------------- LOGOUT -------------------
@app.route('/logout')
def logout():
    session.clear()
    flash("Sesión cerrada", "info")
    return redirect(url_for('login'))

# ------------------- PANEL INQUILINO -------------------
@app.route('/inquilino')
def panel_inquilino():
    if 'usuario' not in session or session.get('rol') != 'inquilino':
        flash("Acceso denegado", "danger")
        return redirect(url_for('login'))

    habitaciones = ejecutar_query(
        "SELECT * FROM habitaciones WHERE usuario_id = ?",
        (session['usuario_id'],), fetch=True
    )
    return render_template('index_inquilino.html', habitaciones=habitaciones)

# ------------------- PANEL DUEÑO -------------------
@app.route('/dueño')
def panel_dueño():
    if 'usuario' not in session or session.get('rol') != 'dueño':
        flash("Acceso denegado", "danger")
        return redirect(url_for('login'))

    inquilinos = ejecutar_query("SELECT * FROM usuarios WHERE rol = 'inquilino'", fetch=True)
    return render_template('index_dueño.html', inquilinos=inquilinos)

# ------------------- HABITACIÓN -------------------
@app.route('/habitacion/<int:habitacion_id>')
def habitacion(habitacion_id):
    if 'usuario' not in session:
        return redirect(url_for('login'))

    habitacion = ejecutar_query("SELECT * FROM habitaciones WHERE id = ?", (habitacion_id,), fetch=True)
    if not habitacion:
        flash("Habitación no encontrada", "danger")
        return redirect(url_for('panel_inquilino'))

    estado_auto = "Modo automático activado" if habitacion[0]['modo'] == 'automatico' else None
    return render_template('habitacion.html', habitacion=habitacion[0], numero=habitacion_id, estado_auto=estado_auto)

# ------------------- CONTROL LUCES -------------------
@app.route('/cambiar_luz/<int:habitacion_id>', methods=['POST'])
def cambiar_luz(habitacion_id):
    if 'usuario' not in session:
        return redirect(url_for('login'))

    accion = request.form.get('accion')
    conn = get_db()
    habitacion = conn.execute("SELECT * FROM habitaciones WHERE id = ?", (habitacion_id,)).fetchone()
    if not habitacion:
        conn.close()
        return redirect(url_for('panel_inquilino'))

    if accion == "toggle":
        nuevo_estado = 'on' if habitacion['estado'] == 'off' else 'off'
        comando = "KEY_POWER" if nuevo_estado == 'on' else "KEY_OFF"
        enviar_ir(comando)
        conn.execute("UPDATE habitaciones SET estado = ? WHERE id = ?", (nuevo_estado, habitacion_id))

    conn.commit()
    conn.close()
    return redirect(url_for('habitacion', habitacion_id=habitacion_id))

# ------------------- CAMBIAR MODO -------------------
@app.route('/cambiar_modo/<int:habitacion_id>', methods=['POST'])
def cambiar_modo(habitacion_id):
    conn = get_db()
    habitacion = conn.execute("SELECT * FROM habitaciones WHERE id = ?", (habitacion_id,)).fetchone()
    if not habitacion:
        conn.close()
        return redirect(url_for('panel_inquilino'))

    nuevo_modo = "automatico" if habitacion['modo'] != "automatico" else "manual"
    conn.execute("UPDATE habitaciones SET modo = ? WHERE id = ?", (nuevo_modo, habitacion_id))
    conn.commit()

    if nuevo_modo == "automatico":
        modoauto.activar_modo_automatico(habitacion_id)

    flash(f"Modo automático {'activado' if nuevo_modo == 'automatico' else 'desactivado'}", "success")
    conn.close()
    return redirect(url_for('habitacion', habitacion_id=habitacion_id))

# ------------------- CAMBIAR COLOR -------------------
@app.route('/cambiar_color/<int:habitacion_id>', methods=['POST'])
def cambiar_color(habitacion_id):
    color = request.form.get('color')
    ejecutar_query("UPDATE habitaciones SET color = ? WHERE id = ?", (color, habitacion_id))
    
    comandos = {
        "RED": "KEY_RED", "GREEN": "KEY_GREEN", "BLUE": "KEY_BLUE", "WHITE": "KEY_WHITE",
        "YELLOW": "KEY_YELLOW", "CYAN": "KEY_CYAN", "MAGENTA": "KEY_MAGENTA", "ORANGE": "KEY_ORANGE",
        "LIME": "KEY_LIME", "TURQUOISE": "KEY_TURQUOISE", "PURPLE": "KEY_PURPLE", "GOLD": "KEY_MUSTARD",
        "AQUAMARINE": "KEY_AQUAMARINE", "VIOLET": "KEY_VIOLET", "NAVY": "KEY_NAVY",
    }
    enviar_ir(comandos.get(color, "KEY_WHITE"))
    return redirect(url_for('habitacion', habitacion_id=habitacion_id))

# ------------------- INTENSIDAD -------------------
@app.route('/cambiar_intensidad/<int:habitacion_id>', methods=['POST'])
def cambiar_intensidad(habitacion_id):
    if 'usuario' not in session:
        return redirect(url_for('login'))

    accion = request.form.get('accion')
    habitacion = ejecutar_query("SELECT intensidad FROM habitaciones WHERE id = ?", (habitacion_id,), fetch=True)
    if not habitacion:
        return redirect(url_for('panel_inquilino'))

    intensidad = habitacion[0]['intensidad']
    if accion == 'subir':
        intensidad = min(100, intensidad + 10)
        enviar_ir("KEY_UP")
    elif accion == 'bajar':
        intensidad = max(0, intensidad - 10)
        enviar_ir("KEY_DOWN")

    ejecutar_query("UPDATE habitaciones SET intensidad = ? WHERE id = ?", (intensidad, habitacion_id))
    return redirect(url_for('habitacion', habitacion_id=habitacion_id))

# ------------------- PISO INQUILINO -------------------
@app.route('/piso/<int:inquilino_id>')
def piso_inquilino(inquilino_id):
    if session.get('rol') != 'dueño':
        return redirect(url_for('login'))

    habitaciones = ejecutar_query("SELECT * FROM habitaciones WHERE usuario_id = ?", (inquilino_id,), fetch=True)
    if not habitaciones:
        flash("Sin habitaciones", "info")
        return redirect(url_for('panel_dueño'))

    return render_template('piso_inquilino.html', habitaciones=habitaciones)

# ------------------- CREAR INQUILINO -------------------
@app.route('/crear_inquilino', methods=['GET', 'POST'])
def crear_inquilino():
    if session.get('rol') != 'dueño':
        return redirect(url_for('login'))

    if request.method == 'POST':
        usuario = request.form['usuario']
        contraseña = request.form['contraseña']

        if ejecutar_query("SELECT id FROM usuarios WHERE usuario = ?", (usuario,), fetch=True):
            flash("Usuario ya existe", "danger")
            return redirect(url_for('crear_inquilino'))

        ejecutar_query("INSERT INTO usuarios (usuario, contraseña, rol) VALUES (?, ?, 'inquilino')", (usuario, contraseña))
        usuario_id = ejecutar_query("SELECT id FROM usuarios WHERE usuario = ?", (usuario,), fetch=True)[0]['id']

        for nombre in ['Sala', 'Cocina', 'Dormitorio', 'Baño']:
            ejecutar_query(
                "INSERT INTO habitaciones (usuario_id, nombre, estado, modo, color, intensidad) VALUES (?, ?, 'off', 'manual', 'white', 100)",
                (usuario_id, nombre)
            )

        flash("Inquilino creado", "success")
        return redirect(url_for('panel_dueño'))

    return render_template('crear_inquilino.html')

# ------------------- RUN -------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)