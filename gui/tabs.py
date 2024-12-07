import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from logica.validaciones import validar_datos
from logica.calculos import calcular_resultados
from logica.graficos import graficar_estructura_galpon

def configurar_tabs(notebook):
    tab1 = ttk.Frame(notebook)
    tab2 = ttk.Frame(notebook)

    notebook.add(tab1, text="Ingresar Datos")
    notebook.add(tab2, text="Resultados")

    configurar_tab_ingreso(tab1, notebook, tab2)

def configurar_tab_ingreso(tab, notebook, tab_resultados):
    def enviar_datos():
        try:
            # Capturar los datos ingresados
            datos = {
                "alto": float(entry_alto.get()),
                "ancho": float(entry_ancho.get()),
                "largo": float(entry_largo.get()),
                "peralte": float(entry_peralte.get())
            }

            # Validar datos
            validar_datos(datos)

            # Calcular resultados
            resultados, graficos = calcular_resultados(datos)

            # Graficar estructura
            graficar_estructura_galpon(datos, graficos)

            # Mostrar resultados
            mostrar_resultados(tab_resultados, resultados)

            notebook.select(1)
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

    btn_enviar = tk.Button(tab, text="Enviar", command=enviar_datos)
    btn_enviar.grid(row=4, column=0, columnspan=2, pady=20)

def mostrar_resultados(tab, resultados):
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

    # Mostrar cada resultado en una etiqueta
    for linea in resultados:
        tk.Label(scrollable_frame, text=linea, font=("Arial", 12), anchor="w", justify="left").pack(fill='x', padx=5)

