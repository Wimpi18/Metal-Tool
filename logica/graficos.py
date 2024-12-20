import matplotlib.pyplot as plt
from math import sqrt, ceil

def graficar_estructura_galpon(datos, graficos):
    alto, ancho, largo, peralte, longitudesBase = datos.values()

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Parámetros del diseño
    distancia_pilares = (largo) / (ceil(1 * largo / 5) - 1)
    num_pilares = num_vigas = (ceil(largo / distancia_pilares) + 1)
    num_costaneras = round(((5*sqrt(26))/39) * sqrt((peralte-alto)**2 + (ancho/2)**2))
    
    # Dibujar los pilares (esquinas de cada marco)
    for i in range(num_pilares):
        x = i * distancia_pilares
        # Pilares delanteros y traseros
        ax.plot([x, x], [0, 0], [0, alto], color='brown', linewidth=2)  # Pilar frontal
        ax.plot([x, x], [ancho, ancho], [0, alto], color='brown', linewidth=2)  # Pilar trasero
    

    # Dibujar las costaneras
    for i in range(num_pilares - 1):
        for j in range(num_costaneras):
            x1 = i * distancia_pilares
            x2 = (i + 1) * distancia_pilares
            y = (j / num_costaneras) * (ancho/2)
            z = alto+j*(peralte-alto)/num_costaneras
            ax.plot([x1, x2], [y, y], [z, z], color='orange', linewidth=2)
            ax.plot([x1, x2], [ancho - y, ancho - y], [z, z], color='orange', linewidth=2)

    # Dibujar las vigas (vigas diagonales del techo)
    for i in range(num_vigas):
        x = i * distancia_pilares
        ax.plot([x, x], [0, ancho / 2], [alto, peralte], color='blue', linewidth=1.5)  # Frontal
        ax.plot([x, x], [ancho, ancho / 2], [alto, peralte], color='blue', linewidth=1.5)  # Trasera
    
    # Dibujar las cerchas (peralte)
    for i in range(num_pilares):
        x = i * distancia_pilares
        ax.plot([x, x], [0, ancho], [alto, alto], color='green', linewidth=1.5)
        ax.plot([x, x], [ancho / 2, ancho / 2], [alto, peralte], color='green', linewidth=1.5)
        ax.plot([x, x], [ancho / 4, ancho / 4], [alto, alto+(peralte - alto)/2], color='green', linewidth=1.5)
        ax.plot([x, x], [ancho - ancho / 4, ancho - ancho / 4], [alto, alto+(peralte - alto)/2], color='green', linewidth=1.5)
        ax.plot([x, x], [ancho / 4, ancho / 2], [alto+(peralte - alto)/2, alto], color='green', linewidth=1.5)
        ax.plot([x, x], [ancho / 2, ancho - ancho / 4], [alto, alto+(peralte - alto)/2], color='green', linewidth=1.5)
    
    # Crear los elementos de la leyenda
    pillar_line = plt.Line2D([0], [0], color='brown', lw=2)
    costanera_line = plt.Line2D([0], [0], color='orange', lw=2)
    viga_line = plt.Line2D([0], [0], color='blue', lw=1.5)
    cercha_line = plt.Line2D([0], [0], color='green', lw=1.5)
    
    # Añadir la leyenda
    ax.legend([pillar_line, costanera_line, viga_line, cercha_line],
              ['Pilares', 'Costaneras', 'Vigas', 'Cerchas'], loc='upper left')

    # Configurar los límites del gráfico
    ax.set_xlabel('Largo (m)')
    ax.set_ylabel('Ancho (m)')
    ax.set_zlabel('Altura (m)')
    ax.set_xlim([-2, largo+2])
    ax.set_ylim([-2, ancho+2])
    ax.set_zlim([0, peralte])

    plt.show(block=False)
