import tkinter as tk
from tkinter import ttk, messagebox
from logica.validaciones import validar_datos
from logica.calculos import calcular_resultados, calcular_costos_totales
from logica.graficos import graficar_estructura_galpon
import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import ast

# Valores predeterminados de costos unitarios
COSTOS_POR_DEFECTO = {
    "mh4": 13910.20,  # Costo unitario de perfil HEB 400 ($/m)
    "mh3": 9836.69,  # Costo unitario de perfil HEB 300 ($/m)
    "mc": 933.67,    # Costo unitario de perfil C ($/m)
    "ma": 2815.44     # Costo unitario de pernos de anclaje ($/unidad)
}

def configurar_tabs(notebook):
    tab1 = ttk.Frame(notebook)
    tab2 = ttk.Frame(notebook)
    tab3 = ttk.Frame(notebook)

    notebook.add(tab1, text="Ingresar Datos")
    notebook.add(tab3, text="Configurar Costos")
    notebook.add(tab2, text="Resultados")

    costos_actuales = COSTOS_POR_DEFECTO.copy()

    configurar_tab_ingreso(tab1, notebook, tab2, costos_actuales)
    configurar_tab_costos(tab3, costos_actuales)

def configurar_tab_ingreso(tab, notebook, tab_resultados, costos_actuales):
    def enviar_datos():
        try:
            # Capturar los datos ingresados
            datos = {
                "alto": float(entry_alto.get()),
                "ancho": float(entry_ancho.get()),
                "largo": float(entry_largo.get()),
                "peralte": float(entry_peralte.get()),
                "longitudBase": float(entry_longitudBase.get())
            }

            # Validar datos
            validar_datos(datos)

            # Calcular resultados
            resultados, graficos = calcular_resultados(datos)

            # Calcular costos totales
            costos = calcular_costos_totales(resultados, costos_actuales, datos["longitudBase"])
            resultados.extend(costos)

            # Graficar estructura
            graficar_estructura_galpon(datos, graficos)

            # Mostrar resultados
            mostrar_resultados(tab_resultados, resultados, datos["longitudBase"])

            notebook.select(2)
        except ValueError as e:
            messagebox.showerror("Error", f"Entrada inválida: {e}")

    tk.Label(tab, text="Alto (m):").grid(row=0, column=0, padx=10, pady=10, sticky="e")
    entry_alto = tk.Entry(tab)
    entry_alto.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(tab, text="Ancho (m):").grid(row=1, column=0, padx=10, pady=10, sticky="e")
    entry_ancho = tk.Entry(tab)
    entry_ancho.grid(row=1, column=1, padx=10, pady=10)

    tk.Label(tab, text="Largo (m):").grid(row=2, column=0, padx=10, pady=10, sticky="e")
    entry_largo = tk.Entry(tab)
    entry_largo.grid(row=2, column=1, padx=10, pady=10)

    tk.Label(tab, text="Peralte (m):").grid(row=3, column=0, padx=10, pady=10, sticky="e")
    entry_peralte = tk.Entry(tab)
    entry_peralte.grid(row=3, column=1, padx=10, pady=10)
    
    tk.Label(tab, text="Longitud base de perfil HEB300 (m):").grid(row=4, column=0, padx=10, pady=10, sticky="e")
    entry_longitudBase = tk.Entry(tab)
    entry_longitudBase.grid(row=4, column=1, padx=10, pady=10)

    btn_enviar = tk.Button(tab, text="Enviar", command=enviar_datos)
    btn_enviar.grid(row=5, column=0, columnspan=2, pady=20)

def configurar_tab_costos(tab, costos_actuales):
    entradas_costos = {}

    def actualizar_costos():
        for clave, entrada in entradas_costos.items():
            try:
                costos_actuales[clave] = float(entrada.get())
            except ValueError:
                messagebox.showerror("Error", f"El costo de {clave} no es válido.")
                return
        messagebox.showinfo("Éxito", "Costos actualizados correctamente.")

    def restablecer_costos():
        for clave, valor in COSTOS_POR_DEFECTO.items():
            costos_actuales[clave] = valor
            entradas_costos[clave].delete(0, tk.END)
            entradas_costos[clave].insert(0, f"{valor:.2f}")
        messagebox.showinfo("Éxito", "Costos restablecidos a los valores predeterminados.")

    tk.Label(tab, text="Configurar Costos Unitarios ($):", font=("Arial", 14, "bold")).pack(pady=10)
    frame_costos = ttk.Frame(tab)
    frame_costos.pack(pady=10)

    row = 0
    for clave, valor in COSTOS_POR_DEFECTO.items():
        tk.Label(frame_costos, text=f"{clave}:").grid(row=row, column=0, padx=10, pady=5, sticky="e")
        entrada = tk.Entry(frame_costos)
        entrada.grid(row=row, column=1, padx=10, pady=5)
        entrada.insert(0, f"{valor:.2f}")
        entradas_costos[clave] = entrada
        row += 1

    tk.Button(tab, text="Actualizar Costos", command=actualizar_costos).pack(pady=10)
    tk.Button(tab, text="Restablecer Valores Predeterminados", command=restablecer_costos).pack(pady=10)

