# modoauto.py
import time
import RPi.GPIO as GPIO
import board
import busio
import adafruit_tsl2561
import threading
import sqlite3

# IMPORTAMOS SOLO ir_control.py → SIN CIRCULAR IMPORT
from ir_control import encender, apagar


# ==================== BASE DE DATOS ====================
def registrar_sensor(tipo, habitacion_id, valor):
    """Registra un evento de sensor en la tabla 'sensores'"""
    try:
        conexion = sqlite3.connect("database.db")
        cursor = conexion.cursor()
        tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO sensores (tipo, habitacion_id, valor, tiempo) VALUES (?, ?, ?, ?)",
            (tipo, habitacion_id, float(valor), tiempo)
        )
        conexion.commit()
        conexion.close()
    except Exception as e:
        print(f"[ERROR DB] No se pudo registrar sensor: {e}")


# ==================== CONSULTA MODO ====================
def obtener_modo_desde_db(id_habitacion):
    try:
        conexion = sqlite3.connect("database.db")
        cursor = conexion.cursor()
        cursor.execute("SELECT modo FROM habitaciones WHERE id = ?;", (id_habitacion,))
        resultado = cursor.fetchone()
        conexion.close()
        return resultado[0] if resultado else "manual"
    except Exception as e:
        print(f"Error DB: {e}")
        return "manual"


# ==================== MODO AUTOMÁTICO ====================
def ejecutar_modo_automatico(id_habitacion):
    print(f"\nINICIANDO MODO AUTOMÁTICO - Habitación {id_habitacion}")

    # === GPIO ===
    try:
        GPIO.setmode(GPIO.BCM)
        PIN_PIR = 27
        GPIO.setup(PIN_PIR, GPIO.IN)
        print("GPIO configurado (PIR en GPIO 27)")
    except Exception as e:
        print(f"ERROR GPIO: {e}")
        return

    # === Sensor de luz ===
    sensor_luz = None
    usar_sensor_luz = True
    try:
        print("Inicializando I2C y TSL2561...")
        i2c = busio.I2C(board.SCL, board.SDA)
        sensor_luz = adafruit_tsl2561.TSL2561(i2c)
        sensor_luz.enabled = True
        time.sleep(1)
        sensor_luz.gain = 0
        sensor_luz.integration_time = 1
        print("Sensor de luz TSL2561: OK")
    except Exception as e:
        print(f"Sensor de luz FALLÓ: {e}")
        print(" → Forzando oscuridad (10 lux)")
        usar_sensor_luz = False

    # === Estado ===
    luz_encendida = False
    ultimo_movimiento = None

    # === Filtro PIR ===
    lectura_anterior = 0
    contador_movimiento = 0
    MOVIMIENTO_REQUERIDO = 2

    print("Bucle principal iniciando en 2 segundos...\n")
    time.sleep(2)

    try:
        while True:
            # Verificar modo
            modo = obtener_modo_desde_db(id_habitacion)
            if modo != "automatico":
                print(f"Modo cambiado a '{modo}' → deteniendo.")
                break

            # === PIR con filtro ===
            lectura_actual = GPIO.input(PIN_PIR)
            if lectura_actual == 1 and lectura_anterior == 1:
                contador_movimiento = min(contador_movimiento + 1, 5)
            elif lectura_actual == 0:
                contador_movimiento = max(contador_movimiento - 2, 0)
            movimiento = 1 if contador_movimiento >= MOVIMIENTO_REQUERIDO else 0
            lectura_anterior = lectura_actual

            # === LECTURA DE LUZ CORREGIDA ===
            luz_actual = 10.0  # valor por defecto
            if usar_sensor_luz and sensor_luz:
                try:
                    lux_val = sensor_luz.lux
                    if lux_val is not None:
                        luz_actual = float(lux_val)
                    else:
                        luz_actual = 10.0
                except Exception as e:
                    print(f"Error leyendo TSL2561: {e}")
                    luz_actual = 10.0

            # === Tiempo sin movimiento ===
            tiempo_sin_mov = time.time() - ultimo_movimiento if ultimo_movimiento else 0

            # === LOG ===
            print(f"[Hab {id_habitacion}] Lux: {luz_actual:5.1f} | PIR: {lectura_actual}→{movimiento} | "
                  f"On: {luz_encendida} | T: {tiempo_sin_mov:4.1f}s")

            # === ENCENDER ===
            if luz_actual < 20 and movimiento == 1 and not luz_encendida:
                print(f"ENCENDIENDO LUZ (lux={luz_actual:.2f}, mov={movimiento})")
                # → SOLO REGISTRAR LOS VALORES QUE ACTIVARON LA LUZ
                registrar_sensor('luz', id_habitacion, luz_actual)
                registrar_sensor('movimiento', id_habitacion, movimiento)
                # ← NO SE GUARDA luz=1
                encender()
                luz_encendida = True
                ultimo_movimiento = time.time()

            # === REINICIAR TEMPORIZADOR ===
            if movimiento == 1:
                ultimo_movimiento = time.time()

            # === APAGAR A LOS 30s ===
            if luz_encendida and ultimo_movimiento and (time.time() - ultimo_movimiento) >= 30:
                print("APAGANDO LUZ (30 segundos sin movimiento)")
                # → NO SE GUARDA NADA AL APAGAR
                apagar()
                luz_encendida = False
                ultimo_movimiento = None

            time.sleep(0.2)

    except KeyboardInterrupt:
        print("\nDetenido por usuario.")
    except Exception as e:
        print(f"Error crítico: {e}")
    finally:
        GPIO.cleanup()
        print("GPIO limpiado.")


# ==================== INICIAR HILO ====================
def activar_modo_automatico(id_habitacion):
    hilo = threading.Thread(target=ejecutar_modo_automatico, args=(id_habitacion,), daemon=True)
    hilo.start()
    print(f">>> Hilo automático iniciado para habitación {id_habitacion}.")


# ==================== PRUEBA LOCAL ====================
if __name__ == "__main__":
    ejecutar_modo_automatico(8)
