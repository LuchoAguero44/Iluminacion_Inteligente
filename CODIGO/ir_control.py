# ir_control.py
import subprocess
import threading
import time

def _enviar_ir(comando):
    try:
        result = subprocess.run(
            ["irsend", "SEND_ONCE", "CONTROL_INT", comando],
            check=True,
            timeout=3,
            capture_output=True,
            text=True
        )
        print(f"[IR] Enviado: {comando}")
    except subprocess.TimeoutExpired:
        print(f"[IR] Timeout: {comando}")
    except subprocess.CalledProcessError as e:
        print(f"[IR] Error irsend: {e.stderr}")
    except Exception as e:
        print(f"[IR] Error: {e}")


def encender():
    def _secuencia():
        _enviar_ir("KEY_POWER")
        time.sleep(0.5)   # ← AHORA SÍ está dentro del hilo
        _enviar_ir("KEY_WHITE")
    
    threading.Thread(target=_secuencia, daemon=True).start()
    
def apagar():
  _enviar_ir("KEY_OFF")
