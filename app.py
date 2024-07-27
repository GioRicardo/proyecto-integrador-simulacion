import random
import math
from tabulate import tabulate
import json
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.stats import kurtosis, skew, sem, norm

# --------------------------------------------------------------------------------------------

# Paso 1: Inicializar variables
# Variables globales
cola_espera = []
buffer = []
cajas = [None] * 5
current_time = 0
current_time2 = 0
cola = []
tabla_clientes = []  # Estructura para almacenar los datos de la tabla
count1 = 0
ejecutado_una_vez = False

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
    for i in range(1, 31):
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
    #print(tabulate(table, headers, tablefmt="grid"))
    print("\n=====================================================================================================\n")

# Funciones auxiliares para contar tipos de clientes
def contar_tipo_cliente(tipo):
    count = 0
    for cliente in buffer + [caja for caja in cajas if caja is not None]:
        if cliente["tipo_cliente"] == tipo:
            count += 1
    return count

def mover_a_buffer():
    global buffer, cola_espera, cajas, current_time, count1, ejecutado_una_vez
    
    if not ejecutado_una_vez and all(caja is None for caja in cajas):
        count1+=1
        # Organizar la cola por tiempo de espera + bonificación en orden descendente
        #cola_espera.sort(key=lambda x: (x["hill"] + x["bonificacion"]), reverse=True)
        cliente = cola_espera[0]
        
        #print(cola_espera)
        for i in range(len(cajas)):
            
            
            if cola_espera:
                buffer.append(cola_espera.pop(0))
                
                # Si la caja está vacía y hay clientes en el buffer
                if cajas[i] is None and buffer:
                        # Asignar el primer cliente del buffer a la caja
                        cliente = buffer.pop(0)
                            
                        # Actualizar el tiempo de salida
                        cliente["tiempo_espera"] = 0
                        cliente["tiempo_salida"] = current_time + cliente["service_time"]
                        cajas[i] = cliente

                        # Actualizar la tabla con los tiempos reales
                        for row in tabla_clientes:
                                if row[0] == cliente["id"]:
                                    row[8] = cliente["tiempo_espera"]
                                    row[9] = cliente["tiempo_salida"]
                                    break
        ejecutado_una_vez = True                      
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
            # Si todas las cajas están vacías, el tiempo de espera es 0
            
            
            # Actualizar el tiempo de espera
            cliente["tiempo_espera"] = current_time - cliente["hill"]
            # Actualizar el tiempo de salida
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
datos_cajas2 = []
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
                service_time = cajas[i]["service_time"]
                cajas[i]["service_time"] -= 1
                # Guardar el estado actual de las cajas
                datos_cajas.append(cajas[i].copy())  # Agregar una copia del estado actual
                # Si el tiempo de servicio es 0 o menor, liberar la caja
                if cajas[i]["service_time"] <= 0:
                    cajas[i]["service_time"] = service_time
                    datos_cajas2.append(cajas[i].copy())
                    cajas[i] = None

    # Escribir la lista en un archivo JSON del decremento del tiempo de servicio
    with open('datos_cajas.json', 'w') as archivo_json:
        json.dump(datos_cajas, archivo_json, indent=4)

    tabla_clientes2 = tabla_clientes
    # Mostrar tabla actualizada
    headers = ["Cliente", "Valor Aleatorio 1", "Tell", "Hill", "Valor Aleatorio 2", "Tipo Cliente", "Bonificación", "Tiempo de Servicio", "Tiempo de Espera", "Tiempo de Salida"]
    print("Clientes en orden de llegada")
    print(tabulate(tabla_clientes, headers, tablefmt="grid"))
    headers2 = ["Cliente", "Tell", "Hill", "Tipo Cliente", "Bonificación", "Tiempo de Servicio", "Tiempo de Espera", "Tiempo de Salida"]
    # Suponiendo que datos_cajas2 no está vacío y todos los diccionarios tienen las mismas claves
    headers = datos_cajas2[0].keys()
    # Convertir los diccionarios a listas de valores
    table = [list(d.values()) for d in datos_cajas2]
    # print("Orden de salida de los clientes de las cajas")
    
    # Convertir table a DataFrame
    df = pd.DataFrame(table)
    
    # Cambiar nombres de columnas usando rename()
    df = df.rename(columns={0: 'Cliente', 1: 'Tell', 2: 'Hill', 3: 'Tipo Cliente', 4: 'Bonificación', 5: 'Tiempo de Servicio', 6: 'Tiempo de Espera', 7: 'Tiempo de Salida'})
    
    descriptive_stats = df.describe()
    # Filtrar solo las columnas numéricas
    numeric_df = df.select_dtypes(include='number')
    
    # print(numeric_df)
    
    # Calcular la moda
    mode = df.mode()
    
    # Calcular la desviación estándar de cada columna
    std_dev = numeric_df.std()

    # Calcular la media de cada columna
    mean = numeric_df.mean()
    
    # Calcular el coeficiente de variación (CV)
    cv = (std_dev / mean) * 100
    
    # Calcular el rango
    data_range = numeric_df.max() - numeric_df.min()
    
    # Calcular la varianza de cada columna numérica
    variance = numeric_df.var()
    
    # Agrupaciones (Group By)
    grouped = df.groupby('Tipo Cliente').mean()
    
    # Error Típico (Standard Error of the Mean)
    # Calculado como la desviación estándar dividida por la raíz cuadrada del tamaño de la muestra
    standard_error = numeric_df.apply(sem)

    # Curtosis
    # La curtosis de una distribución normal es 0. Más de 0 indica una distribución "apuntada".
    kurtosis_values = numeric_df.apply(kurtosis)

    # Coeficiente de Asimetría (Skewness)
    # La asimetría de una distribución normal es 0. Los valores positivos indican una cola derecha más larga, los valores negativos una cola izquierda más larga
    skewness_values = numeric_df.apply(skew)
    
    # Mostrar los resultados
    print("Estadísticas Descriptivas Básicas:\n", descriptive_stats)
    print("=====================================================================================================")
    print("\nModa:\n", mode)
    print("=====================================================================================================")
    print("\nVarianza:\n", variance)
    print("=====================================================================================================")
    print("\nDesviación Estándar:\n", std_dev)
    print("=====================================================================================================")
    print("\nCoeficiente de Variación (%):\n", cv)
    print("=====================================================================================================")
    print("\nRango:\n", data_range)
    print("=====================================================================================================")
    print("\nEstadísticas por grupo: media por tipo de cliente\n", grouped)
    print("=====================================================================================================")
    print("\nError Típico (SEM):\n", standard_error)
    print("=====================================================================================================")
    print("\nCurtosis:\n", kurtosis_values)
    print("=====================================================================================================")
    print("\nCoeficiente de Asimetría (Skewness):\n", skewness_values)
    # Mostrar el DataFrame
    # print(df.describe())
    # print(tabulate(table, headers=headers, tablefmt="grid"))
    #print(tabla_clientes)
    headers2 = list(datos_cajas2[0].keys()) 
    # Suponiendo que datos_cajas2 es una lista de diccionarios con las claves 'tiempo_espera', 'tiempo_salida', 'hill' y 'tipo_cliente'
    tiempo_espera = [d['tiempo_espera'] for d in datos_cajas2]
    tiempo_salida = [d['tiempo_salida'] for d in datos_cajas2]
    hill = [d['hill'] for d in datos_cajas2]
    tipo_cliente = [d['tipo_cliente'] for d in datos_cajas2]

    # Crear una figura y un eje
    fig, ax = plt.subplots()

    # Definir colores y marcadores para cada tipo de cliente y hill
    colores = {'USUARIO': 'r', 'EMPRESAS': 'g', 'PERSONAL': 'b', 'BANCARIO': 'c', 'ESPECIAL': 'm', 'VIP': 'y', 'TRANSFERIDO': 'k'}
    marcadores = {'Hill1': 'o', 'Hill2': 's', 'Hill3': '^', 'Hill4': 'd'}

    # Graficar los datos
    for t_espera, t_salida, h, t_cliente in zip(tiempo_espera, tiempo_salida, hill, tipo_cliente):
        ax.scatter(t_espera, t_salida, color=colores.get(t_cliente, 'k'), marker=marcadores.get(h, 'x'), label=f'{t_cliente} - {h}')

    # Añadir etiquetas y título
    ax.set_xlabel('Tiempo de Espera')
    ax.set_ylabel('Tiempo de Salida')
    ax.set_title('Gráfico de Tiempo de Espera vs Tiempo de Salida')

    # Crear una leyenda única
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys())

    # Mostrar el gráfico
    plt.show()
if __name__ == '__main__':
    simulacion()
