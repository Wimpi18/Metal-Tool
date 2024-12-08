from math import sqrt
from pulp import LpProblem, LpMinimize, LpVariable, lpSum, value

def calcular_resultados(datos):
    alto = datos["alto"]
    ancho = datos["ancho"]
    largo = datos["largo"]
    peralte = datos["peralte"]

    distancia_pilares = 6
    num_pilares = num_vigas = (int(largo / distancia_pilares) + 1) * 2
    num_costaneras = round(((5 * sqrt(26)) / 39) * sqrt((peralte - alto) ** 2 + (ancho / 2) ** 2)) * (num_pilares / 2 - 1) * 2

    resultados = [
        f"Cantidad de pilares HEB400: {num_pilares}",
        f"Longitud de pilares HEB400: {alto:.2f} m",
        "",
        f"Cantidad de costaneras C: {num_costaneras}",
        f"Longitud de costaneras C: {distancia_pilares:.2f} m",
        "",
        "Para cerchas:",
        f"  Cantidad de vigas HEB300: {num_vigas}",
        f"  Longitud de vigas HEB300: {sqrt((peralte-alto)**2 + (ancho/2)**2):.2f} m",
        "",
        f"  Cantidad de tirantes HEB300: {num_vigas / 2}",
        f"  Longitud de tirantes HEB300: {ancho:.2f} m",
        "",
        f"  Cantidad de pendolones HEB300: {num_vigas / 2}",
        f"  Longitud de pendolones HEB300: {peralte-alto:.2f} m",
        "",
        f"  Cantidad de montantes HEB300: {num_vigas}",
        f"  Longitud de montantes HEB300: {(peralte-alto)/2:.2f} m",
        "",
        f"  Cantidad de tornapuntas HEB300: {num_vigas}",
        f"  Longitud de tornapuntas HEB300: {sqrt(((peralte-alto)/2)**2 + (ancho/4)**2):.2f} m"
    ]

    return resultados, {"num_pilares": num_pilares, "num_costaneras": num_costaneras}

def calcular_costos_totales(resultados, costos):
    costos_totales = []
    costoPerfilHeb400 = float(resultados[0].split(':')[1].strip()) * float(resultados[1].split(':')[1].strip().split(' ')[0]) * costos['mh4']
    costoPerfilC = float(resultados[3].split(':')[1].strip()) * float(resultados[4].split(':')[1].strip().split(' ')[0]) * costos['mc']
    costoPernosAnclaje = float(resultados[0].split(':')[1].strip()) * 4 * costos['ma'] # Se calcula la cantidad de pernos de anclaje en base a la cantidad de pilares

    costoVigas = float(resultados[7].split(':')[1].strip()) * float(resultados[8].split(':')[1].strip().split(' ')[0]) * costos['mh3']
    costoTirantes = float(resultados[10].split(':')[1].strip()) * float(resultados[11].split(':')[1].strip().split(' ')[0]) * costos['mh3']
    costoPendolones = float(resultados[13].split(':')[1].strip()) * float(resultados[14].split(':')[1].strip().split(' ')[0]) * costos['mh3']
    costoMontantes = float(resultados[16].split(':')[1].strip()) * float(resultados[17].split(':')[1].strip().split(' ')[0]) * costos['mh3']
    costoTornapuntas = float(resultados[19].split(':')[1].strip()) * float(resultados[20].split(':')[1].strip().split(' ')[0]) * costos['mh3']
    costoPerfilHeb300 = costoVigas + costoTirantes + costoPendolones + costoMontantes + costoTornapuntas
    
    cantidades = [float(resultados[7].split(':')[1].strip()), float(resultados[10].split(':')[1].strip()),
                  float(resultados[13].split(':')[1].strip()), float(resultados[16].split(':')[1].strip()),
                  float(resultados[19].split(':')[1].strip())]  # Cantidades requeridas de perfiles HEB300
    longitudes = [float(resultados[8].split(':')[1].strip().split(' ')[0]), float(resultados[11].split(':')[1].strip().split(' ')[0]),
                  float(resultados[14].split(':')[1].strip().split(' ')[0]), float(resultados[17].split(':')[1].strip().split(' ')[0]),
                  float(resultados[20].split(':')[1].strip().split(' ')[0])]  # Longitudes requeridas en metros
    longitud_base = 15.0  # Longitud base de las barras en metros
    costo_por_metro = costos['mh3'] # Costo por metro de la barra

    barras_usadas, cortes, costo_total = simulacion_de_cortes(cantidades, longitudes, longitud_base, costo_por_metro)
    
    costos_totales.append(" ")
    costos_totales.append("Costo galpón:")
    costos_totales.append(f"Costo total pilares con perfil HEB400: {costoPerfilHeb400:.2f} $")
    costos_totales.append(f"Costo total costaneras con perfil C: {costoPerfilC:.2f} $")
    costos_totales.append(f"Costo total pernos de anclaje: {costoPernosAnclaje:.2f} $")

    costos_totales.append("Simulación de cortes:")
    costos_totales.append(f"Cantidad de barras utilizadas: {barras_usadas}")
    
    desperdicio = barras_usadas * longitud_base
    costos_totales.append("Cortes realizados:")
    for longitud, cantidad in cortes.items():
        costos_totales.append(f"  {cantidad} cortes de longitud {longitud} m")
        desperdicio -= cantidad * longitud
    costos_totales.append(f"Desperdicio perfil HEB300: {desperdicio:.2f} m")
    costos_totales.append(f"Costo total cerchas con perfil HEB300: {costo_total:.2f} $")
    return costos_totales

def simulacion_de_cortes(cantidades, longitudes, longitud_base, costo_por_metro):
    """
    Simula los cortes necesarios para cumplir con las órdenes de perfiles HEB300, minimizando el desperdicio.
    
    :param cantidades: Lista de cantidades requeridas por cada longitud.
    :param longitudes: Lista de longitudes requeridas (en metros).
    :param longitud_base: Longitud base de la barra (en metros).
    :param costo_por_metro: Costo por metro de la barra.
    """
    prob = LpProblem("Cutting Stock Problem", LpMinimize)

    # Número de tipos de longitudes requeridas
    I = len(longitudes)

    # Variables de decisión: número de barras utilizadas y el número de cortes por barra
    y = LpVariable("NumeroDeBarras", cat="Integer", lowBound=0)
    x = LpVariable.dicts("Cortes", list(range(I)), cat="Integer", lowBound=0)

    # Función objetivo: minimizar el costo total
    prob += y * longitud_base * costo_por_metro, "CostoTotal"

    # Restricción 1: Satisfacer la demanda de cada longitud requerida
    for i in range(I):
        prob += x[i] >= cantidades[i], f"Demanda_{i}"

    # Restricción 2: Longitud total de cortes por barra no puede exceder la longitud base
    prob += lpSum(x[i] * longitudes[i] for i in range(I)) <= y * longitud_base, "RestriccionDeLongitud"

    # Resolver el problema
    prob.solve()

    # Imprimir resultados
    barras_usadas = value(y)
    cortes = {longitudes[i]: value(x[i]) for i in range(I)}
    costo_total = value(prob.objective)

    return barras_usadas, cortes, costo_total
