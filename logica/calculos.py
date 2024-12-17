from math import sqrt, ceil
from pulp import LpProblem, LpMinimize, LpVariable, lpSum, value
from itertools import combinations_with_replacement
import matplotlib.pyplot as plt
SOLVER_MILO = "highs"
SOLVER_MINLO = "ipopt"

from amplpy import AMPL, ampl_notebook

ampl = ampl_notebook(
    modules=["coin", "highs"],  
    license_uuid="default",  
) 

def calcular_resultados(datos):
    alto = datos["alto"]
    ancho = datos["ancho"]
    largo = datos["largo"]
    peralte = datos["peralte"]

    distancia_pilares = (largo) / (ceil(2 * largo / 3) - 1)
    num_pilares = num_vigas = (ceil(largo / distancia_pilares) + 1) * 2
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

def calcular_costos_totales(resultados, costos, longitudesBase):
    costos_totales = []
    costoPerfilHeb400 = float(resultados[0].split(':')[1].strip()) * float(resultados[1].split(':')[1].strip().split(' ')[0]) * costos['mh4']
    costoPerfilC = float(resultados[3].split(':')[1].strip()) * float(resultados[4].split(':')[1].strip().split(' ')[0]) * costos['mc']
    costoPernosAnclaje = float(resultados[0].split(':')[1].strip()) * 4 * costos['ma'] 

    costoVigas = float(resultados[7].split(':')[1].strip()) * float(resultados[8].split(':')[1].strip().split(' ')[0]) * costos['mh3']
    costoTirantes = float(resultados[10].split(':')[1].strip()) * float(resultados[11].split(':')[1].strip().split(' ')[0]) * costos['mh3']
    costoPendolones = float(resultados[13].split(':')[1].strip()) * float(resultados[14].split(':')[1].strip().split(' ')[0]) * costos['mh3']
    costoMontantes = float(resultados[16].split(':')[1].strip()) * float(resultados[17].split(':')[1].strip().split(' ')[0]) * costos['mh3']
    costoTornapuntas = float(resultados[19].split(':')[1].strip()) * float(resultados[20].split(':')[1].strip().split(' ')[0]) * costos['mh3']
    
    
    cantidades = [float(resultados[7].split(':')[1].strip()), float(resultados[10].split(':')[1].strip()),
                  float(resultados[13].split(':')[1].strip()), float(resultados[16].split(':')[1].strip()),
                  float(resultados[19].split(':')[1].strip())]  
    longitudes = [float(resultados[8].split(':')[1].strip().split(' ')[0]), float(resultados[11].split(':')[1].strip().split(' ')[0]),
                  float(resultados[14].split(':')[1].strip().split(' ')[0]), float(resultados[17].split(':')[1].strip().split(' ')[0]),
                  float(resultados[20].split(':')[1].strip().split(' ')[0])]  
    costo_por_metro = costos['mh3'] 

    x, costoPerfilHeb300, desperdicio_total = simulacion_de_cortes(cantidades, longitudes, longitudesBase, costo_por_metro)
    
    costos_totales.append(" ")
    costos_totales.append(f"    Costo total pilares con perfil HEB400: {costoPerfilHeb400:.2f} $")
    costos_totales.append(f"    Costo total costaneras con perfil C: {costoPerfilC:.2f} $")
    costos_totales.append(f"    Costo total pernos de anclaje: {costoPernosAnclaje:.2f} $")
    costos_totales.append(f"    Costo total cerchas con perfil HEB300: {costoPerfilHeb300:.2f} $")
    costos_totales.append(f"Costo galpón: {costoPerfilHeb400 + costoPerfilC + costoPernosAnclaje + costoPerfilHeb300:.2f} $")
    
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

def simulacion_de_cortes(cantidades, longitudes, longitudesBase, costo_por_metro):
    """
    Simula los cortes necesarios para cumplir con las órdenes de perfiles HEB300, minimizando el desperdicio.
    """

    inventario = {}

    for i in range(0, len(longitudesBase)):
        inventario["Longitud " + str(i + 1) + " de " + str(longitudesBase[i]) + "m"] = {"longitud": longitudesBase[i], "costo": costo_por_metro * longitudesBase[i]}

    elementos = {
        "Viga": {"longitud": longitudes[0], "demanda": cantidades[0]},
        "Tirante": {"longitud": longitudes[1], "demanda": cantidades[1]},
        "Pendolón": {"longitud": longitudes[2], "demanda": cantidades[2]},
        "Montante": {"longitud": longitudes[3], "demanda": cantidades[3]},
        "Tornapunta": {"longitud": longitudes[4], "demanda": cantidades[4]},
    }

    patrones = generar_patrones(inventario, elementos)

    ax = plot_patrones(inventario, elementos, patrones)

    x, costo, desperdicio_total = cut_patrones(inventario, elementos, patrones)

    ax = plot_nonzero_patrones(inventario, elementos, patrones, x, costo, desperdicio_total)


    return x, costo, desperdicio_total




