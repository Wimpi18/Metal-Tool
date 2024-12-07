import tkinter as tk
from tkinter import ttk
from gui.tabs import configurar_tabs

def iniciar_aplicacion():
    ventana = tk.Tk()
    ventana.title("Ingreso de Dimensiones del Galpón")
    ventana.geometry("500x400")
    
    notebook = ttk.Notebook(ventana)
    notebook.pack(fill='both', expand=True)

    configurar_tabs(notebook)
    ventana.mainloop()
