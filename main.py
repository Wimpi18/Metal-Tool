import tkinter as tk
from tkinter import messagebox

def enviar_datos():
    try:
        # Capturar los datos ingresados
        alto = float(entry_alto.get())
        ancho = float(entry_ancho.get())
        largo = float(entry_largo.get())
        peralte = float(entry_peralte.get())
        
        # Validaciones
        if alto < 3 or alto > 18:
            raise ValueError("El alto debe estar entre 3 y 18 metros.")
        if ancho < 6 or ancho > 50:
            raise ValueError("El ancho debe estar entre 6 y 50 metros.")
        if largo < 6 or largo > 100 or largo % 6 != 0:
            raise ValueError("El largo debe estar entre 6 y 100 metros, y ser múltiplo de 6.")
        if peralte <= alto or peralte > alto + 5:
            raise ValueError("El peralte debe ser mayor que el alto y no exceder en más de 5 metros al alto.")
        
        # Mensaje de confirmación
        messagebox.showinfo("Datos enviados", f"Datos ingresados correctamente:\n"
                                              f"Alto: {alto} m\nAncho: {ancho} m\n"
                                              f"Largo: {largo} m\nPeralte: {peralte} m")
    except ValueError as e:
        # Mostrar mensaje de error
        messagebox.showerror("Error", f"Entrada inválida: {e}")

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Ingreso de Dimensiones del Galpón")
ventana.geometry("500x400")

# Etiquetas y campos de entrada
tk.Label(ventana, text="Alto (m):").grid(row=0, column=0, padx=10, pady=10, sticky="e")
entry_alto = tk.Entry(ventana)
entry_alto.grid(row=0, column=1, padx=10, pady=10)

tk.Label(ventana, text="Ancho (m):").grid(row=1, column=0, padx=10, pady=10, sticky="e")
entry_ancho = tk.Entry(ventana)
entry_ancho.grid(row=1, column=1, padx=10, pady=10)

tk.Label(ventana, text="Largo (m):").grid(row=2, column=0, padx=10, pady=10, sticky="e")
entry_largo = tk.Entry(ventana)
entry_largo.grid(row=2, column=1, padx=10, pady=10)

tk.Label(ventana, text="Peralte (m):").grid(row=3, column=0, padx=10, pady=10, sticky="e")
entry_peralte = tk.Entry(ventana)
entry_peralte.grid(row=3, column=1, padx=10, pady=10)

# Botón para enviar los datos
btn_enviar = tk.Button(ventana, text="Enviar", command=enviar_datos)
btn_enviar.grid(row=4, column=0, columnspan=2, pady=20)

# Iniciar el bucle principal
ventana.mainloop()