def generar_patrones(inventario, elementos):
    """
    Genera patrones de cortes factibles a partir de longitudes de inventario para cumplir con las longitudes especificadas de los elementos.

    Parámetros:
    inventario (dict): Un diccionario donde las claves son los identificadores de inventario y los valores son diccionarios
                con la clave 'longitud' que representa la longitud de cada inventario.

    elementos (dict): Un diccionario donde las claves son los identificadores de los elementos y los valores son diccionarios
                con la clave 'longitud' que representa las longitudes requeridas de los elementos.

    Retorna:
    patrones (list): Una lista de diccionarios, donde cada diccionario representa un patrón de cortes.
                Cada diccionario de patrón contiene 'inventario' (el identificador del inventario) y 'cortes'
                (un diccionario donde las claves son los identificadores de los elementos y el valor es el número
                de cortes del inventario para cada elemento).
    """

    patrones = []
    for f in elementos:
        feasible = False
        for s in inventario:
            num_cuts = int(inventario[s]["longitud"] / elementos[f]["longitud"])

            if num_cuts > 0:
                feasible = True
                cuts_dict = {key: 0 for key in elementos.keys()}
                cuts_dict[f] = num_cuts

                used_longitud = num_cuts * elementos[f]["longitud"]
                desperdicio = inventario[s]["longitud"] - used_longitud

                patrones.append({"inventario": s, "cortes": cuts_dict, "desperdicio": desperdicio})

        if not feasible:
            print(f"No se encontró un patrón factible para {f}")
            return []

    return patrones


def plot_patrones(inventario, elementos, patrones):
    lw = 0.6
    cmap = plt.get_cmap("tab10")
    colors = {f: cmap(k % 10) for k, f in enumerate(elementos.keys())}
    fig, ax = plt.subplots(1, 1, figsize=(8, 0.05 + 0.4 * len(patrones)))

    for k, pattern in enumerate(patrones):
        s = pattern["inventario"]

        y_lo = (-k - lw / 2, -k - lw / 2)
        y_hi = (-k + lw / 2, -k + lw / 2)
        ax.fill_between((0, inventario[s]["longitud"]), y_lo, y_hi, color="k", alpha=0.1)

        xa = 0
        for f, n in pattern["cortes"].items():
            for j in range(n):
                xb = xa + elementos[f]["longitud"]
                ax.fill_between((xa, xb), y_lo, y_hi, alpha=1.0, color=colors[f])
                ax.plot((xb, xb), (y_lo[0], y_hi[0]), "w", lw=1, solid_capstyle="butt")
                ax.text(
                    (xa + xb) / 2,
                    -k,
                    f,
                    ha="center",
                    va="center",
                    fontsize=6,
                    color="w",
                    weight="bold",
                )
                xa = xb

    ax.spines[["top", "right", "left", "bottom"]].set_visible(False)
    ax.set_yticks(
        range(0, -len(patrones), -1),
        [pattern["inventario"] for pattern in patrones],
        fontsize=8,
    )

    return ax


def cut_patrones(inventario, elementos, patrones):
    m = AMPL()

    m.eval(
        """
        set S;
        set F;
        set P;

        param c{P};
        param a{F, P};
        param demanda_elementos{F};

        var x{P} integer >= 0;

        minimize costo:
            sum{p in P} c[p]*x[p];

        subject to demanda{f in F}:
            sum{p in P} a[f,p]*x[p] >= demanda_elementos[f];

    """
    )

    m.set["S"] = list(inventario.keys())
    m.set["F"] = list(elementos.keys())
    m.set["P"] = list(range(len(patrones)))

    s = {p: patrones[p]["inventario"] for p in range(len(patrones))}
    c = {p: inventario[s[p]]["costo"] for p in range(len(patrones))}
    m.param["c"] = c
    a = {
        (f, p): patrones[p]["cortes"][f]
        for p in range(len(patrones))
        for f in elementos.keys()
    }
    m.param["a"] = a
    m.param["demanda_elementos"] = {
        f_part: elementos[f_part]["demanda"] for f_part in elementos.keys()
    }

    m.option["solver"] = SOLVER_MILO
    m.get_output("solve;")

    
    x_valores = [m.var["x"][p].value() for p in range(len(patrones))]

    
    desperdicio_total = 0
    for p in range(len(patrones)):
        if x_valores[p] > 0:  
            longitud_inventario = inventario[patrones[p]["inventario"]]["longitud"]
            
            longitud_total_corte = sum(elementos[f]["longitud"] * patrones[p]["cortes"].get(f, 0) for f in elementos)
            
            desperdicio = longitud_inventario - longitud_total_corte
            desperdicio_total += desperdicio * x_valores[p]

    return x_valores, m.obj["costo"].value(), desperdicio_total


def plot_nonzero_patrones(inventario, elementos, patrones, x, costo, desperdicio_total):
    
    k = [j for j, _ in enumerate(x) if _ > 0]
    patrones_seleccionados = [patrones[j] for j in k]
    counts = [ceil(x[j]) for j in k]  
    
    ax = plot_patrones(inventario, elementos, patrones_seleccionados)

    ticks = [
        f"{counts[i]} x {pattern['inventario']}" for i, pattern in enumerate(patrones_seleccionados)
    ]
    ax.set_yticks(range(0, -len(k), -1), ticks, fontsize=8)

    
    for i, pattern in enumerate(patrones_seleccionados):
        desperdicio = pattern["desperdicio"]  
        longitud_inventario = inventario[pattern["inventario"]]["longitud"]  
        ax.text(
            longitud_inventario + 0.5,  
            -i,  
            f"Desperdicio: {desperdicio:.2f}m",  
            ha="left",  
            va="center",  
            fontsize=8,
            color="red",
        )

    
    ax.set_title(f"Costo = {round(costo, 2)} | Desperdicio Total = {round(desperdicio_total, 2)}m", fontsize=10)
    return ax


