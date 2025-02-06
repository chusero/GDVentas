import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
import json
import os
from datetime import datetime, timedelta

# Ajustar las rutas relativas a los archivos JSON
RUTA_HISTORIAL_PEDIDOS = os.path.join(os.path.dirname(__file__), "historial_pedidos.json")

def cargar_datos(ruta):
    try:
        with open(ruta, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def consultar_pedidos(parent):
    # Limpiar el contenido anterior
    for widget in parent.winfo_children():
        widget.destroy()

    frame = tk.Frame(parent)
    frame.pack(fill="both", expand=True)

    # Título de la lista de pedidos
    tk.Label(frame, text="Consultar Pedidos", font=("Helvetica", 23)).grid(row=0, columnspan=4, pady=10)

    pedidos = cargar_datos(RUTA_HISTORIAL_PEDIDOS)

    # Filtro de fecha
    filtro_frame = tk.Frame(frame)
    filtro_frame.grid(row=1, column=0, columnspan=4, pady=10, sticky="w")

    tk.Label(filtro_frame, text="Filtrar por fecha (desde):").grid(row=0, column=0, pady=10, padx=5, sticky="e")
    fecha_desde = DateEntry(filtro_frame, width=12, date_pattern='dd/mm/yyyy')
    fecha_desde.grid(row=0, column=1, pady=10, padx=5, sticky="w")

    tk.Label(filtro_frame, text="hasta:").grid(row=0, column=2, pady=10, padx=5, sticky="e")
    fecha_hasta = DateEntry(filtro_frame, width=12, date_pattern='dd/mm/yyyy')
    fecha_hasta.grid(row=0, column=3, pady=10, padx=5, sticky="w")

    tk.Button(filtro_frame, text="Filtrar", command=lambda: filtrar_pedidos(fecha_desde, fecha_hasta, tree, pedidos), bg="blue", fg="white").grid(row=0, column=4, pady=10, padx=5, sticky="w")

    # Crear la tabla de pedidos con scrollbars
    columns = ["Fecha", "Proveedor", "Productos"]

    tree_frame = tk.Frame(frame)
    tree_frame.grid(row=2, column=0, columnspan=4, pady=10, sticky="nsew")

    tree_scroll_y = tk.Scrollbar(tree_frame, orient="vertical")
    tree_scroll_y.pack(side="right", fill="y")

    tree_scroll_x = tk.Scrollbar(tree_frame, orient="horizontal")
    tree_scroll_x.pack(side="bottom", fill="x")

    tree = ttk.Treeview(tree_frame, columns=columns, show="headings", yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
    tree.pack(fill="both", expand=True)

    tree_scroll_y.config(command=tree.yview)
    tree_scroll_x.config(command=tree.xview)

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="w", width=tk.font.Font().measure(col))

    for pedido in pedidos:
        tree.insert("", "end", values=[pedido["Fecha"], pedido["Proveedor"], ", ".join([f"{producto['Nombre']} (Cantidad: {producto['Cantidad']})" for producto in pedido["Productos"]])])

    # Ajustar el ancho de las columnas al contenido
    for col in columns:
        max_len = max([len(str(tree.set(item, col))) for item in tree.get_children()]) * 10
        tree.column(col, width=max_len)

    frame.grid_rowconfigure(2, weight=1)
    frame.grid_columnconfigure(0, weight=1)

def filtrar_pedidos(fecha_desde, fecha_hasta, tree, pedidos):
    try:
        fecha_desde_val = datetime.strptime(fecha_desde.get(), "%d/%m/%Y")
        fecha_hasta_val = datetime.strptime(fecha_hasta.get(), "%d/%m/%Y") + timedelta(days=1) - timedelta(seconds=1)

        print(f"Filtrando desde {fecha_desde_val} hasta {fecha_hasta_val}")

        for item in tree.get_children():
            tree.delete(item)

        for pedido in pedidos:
            try:
                fecha_pedido = datetime.strptime(pedido["Fecha"], "%y-%m-%d %H:%M:%S")
                print(f"Evaluando pedido con fecha: {fecha_pedido}")
                if fecha_desde_val <= fecha_pedido <= fecha_hasta_val:
                    tree.insert("", "end", values=[pedido["Fecha"], pedido["Proveedor"], ", ".join([f"{producto['Nombre']} (Cantidad: {producto['Cantidad']})" for producto in pedido["Productos"]])])
            except ValueError as ve:
                print(f"Error al convertir la fecha del pedido: {ve}")
    except Exception as e:
        print(f"Error al filtrar los pedidos: {e}")

