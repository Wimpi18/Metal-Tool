from math import sqrt
from pulp import LpProblem, LpMinimize, LpVariable, lpSum, value
from itertools import combinations_with_replacement

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
        f"      Cantidad de vigas HEB300: {num_vigas}",
        f"      Longitud de vigas HEB300: {sqrt((peralte-alto)**2 + (ancho/2)**2):.2f} m",
        "",
        f"      Cantidad de tirantes HEB300: {num_vigas / 2}",
        f"      Longitud de tirantes HEB300: {ancho:.2f} m",
        "",
        f"      Cantidad de pendolones HEB300: {num_vigas / 2}",
        f"      Longitud de pendolones HEB300: {peralte-alto:.2f} m",
        "",
        f"      Cantidad de montantes HEB300: {num_vigas}",
        f"      Longitud de montantes HEB300: {(peralte-alto)/2:.2f} m",
        "",
        f"      Cantidad de tornapuntas HEB300: {num_vigas}",
        f"      Longitud de tornapuntas HEB300: {sqrt(((peralte-alto)/2)**2 + (ancho/4)**2):.2f} m"
    ]

    return resultados, {"num_pilares": num_pilares, "num_costaneras": num_costaneras}

def calcular_costos_totales(resultados, costos, longitud_base):
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
    costo_por_metro = costos['mh3'] # Costo por metro de la barra

    barras_usadas, combinaciones, costo_total, desperdicio_total = simulacion_de_cortes(cantidades, longitudes, longitud_base, costo_por_metro)
    
    costos_totales.append(" ")
    costos_totales.append(f"Costo galpón: {costoPerfilHeb400 + costoPerfilC + costoPernosAnclaje + costo_total:.2f} $")
    costos_totales.append(f"    Costo total pilares con perfil HEB400: {costoPerfilHeb400:.2f} $")
    costos_totales.append(f"    Costo total costaneras con perfil C: {costoPerfilC:.2f} $")
    costos_totales.append(f"    Costo total pernos de anclaje: {costoPernosAnclaje:.2f} $")
    costos_totales.append(f"    Costo total cerchas con perfil HEB300: {costo_total:.2f} $")
    
    costos_totales.append(" ")
    costos_totales.append("Simulación de cortes:")
    costos_totales.append(f"    Cantidad de barras utilizadas: {barras_usadas}")
    costos_totales.append("")
    costos_totales.append(f"    Combinaciones de cortes:")
    for patron, cantidad in combinaciones.items():
        costos_totales.append(f"            Patrón {patron}: {cantidad} barras")
    costos_totales.append("")
    costos_totales.append(f"    Desperdicio perfil HEB300: {desperdicio_total:.2f} m")
    
    return costos_totales

def generar_patrones(longitudes, longitud_base):
    """
    Genera todos los patrones posibles de cortes dentro de la longitud base.
    :param longitudes: Lista de longitudes requeridas.
    :param longitud_base: Longitud base de la barra.
    :return: Lista de patrones de corte.
    """
    patrones = []
    for r in range(1, len(longitudes) + 1):
        for comb in combinations_with_replacement(longitudes, r):
            if sum(comb) <= longitud_base:
                patrones.append(comb)
    return patrones

def simulacion_de_cortes(cantidades, longitudes, longitud_base, costo_por_metro):
    """
    Simula los cortes necesarios para cumplir con las órdenes de perfiles HEB300, minimizando el desperdicio.
    """
    # Generar todos los patrones viables de cortes
    patrones = generar_patrones(longitudes, longitud_base)
    num_patrones = len(patrones)

    # Crear el problema de optimización
    prob = LpProblem("Cutting Stock Problem", LpMinimize)

    # Variables de decisión: cuántas barras usan cada patrón
    x = LpVariable.dicts("Patron", list(range(num_patrones)), cat="Integer", lowBound=0)

    # Función objetivo: minimizar el costo total
    prob += lpSum(x[p] for p in range(num_patrones)) * costo_por_metro * longitud_base, "CostoTotal"

    # Restricción: satisfacer la demanda de cada longitud
    for i, longitud in enumerate(longitudes):
        prob += (
            lpSum(x[p] * patrones[p].count(longitud) for p in range(num_patrones)) >= cantidades[i],
            f"Demanda_{longitud}",
        )

    # Resolver el problema
    prob.solve()

    # Resultados
    barras_usadas = sum(value(x[p]) for p in range(num_patrones))
    combinaciones_cortes = {tuple(patrones[p]): int(value(x[p])) for p in range(num_patrones) if value(x[p]) > 0}
    costo_total = value(prob.objective)

    # Cálculo del desperdicio total
    desperdicio_total = sum(
        (longitud_base - sum(patron)) * cantidad
        for patron, cantidad in combinaciones_cortes.items()
    )

    return barras_usadas, combinaciones_cortes, costo_total, desperdicio_total
