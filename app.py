import random
import math
from tabulate import tabulate
import json

# --------------------------------------------------------------------------------------------

# Paso 1: Inicializar variables
# Variables globales
cola_espera = []
buffer = []
cajas = [None] * 4
current_time = 0
cola = []
tabla_clientes = []  # Estructura para almacenar los datos de la tabla

# RND - número aleatorio entre 0 y 1
def generate_random_value():
    return random.random()

# Tiempo entre llegadas (TELL)
def calculate_expression(x):
    return (-47.75) * (math.log(x))

# Tiempo de servicio (TS)
def calculate_service_time(a, b):
    r = generate_random_value()
    return a + (b - a) * r

def inicio_de_simulacion():
    global current_time, tabla_clientes
    table = []
    # Paso 4: Generar los primeros 20 clientes
    for i in range(1, 21):
        cliente = {
            "id": i,
            "tell": 0,
            "hill": 0,
            "tipo_cliente": "",
            "bonificacion": 0,
            "service_time": 0,
            "tiempo_espera": "Pendiente",  # Inicialmente pendiente
            "tiempo_salida": "Pendiente"   # Inicialmente pendiente
        }
        valor_aleatorio1 = generate_random_value()
        # Paso 5: Calcular el tiempo entre llegadas
        tell = calculate_expression(valor_aleatorio1)
        current_time += tell
        cliente["tell"] = tell
        cliente["hill"] = current_time
        valor_aleatorio2 = generate_random_value()
        # Paso 6: Calcular el tipo de cliente
        if valor_aleatorio2 < 0.52:
            cliente["tipo_cliente"] = "BANCARIO"
            cliente["bonificacion"] = 400
            a, b = 240, 580
        elif 0.52 <= valor_aleatorio2 < 0.53:
            cliente["tipo_cliente"] = "TRANSFERIDO"
            cliente["bonificacion"] = 0
            a, b = 700, 1400
        elif 0.53 <= valor_aleatorio2 < 0.56:
            cliente["tipo_cliente"] = "EMPRESAS"
            cliente["bonificacion"] = 400
            a, b = 700, 2300
        elif 0.56 <= valor_aleatorio2 < 0.58:
            cliente["tipo_cliente"] = "ESPECIAL"
            cliente["bonificacion"] = 1000
            a, b = 240, 580
        elif 0.58 <= valor_aleatorio2 < 0.81:
            cliente["tipo_cliente"] = "PERSONAL"
            cliente["bonificacion"] = 1000
            a, b = 240, 580
        elif 0.81 <= valor_aleatorio2 < 0.98:
            cliente["tipo_cliente"] = "USUARIO"
            cliente["bonificacion"] = 0
            a, b = 240, 580
        else:
            cliente["tipo_cliente"] = "VIP"
            cliente["bonificacion"] = 1800
            a, b = 240, 580
        # Paso 7: Calcular el tiempo del servicio
        cliente["service_time"] = calculate_service_time(a, b)
        # Paso 8: Agregar el cliente a la cola de espera sin importar el tipo de cliente ni el orden
        cola_espera.append(cliente)
        
        row = [
            i,
            valor_aleatorio1,
            tell,
            current_time,
            valor_aleatorio2,
            cliente["tipo_cliente"],
            cliente["bonificacion"],
            cliente["service_time"],
            cliente["tiempo_espera"],  # Inicialmente pendiente
            cliente["tiempo_salida"]   # Inicialmente pendiente
        ]
        
        table.append(row)
        tabla_clientes.append(row)  # Agrega a la tabla de clientes
    
    headers = ["Cliente", "Valor Aleatorio 1", "Tell", "Hill", "Valor Aleatorio 2", "Tipo Cliente", "Bonificación", "Tiempo de Servicio", "Tiempo de Espera", "Tiempo de Salida"]
    print(tabulate(table, headers, tablefmt="grid"))

