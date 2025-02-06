import tkinter as tk
from tkinter import ttk
import json
import os
from datetime import datetime

# Ajustar las rutas relativas a los archivos JSON
RUTA_FACTURAS = os.path.join(os.path.dirname(__file__), "facturas.json")

def cargar_datos(ruta):
    try:
        with open(ruta, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def guardar_datos(ruta, datos):
    with open(ruta, "w") as f:
        json.dump(datos, f, indent=4)

def generar_factura(productos_vendidos):
    factura = {
        "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Productos": productos_vendidos,
        "Total": sum(float(producto["subtotal"]) for producto in productos_vendidos)
    }
    facturas = cargar_datos(RUTA_FACTURAS)
    facturas.append(factura)
    guardar_datos(RUTA_FACTURAS, facturas)
    return factura

def previsualizar_factura(factura):
    ventana = tk.Toplevel()
    ventana.title("Previsualización de Factura")

    tk.Label(ventana, text="Factura", font=("Helvetica", 16)).pack(pady=10)

    columnas = ["Producto", "Cantidad", "Precio Unitario", "Subtotal"]

    tree = ttk.Treeview(ventana, columns=columnas, show="headings")
    tree.pack(fill="both", expand=True)

    for col in columnas:
        tree.heading(col, text=col)
        tree.column(col, anchor="w")

    for producto in factura["Productos"]:
        nombre = producto["Nombre"]
        cantidad = int(producto["cantidad"])
        precio_unitario = float(producto["precio"])
        subtotal = float(producto["subtotal"])
        tree.insert("", "end", values=[nombre, cantidad, precio_unitario, subtotal])

    tk.Label(ventana, text=f"Total: ${factura['Total']:.2f}", font=("Helvetica", 14)).pack(pady=10)

    tk.Button(ventana, text="Cerrar", command=ventana.destroy).pack(pady=10)

# Ejemplo de cómo llamar la generación de factura
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Generar Factura")
    root.geometry("800x600")

    productos_vendidos = [
        {"Nombre": "medias", "cantidad": "2", "precio": "100", "subtotal": "200"},
        {"Nombre": "pantalon", "cantidad": "1", "precio": "500", "subtotal": "500"}
    ]

    factura = generar_factura(productos_vendidos)
    previsualizar_factura(factura)

    root.mainloop()
