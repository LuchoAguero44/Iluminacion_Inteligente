import RPi.GPIO as GPIO
import time

# Configurar modo de numeración de pines (BCM = número de GPIO)
GPIO.setmode(GPIO.BCM)

# Configurar GPIO4 como entrada
GPIO.setup(4, GPIO.IN)

try:
    while True:
        estado = GPIO.input(4)  # Lee el pin (0 o 1)
        print("GPIO4 =", estado)
        time.sleep(0.5)

except KeyboardInterrupt:
    print("Programa terminado")

finally:
    GPIO.cleanup()  # Limpia la configuración de los pines

