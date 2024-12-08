from math import sqrt

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
    
    costos_totales.append(" ")
    costos_totales.append("Costo galpón:")
    costos_totales.append(f"    Costo total pilares: {costoPerfilHeb400:.2f} $")
    costos_totales.append(f"    Costo total costaneras: {costoPerfilC:.2f} $")
    costos_totales.append(f"    Costo total pernos de anclaje: {costoPernosAnclaje:.2f} $")

    costos_totales.append(" ")
    costos_totales.append(f"Costo cerchas con perfil HEB300: {costoPerfilHeb300:.2f} $")
    costos_totales.append(f"    Costo total vigas: {costoVigas:.2f} $")
    costos_totales.append(f"    Costo total tirantes: {costoTirantes:.2f} $")
    costos_totales.append(f"    Costo total pendolones: {costoPendolones:.2f} $")
    costos_totales.append(f"    Costo total montantes: {costoMontantes:.2f} $")
    costos_totales.append(f"    Costo total tornapuntas: {costoTornapuntas:.2f} $")
    return costos_totales