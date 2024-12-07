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
        f"Cantidad de costaneras HEB300: {num_costaneras}",
        f"Longitud de costaneras HEB300: {distancia_pilares:.2f} m",
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
