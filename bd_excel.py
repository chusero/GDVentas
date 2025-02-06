import csv
from tkinter import filedialog, messagebox
import json
import traceback

def leer_csv_y_agregar_a_json():
    try:
        # Seleccionar archivo CSV
        ruta_csv = filedialog.askopenfilename(
            title="Seleccionar archivo CSV",
            filetypes=[("Archivos CSV", "*.csv")]
        )
        if not ruta_csv:
            return  # Usuario canceló

        # Seleccionar archivo JSON
        ruta_json = filedialog.askopenfilename(
            title="Seleccionar productos.json",
            filetypes=[("Archivos JSON", "*.json")]
        )
        if not ruta_json:
            return  # Usuario canceló

        # Leer archivo CSV con delimitador ";"
        nuevos_productos = []
        with open(ruta_csv, "r", encoding="utf-8") as f:
            lector = csv.DictReader(f, delimiter=";")
            for fila in lector:
                producto = {
                    "Nombre": fila["nombre"],
                    "Costo": fila["PrecioCompra"],
                    "Precio de Venta": fila["PrecioVenta"],
                    "IVA": fila["AlicuotaIva"],
                    "Moneda": "ARS",
                    "Cantidad": fila["Stock"],
                    "Categoría": fila["categoria"],
                    "Código de Barras": fila["Codigo de barra"]
                }
                nuevos_productos.append(producto)

        # Cargar y actualizar JSON
        with open(ruta_json, "r", encoding="utf-8") as f:
            productos = json.load(f)
        productos.extend(nuevos_productos)
        with open(ruta_json, "w", encoding="utf-8") as f:
            json.dump(productos, f, indent=4)

        messagebox.showinfo("Éxito", "Datos importados correctamente!")

    except Exception as e:
        error_msg = f"Error al importar datos:\n{str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        print(error_msg)
        messagebox.showerror("Error crítico", error_msg)