# Funciones auxiliares para contar tipos de clientes
def contar_tipo_cliente(tipo):
    count = 0
    for cliente in buffer + [caja for caja in cajas if caja is not None]:
        if cliente["tipo_cliente"] == tipo:
            count += 1
    return count

def mover_a_buffer():
    global buffer, cola_espera, cajas, current_time

    # Calcular el tiempo de salida de las cajas
    tiempos_salida = [caja["hill"] + caja["service_time"] if caja is not None else float('inf') for caja in cajas]
    menor_tiempo_salida = min(tiempos_salida)

    # Mover clientes a la cola si su tiempo de llegada es menor al menor tiempo de salida de las cajas
    global cola
    while cola_espera and cola_espera[0]["hill"] <= menor_tiempo_salida:
        cliente = cola_espera.pop(0)
        cola.append(cliente)

    # Organizar la cola por tiempo de espera + bonificación en orden descendente
    cola.sort(key=lambda x: (x["hill"] + x["bonificacion"]), reverse=True)

    # Mover clientes de la cola al buffer si hay espacio disponible
    while cola and len(buffer) < 3:
        cliente = cola[0]
        
        # Paso 10: Verificar las reglas de prioridad
        
        # Regla a: Cliente Especial
        if cliente["tipo_cliente"] == "Especial":
            if contar_tipo_cliente("Especial") > 0:
                continue

        # Regla b: Cliente Empresas
        elif cliente["tipo_cliente"] == "Empresas":
            cajas_disponibles = sum(1 for caja in cajas if caja is None)
            max_empresas = 2 if cajas_disponibles > 4 else 1
            if contar_tipo_cliente("Empresas") >= max_empresas:
                continue

        # Regla c: Cliente Transferido
        elif cliente["tipo_cliente"] == "Transferido":
            if contar_tipo_cliente("Transferido") > 0:
                continue

        # Paso 11: Mover cliente al buffer
        buffer.append(cola.pop(0))

def mover_a_cajas():
    global buffer, cajas, current_time
    # Mover clientes del buffer a las cajas
    for i in range(len(cajas)):
        # Si la caja está vacía y hay clientes en el buffer
        if cajas[i] is None and buffer:
            # Asignar el primer cliente del buffer a la caja
            cliente = buffer.pop(0)
            # Actualizar el tiempo de espera y tiempo de salida
            cliente["tiempo_espera"] = current_time - cliente["hill"]
            cliente["tiempo_salida"] = current_time + cliente["service_time"]
            cajas[i] = cliente

            # Actualizar la tabla con los tiempos reales
            for row in tabla_clientes:
                if row[0] == cliente["id"]:
                    row[8] = cliente["tiempo_espera"]
                    row[9] = cliente["tiempo_salida"]
                    break

# Lista para almacenar los datos
datos_cajas = []
# Simulación
def simulacion():
    inicio_de_simulacion()
    while cola_espera or buffer or any(cajas):
        mover_a_buffer()
        mover_a_cajas()
        
        # Actualizar el estado de las cajas
        for i in range(len(cajas)):
            if cajas[i] is not None:
                # Decrementar el tiempo de servicio
                cajas[i]["service_time"] -= 1
                # Guardar el estado actual de las cajas
                datos_cajas.append(cajas[i].copy())  # Agregar una copia del estado actual
                # Si el tiempo de servicio es 0 o menor, liberar la caja
                if cajas[i]["service_time"] <= 0:
                    cajas[i] = None

    # Escribir la lista en un archivo JSON del decremento del tiempo de servicio
    with open('datos_cajas.json', 'w') as archivo_json:
        json.dump(datos_cajas, archivo_json, indent=4)

    # Mostrar tabla actualizada
    headers = ["Cliente", "Valor Aleatorio 1", "Tell", "Hill", "Valor Aleatorio 2", "Tipo Cliente", "Bonificación", "Tiempo de Servicio", "Tiempo de Espera", "Tiempo de Salida"]
    print(tabulate(tabla_clientes, headers, tablefmt="grid"))

if __name__ == '__main__':
    simulacion()
