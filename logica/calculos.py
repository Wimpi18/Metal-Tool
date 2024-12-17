from math import sqrt, ceil
from pulp import LpProblem, LpMinimize, LpVariable, lpSum, value
from itertools import combinations_with_replacement
import matplotlib.pyplot as plt
SOLVER_MILO = "highs"
SOLVER_MINLO = "ipopt"

from amplpy import AMPL, ampl_notebook

ampl = ampl_notebook(
    modules=["coin", "highs"],  # modules to install
    license_uuid="default",  # license to use
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
    costoPernosAnclaje = float(resultados[0].split(':')[1].strip()) * 4 * costos['ma'] # Se calcula la cantidad de pernos de anclaje en base a la cantidad de pilares

    costoVigas = float(resultados[7].split(':')[1].strip()) * float(resultados[8].split(':')[1].strip().split(' ')[0]) * costos['mh3']
    costoTirantes = float(resultados[10].split(':')[1].strip()) * float(resultados[11].split(':')[1].strip().split(' ')[0]) * costos['mh3']
    costoPendolones = float(resultados[13].split(':')[1].strip()) * float(resultados[14].split(':')[1].strip().split(' ')[0]) * costos['mh3']
    costoMontantes = float(resultados[16].split(':')[1].strip()) * float(resultados[17].split(':')[1].strip().split(' ')[0]) * costos['mh3']
    costoTornapuntas = float(resultados[19].split(':')[1].strip()) * float(resultados[20].split(':')[1].strip().split(' ')[0]) * costos['mh3']
    # costoPerfilHeb300 = costoVigas + costoTirantes + costoPendolones + costoMontantes + costoTornapuntas
    
    cantidades = [float(resultados[7].split(':')[1].strip()), float(resultados[10].split(':')[1].strip()),
                  float(resultados[13].split(':')[1].strip()), float(resultados[16].split(':')[1].strip()),
                  float(resultados[19].split(':')[1].strip())]  # Cantidades requeridas de perfiles HEB300
    longitudes = [float(resultados[8].split(':')[1].strip().split(' ')[0]), float(resultados[11].split(':')[1].strip().split(' ')[0]),
                  float(resultados[14].split(':')[1].strip().split(' ')[0]), float(resultados[17].split(':')[1].strip().split(' ')[0]),
                  float(resultados[20].split(':')[1].strip().split(' ')[0])]  # Longitudes requeridas en metros
    costo_por_metro = costos['mh3'] # Costo por metro de la barra

    x, costoPerfilHeb300, total_waste = simulacion_de_cortes(cantidades, longitudes, longitudesBase, costo_por_metro)
    
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

    stocks = {}

    for i in range(0, len(longitudesBase)):
        stocks["Longitud " + str(i + 1) + " de " + str(longitudesBase[i]) + "m"] = {"length": longitudesBase[i], "cost": costo_por_metro * longitudesBase[i]}


    print("longitudes:")
    print(longitudes)

    print("cantidades:")
    print(cantidades)

    finish = {
        "Viga": {"length": longitudes[0], "demand": cantidades[0]},
        "Tirante": {"length": longitudes[1], "demand": cantidades[1]},
        "Pendolón": {"length": longitudes[2], "demand": cantidades[2]},
        "Montante": {"length": longitudes[3], "demand": cantidades[3]},
        "Tornapunta": {"length": longitudes[4], "demand": cantidades[4]},
    }

    patterns = make_patterns(stocks, finish)

    ax = plot_patterns(stocks, finish, patterns)

    x, cost, total_waste = cut_patterns(stocks, finish, patterns)

    ax = plot_nonzero_patterns(stocks, finish, patterns, x, cost, total_waste)


    return x, cost, total_waste




def make_patterns(stocks, finish):
    """
    Generates patterns of feasible cuts from stock lengths to meet specified finish lengths.

    Parameters:
    stocks (dict): A dictionary where keys are stock identifiers and values are dictionaries
                   with key 'length' representing the length of each stock.

    finish (dict): A dictionary where keys are finish identifiers and values are dictionaries
                   with key 'length' representing the required finish lengths.

    Returns:
    patterns (list): A list of dictionaries, where each dictionary represents a pattern of cuts.
                   Each pattern dictionary contains 'stock' (the stock identifier) and 'cuts'
                   (a dictionary where keys are finish identifiers and the value is the number
                   of cuts from the stock for each finish).
    """

    patterns = []
    for f in finish:
        feasible = False
        for s in stocks:
            # max number of f that fit on s
            num_cuts = int(stocks[s]["length"] / finish[f]["length"])

            # make pattern and add to list of patterns
            if num_cuts > 0:
                feasible = True
                cuts_dict = {key: 0 for key in finish.keys()}
                cuts_dict[f] = num_cuts

                # Calculate the total length used and the waste
                used_length = num_cuts * finish[f]["length"]
                waste = stocks[s]["length"] - used_length

                patterns.append({"stock": s, "cuts": cuts_dict, "waste": waste})

        if not feasible:
            print(f"No feasible pattern was found for {f}")
            return []

    return patterns


def plot_patterns(stocks, finish, patterns):
    # set up figure parameters
    lw = 0.6
    cmap = plt.get_cmap("tab10")
    colors = {f: cmap(k % 10) for k, f in enumerate(finish.keys())}
    fig, ax = plt.subplots(1, 1, figsize=(8, 0.05 + 0.4 * len(patterns)))

    for k, pattern in enumerate(patterns):
        # get stock key/name
        s = pattern["stock"]

        # plot stock as a grey background
        y_lo = (-k - lw / 2, -k - lw / 2)
        y_hi = (-k + lw / 2, -k + lw / 2)
        ax.fill_between((0, stocks[s]["length"]), y_lo, y_hi, color="k", alpha=0.1)

        # overlay finished parts
        xa = 0
        for f, n in pattern["cuts"].items():
            for j in range(n):
                xb = xa + finish[f]["length"]
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

    # clean up axes
    ax.spines[["top", "right", "left", "bottom"]].set_visible(False)
    ax.set_yticks(
        range(0, -len(patterns), -1),
        [pattern["stock"] for pattern in patterns],
        fontsize=8,
    )

    return ax

# Given dictionaries of stocks and finished parts, and a list of patterns,
# find minimum choice of patterns to cut


def cut_patterns(stocks, finish, patterns):
    m = AMPL()

    m.eval(
        """
        set S;
        set F;
        set P;

        param c{P};
        param a{F, P};
        param demand_finish{F};

        var x{P} integer >= 0;

        minimize cost:
            sum{p in P} c[p]*x[p];

        subject to demand{f in F}:
            sum{p in P} a[f,p]*x[p] >= demand_finish[f];

    """
    )

    m.set["S"] = list(stocks.keys())
    m.set["F"] = list(finish.keys())
    m.set["P"] = list(range(len(patterns)))

    s = {p: patterns[p]["stock"] for p in range(len(patterns))}
    c = {p: stocks[s[p]]["cost"] for p in range(len(patterns))}
    m.param["c"] = c
    a = {
        (f, p): patterns[p]["cuts"][f]
        for p in range(len(patterns))
        for f in finish.keys()
    }
    m.param["a"] = a
    m.param["demand_finish"] = {
        f_part: finish[f_part]["demand"] for f_part in finish.keys()
    }

    m.option["solver"] = SOLVER_MILO
    m.get_output("solve;")

    # Obtener la solución
    x_values = [m.var["x"][p].value() for p in range(len(patterns))]

    # Calcular el desperdicio total
    total_waste = 0
    for p in range(len(patterns)):
        if x_values[p] > 0:  # Si el patrón p se utiliza
            stock_length = stocks[patterns[p]["stock"]]["length"]
            # Calcular la longitud total utilizada en este patrón
            total_cut_length = sum(finish[f]["length"] * patterns[p]["cuts"].get(f, 0) for f in finish)
            # Calcular el desperdicio para este patrón
            waste = stock_length - total_cut_length
            total_waste += waste * x_values[p]  # El desperdicio se multiplica por cuántas veces se usa este patrón

    # Retornar el resultado de la optimización junto con el desperdicio total
    return x_values, m.obj["cost"].value(), total_waste


def plot_nonzero_patterns(stocks, finish, patterns, x, cost, total_waste):
    # Filtrar patrones que se utilizan (x > 0)
    k = [j for j, _ in enumerate(x) if _ > 0]
    selected_patterns = [patterns[j] for j in k]
    counts = [ceil(x[j]) for j in k]  # Redondear x[j] para contar el uso de cada patrón

    # Crear gráfica para los patrones seleccionados
    ax = plot_patterns(stocks, finish, selected_patterns)

    # Etiquetas del eje Y para los patrones seleccionados
    ticks = [
        f"{counts[i]} x {pattern['stock']}" for i, pattern in enumerate(selected_patterns)
    ]
    ax.set_yticks(range(0, -len(k), -1), ticks, fontsize=8)

    # Agregar el desperdicio al lado derecho de las barras
    for i, pattern in enumerate(selected_patterns):
        waste = pattern["waste"]  # Obtener el desperdicio
        stock_length = stocks[pattern["stock"]]["length"]  # Longitud del stock actual
        ax.text(
            stock_length + 0.5,  # Posición horizontal (ligeramente a la derecha del final)
            -i,  # Posición vertical (alineada con la barra)
            f"Desperdicio: {waste:.2f}m",  # Texto del desperdicio
            ha="left",  # Alineación del texto
            va="center",  # Centrar verticalmente
            fontsize=8,
            color="red",
        )

    # Título de la gráfica con el costo total
    ax.set_title(f"Costo = {round(cost, 2)} | Desperdicio Total = {round(total_waste, 2)}m", fontsize=10)
    return ax