def mostrar_resultados(tab, resultados, longitudBase):

    # Limpiar el contenido del tab
    for widget in tab.winfo_children():
        widget.destroy()
    # Crear un marco de desplazamiento
    canvas = tk.Canvas(tab)
    scrollbar = tk.Scrollbar(tab, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    # Título para los resultados
    tk.Label(scrollable_frame, text="Resultados:", font=("Arial", 14, "bold")).pack(pady=(0, 10))
    # Crear un contenedor para tablas
    table_frame = tk.Frame(scrollable_frame)
    table_frame.pack(fill="both", expand=True)
    # Tablas anteriores (Pilares, Cerchas y Costos)
    ttk.Label(table_frame, text="Detalles de pilares y costaneras", font=("Arial", 12, "bold")).pack(pady=(10, 5))
    tree_pilares = ttk.Treeview(table_frame, columns=("Elemento", "Cantidad", "Longitud"), show="headings")
    tree_pilares.pack(fill="x", padx=10, pady=5)
    tree_pilares.heading("Elemento", text="Elemento")
    tree_pilares.heading("Cantidad", text="Cantidad")
    tree_pilares.heading("Longitud", text="Longitud (m)")
    tree_pilares.insert("", "end", values=("Pilares HEB400", extraerDato(resultados[0]), extraerDato(resultados[1])))
    tree_pilares.insert("", "end", values=("Costaneras C", extraerDato(resultados[3]), extraerDato(resultados[4])))
    ttk.Label(table_frame, text="Detalles de cerchas", font=("Arial", 12, "bold")).pack(pady=(10, 5))
    tree_cerchas = ttk.Treeview(table_frame, columns=("Elemento", "Cantidad", "Longitud"), show="headings")
    tree_cerchas.pack(fill="x", padx=10, pady=5)
    cerchas_datos = [
        ("Vigas HEB300", extraerDato(resultados[7]), extraerDato(resultados[8])),
        ("Tirantes HEB300", extraerDato(resultados[10]), extraerDato(resultados[11])),
        ("Pendolones HEB300", extraerDato(resultados[13]), extraerDato(resultados[14])),
        ("Montantes HEB300", extraerDato(resultados[16]), extraerDato(resultados[17])),
        ("Tornapuntas HEB300", extraerDato(resultados[19]), extraerDato(resultados[20]))
    ]
    for dato in cerchas_datos:
        tree_cerchas.insert("", "end", values=dato)
    ttk.Label(table_frame, text="Costos", font=("Arial", 12, "bold")).pack(pady=(10, 5))
    tree_costos = ttk.Treeview(table_frame, columns=("Descripción", "Costo ($)"), show="headings")
    tree_costos.pack(fill="x", padx=10, pady=5)
    costos_datos = [
        ("Pilares HEB400", extraerDato(resultados[22])),
        ("Costaneras C", extraerDato(resultados[23])),
        ("Pernos de anclaje", extraerDato(resultados[24])),
        ("Cerchas HEB300", extraerDato(resultados[25])),
        ("Costo total galpón", extraerDato(resultados[26]))
    ]
    for dato in costos_datos:
        tree_costos.insert("", "end", values=dato)
    # Tabla para simulación de cortes
    ttk.Label(table_frame, text="Simulación de cortes", font=("Arial", 12, "bold")).pack(pady=(10, 5))
    tree_cortes = ttk.Treeview(table_frame, columns=("Descripción", "Cantidad"), show="headings")
    tree_cortes.pack(fill="x", padx=10, pady=5)
    cortes_datos = [
        ("Barras utilizadas", extraerDato(resultados[29]))
    ]
    for i in range(32, len(resultados)):
        if i == len(resultados) - 2:
            continue
        cortes_datos.append((extraerLlave(resultados[i]), extraerDato(resultados[i])))

    for dato in cortes_datos:
        tree_cortes.insert("", "end", values=dato)
    # Gráfico de simulación de cortes
    ttk.Label(table_frame, text="Visualización de Simulación de Cortes", font=("Arial", 12, "bold")).pack(pady=(10, 5))
    marco_grafico = tk.Frame(table_frame)
    marco_grafico.pack(pady=10)
    # Datos del gráfico
    combinaciones = extraerCombinaciones(resultados)
    longitud_base = longitudBase  # Longitud base de la barra
    # Crear la figura
    fig = Figure(figsize=(8, len(combinaciones) * 2))
    ax = fig.add_subplot(111)
    y_labels = []
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    for idx, combinacion in enumerate(reversed(combinaciones)):
        patron = combinacion["patrón"]
        barras = combinacion["barras"]
        y_labels.append(f"Patrón {idx + 1}: {barras} barras")
        start = 0
        for segment_idx, longitud in enumerate(patron):
            ax.barh(idx, longitud, left=start, color=colors[segment_idx % len(colors)], edgecolor='black')
            start += longitud
        desperdicio = longitud_base - sum(patron)
        ax.barh(idx, desperdicio, left=start, color='gray', edgecolor='black')
    ax.set_yticks(range(len(combinaciones)))
    ax.set_yticklabels(y_labels)
    ax.set_xlabel("Longitud (m)")
    ax.set_title("Simulación de Cortes")
    # Incrustar la gráfica en Tkinter
    canvas_grafico = FigureCanvasTkAgg(fig, master=marco_grafico)
    canvas_grafico.draw()
    canvas_grafico.get_tk_widget().pack()

def extraerLlave(resultado:str):
    return resultado.split(':')[0].strip()

def extraerDato(resultado:str):
    return resultado.split(':')[1].strip()

def extraerCombinaciones(resultados):
    combinaciones = []
    
    for i in range(32, len(resultados) - 2):
        # Obtener los patrones
        patronPt1 = extraerLlave(resultados[i]).split(" ")[0].lower()
        patronPt2 = extraerLlave(resultados[i])[7:]
        # Convertir patronPt2 a lista
        patronPt2 = list(ast.literal_eval(patronPt2))
        
        # Obtener las barras
        barrasPt1 = int(extraerDato(resultados[i]).split(" ")[0]) 
        barrasPt2 = extraerDato(resultados[i]).split(" ")[1].lower() 

        
        combinaciones.append({patronPt1: patronPt2, barrasPt2: barrasPt1})
    
    return combinaciones
