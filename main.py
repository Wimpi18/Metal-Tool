import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from math import sqrt

def enviar_datos():
    try:
        # Capturar los datos ingresados
        alto = float(entry_alto.get())
        ancho = float(entry_ancho.get())
        largo = float(entry_largo.get())
        peralte = float(entry_peralte.get())
        
        # Validaciones
        if alto < 3 or alto > 12:
            raise ValueError("El alto debe estar entre 3 y 12 metros.")
        if ancho < 6 or ancho > 50:
            raise ValueError("El ancho debe estar entre 6 y 50 metros.")
        if largo <= 0 or largo > 100 or largo % 6 != 0 or largo < ancho:
            raise ValueError("El largo debe estar entre 0 y 100 metros, ser múltiplo de 6 y mayor que el ancho.")
        if peralte <= alto or peralte > alto + 5:
            raise ValueError("El peralte debe ser mayor que el alto y no exceder en más de 5 metros al alto.")
        
        # Mensaje de confirmación
        messagebox.showinfo("Datos enviados", f"Datos ingresados correctamente:\n"
                                              f"Alto: {alto} m\nAncho: {ancho} m\n"
                                              f"Largo: {largo} m\nPeralte: {peralte} m")
        
        distancia_pilares = 6
        num_pilares = num_vigas = (int(largo / distancia_pilares) + 1)*2
        num_costaneras = round(((5*sqrt(26))/39) * sqrt((peralte-alto)**2 + (ancho/2)**2)) * (num_pilares/2 - 1) * 2

        # Graficar la estructura del galpón
        graficar_estructura_galpon(alto, ancho, largo, peralte)

        # Generar resultados detallados
        resultados = []
        resultados.append(f"Cantidad de pilares HEB400: {num_pilares}")
        resultados.append(f"Longitud de pilares HEB400: {alto:.2f} m")
        resultados.append(f"Cantidad de costaneras HEB300: {num_costaneras}")
        resultados.append(f"Longitud de costaneras HEB300: {distancia_pilares:.2f} m")
        resultados.append("Para las cerchas:")
        resultados.append(f"Cantidad de vigas HEB300: {num_vigas}")
        resultados.append(f"Longitud de vigas HEB300: {sqrt((peralte-alto)**2 + (ancho/2)**2):.2f} m")
        resultados.append(f"Cantidad de tirantes HEB300: {num_vigas / 2}")
        resultados.append(f"Longitud de tirantes HEB300: {ancho:.2f} m")
        resultados.append(f"Cantidad de pendolones HEB300: {num_vigas / 2}")
        resultados.append(f"Longitud de pendolones HEB300: {peralte-alto:.2f} m")
        resultados.append(f"Cantidad de montantes HEB300: {num_vigas}")
        resultados.append(f"Longitud de montantes HEB300: {(peralte-alto)/2:.2f} m")
        resultados.append(f"Cantidad de tornapuntas HEB300: {num_vigas}")
        resultados.append(f"Longitud de tornapuntas HEB300: {sqrt(((peralte-alto)/2)**2 + (ancho/4)**2):.2f} m")
        
        # Mostrar los resultados en el widget de texto
        resultado_text.delete(1.0, tk.END)  # Limpiar texto anterior
        resultado_text.insert(tk.END, "\n".join(resultados))
        
        # Cambiar a la segunda pestaña
        notebook.select(1)

    except ValueError as e:
        # Mostrar mensaje de error
        messagebox.showerror("Error", f"Entrada inválida: {e}")

def graficar_estructura_galpon(alto, ancho, largo, peralte):
    # Crear un gráfico 3D
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    # Parámetros del diseño
    distancia_pilares = 6
    num_pilares = num_vigas = int(largo / distancia_pilares) + 1
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
    
    # Configurar los límites del gráfico
    ax.set_xlabel('Largo (m)')
    ax.set_ylabel('Ancho (m)')
    ax.set_zlabel('Altura (m)')
    ax.set_xlim([-2, largo+2])
    ax.set_ylim([-2, ancho+2])
    ax.set_zlim([0, peralte])

    # Mostrar el gráfico
    plt.show()

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Ingreso de Dimensiones del Galpón")
ventana.geometry("500x400")

# Crear un widget Notebook para manejar las pestañas
notebook = ttk.Notebook(ventana)
notebook.pack(fill='both', expand=True)

# Crear las pestañas
tab1 = ttk.Frame(notebook)
tab2 = ttk.Frame(notebook)

notebook.add(tab1, text="Ingresar Datos")
notebook.add(tab2, text="Resultados")

# Configurar la primera pestaña (Ingreso de datos)
tk.Label(tab1, text="Alto (m):").grid(row=0, column=0, padx=10, pady=10, sticky="e")
entry_alto = tk.Entry(tab1)
entry_alto.grid(row=0, column=1, padx=10, pady=10)

tk.Label(tab1, text="Ancho (m):").grid(row=1, column=0, padx=10, pady=10, sticky="e")
entry_ancho = tk.Entry(tab1)
entry_ancho.grid(row=1, column=1, padx=10, pady=10)

tk.Label(tab1, text="Largo (m):").grid(row=2, column=0, padx=10, pady=10, sticky="e")
entry_largo = tk.Entry(tab1)
entry_largo.grid(row=2, column=1, padx=10, pady=10)

tk.Label(tab1, text="Peralte (m):").grid(row=3, column=0, padx=10, pady=10, sticky="e")
entry_peralte = tk.Entry(tab1)
entry_peralte.grid(row=3, column=1, padx=10, pady=10)

# Botón para enviar los datos
btn_enviar = tk.Button(tab1, text="Enviar", command=enviar_datos)
btn_enviar.grid(row=4, column=0, columnspan=2, pady=20)

# Configurar la segunda pestaña (Resultados)
resultado_text = tk.Text(tab2, wrap=tk.WORD, font=("Arial", 12), height=20, width=50)
resultado_text.pack(pady=10, padx=10)

# Iniciar el bucle principal
ventana.mainloop()
