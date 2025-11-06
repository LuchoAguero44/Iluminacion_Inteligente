import RPi.GPIO as GPIO
import time

# Configurar modo de numeración de pines (BCM = número de GPIO)
GPIO.setmode(GPIO.BCM)

# Configurar GPIO4 como entrada
GPIO.setup(4, GPIO.IN)

try:
    while True:
        estado = GPIO.input(4)  # Lee el pin (0 o 1)
        if estado ==0:
            print("No detectado")
        
        elif estado == 1:
            print("Detectado")
            
        time.sleep(0.5)

except KeyboardInterrupt:
    print("Programa terminado")

finally:
    GPIO.cleanup()  # Limpia la configuración de los pines

