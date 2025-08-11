class Sensor ():


    def __init__(self, id_idicador,tipo_sensor,unidad_medida,emisor,receptor,estado,valor):
        
        self.id_idicador=id_idicador
        self.tipo_sensor=tipo_sensor #1 - Temperatura, 2 - Ultrasonido ....
        self.unidad_medida=unidad_medida #1-cm, 2 - segundos, ....
        self.emisor=emisor #pin utilizado para el emisor
        self.receptor=receptor#pin utiliza para el receptor
        self.estado=estado #True - Activo, False - Inactivo
        self.valor=valor # valor del sensor
        self.__estado_inicial=False #por defecto ponemos false


    
    def leer (self):
        print("Leyendoi el sensor ")
    def apagar(self):
        self.estado = False
        print("Sensor apagado")
    def __chequeo_inicial(self):
        self.__estado_inicial=True
        print("Verificacion de conexion...")


class sensor_ultrasonido(Sensor):
    def __init__ (self,ubicacion,id_idicador,tipo_sensor,unidad_medida,emisor,receptor,estado,valor):
        super().__init__(id_idicador,tipo_sensor,unidad_medida,emisor,receptor,estado,valor)
        self.ubicacion = ubicacion

    def leer(self):
        super().leer()
        if self.estado:
            print("asdxad")
        else:
            print("csdb")
class SensorMovimiento(Sensor):
    def __init__(self, id_idicador, unidad_medida, emisor, receptor, estado, valor, ubicacion):
        super().__init__(id_idicador, "Movimiento", unidad_medida, emisor, receptor, estado, valor)
        self.ubicacion = ubicacion
        self.movimiento_detectado = False

    def detectar(self):
        self.movimiento_detectado = True
        print(f"Movimiento detectado en {self.ubicacion}")

    def resetear(self):
        self.movimiento_detectado = False

class SensorLuminosidad(Sensor):
    def __init__(self, id_idicador, unidad_medida, emisor, receptor, estado, valor, ubicacion, umbral=50):
        super().__init__(id_idicador, "Luminosidad", unidad_medida, emisor, receptor, estado, valor)
        self.ubicacion = ubicacion
        self.umbral = umbral
        self.luminosidad_actual = 0

    def medir(self, valor):
        self.luminosidad_actual = valor
        print(f"Luminosidad en {self.ubicacion}: {valor}")

    def es_baja(self):
        return self.luminosidad_actual < self.umbral

sensor1 = Sensor(
    id_idicador=1,
    tipo_sensor="Temperatura",
    unidad_medida="Celsius",
    emisor=5,
    receptor=6,
    estado=True,
    valor=25
)

# Crear un objeto de la clase sensor_ultrasonido
sensor_ultra = sensor_ultrasonido(
    ubicacion="Entrada",
    id_idicador=2,
    tipo_sensor="Ultrasonido",
    unidad_medida="cm",
    emisor=7,
    receptor=8,
    estado=True,
    valor=100
)

print("Probando sensor1:")
sensor1.leer()
sensor1.apagar()

# Probar métodos del objeto sensor_ultra
print("\nProbando sensor_ultra:")
sensor_ultra.leer()
sensor_ultra.apagar()


sensor_mov = SensorMovimiento(
    id_idicador=10,
    unidad_medida="",
    emisor=1,
    receptor=2,
    estado=True,
    valor=0,
    ubicacion="Pasillo"
)

sensor_luz = SensorLuminosidad(
    id_idicador=11,
    unidad_medida="Lux",
    emisor=3,
    receptor=4,
    estado=True,
    valor=0,
    ubicacion="Sala",
    umbral=40
)

sensor_mov.detectar()
sensor_mov.resetear()
sensor_luz.medir(35)
print("¿Luminosidad baja?", sensor_luz.es_baja())