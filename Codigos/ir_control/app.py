from flask import Flask, render_template, request
import os

app = Flask(__name__)

# Lista de botones y sus comandos KEY_
botones = [
    "POWER", "OFF", "UP", "DOWN",
    "RED", "GREEN", "BLUE", "WHITE",
    "VIOLET", "PURPLE", "CYAN", "TURQUOISE",
    "ORANGE", "ORANGE2", "LIME", "MUSTARD",
    "AQUAMARINE", "YELLOW", "NAVY", "MAGENTA",
    "FLASH", "STROBE", "FADE", "SMOOTH"
]

@app.route("/")
def index():
    return render_template("index.html", botones=botones)

@app.route("/send", methods=["POST"])
def send():
    comando = request.form["comando"]
    os.system(f"irsend SEND_ONCE CONTROL_INT KEY_{comando}")
    print(f"✅ Enviado: KEY_{comando}")
    return ("", 204)  # Respuesta vacía sin recargar la página

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

