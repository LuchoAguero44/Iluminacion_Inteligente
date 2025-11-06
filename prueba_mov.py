import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
PIR_PIN = 27
GPIO.setup(PIR_PIN, GPIO.IN)

print("Esperando movimiento (Ctrl+C para salir)...")
time.sleep(2)

try:
    while True:
        if GPIO.input(PIR_PIN):
            print(" Movimiento detectado!")
        else:
            print("Sin movimiento")
        time.sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()

