import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

# Ajustar las rutas relativas a los archivos JSON
RUTA_HISTORIAL_PEDIDOS = "historial_pedidos.json"
RUTA_PRODUCTOS = "productos.json"

def cargar_datos(ruta):
    try:
        with open(ruta, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def guardar_datos(ruta, datos):
    with open(ruta, "w") as f:
        json_str = json.dumps(datos, ensure_ascii=False, indent=4)
        f.write(json_str.replace("Categoría", "Categor\u00eda").replace("Código de Barras", "C\u00f3digo de Barras"))

def actualizar_stock(productos):
    stock_actual = cargar_datos(RUTA_PRODUCTOS)

    for producto in productos:
        for item in stock_actual:
            if item["C\u00f3digo de Barras"] == producto["C\u00f3digo de Barras"]:
                item["Cantidad"] = str(int(item["Cantidad"]) + int(producto["Cantidad"]))
                break
        else:
            stock_actual.append(producto)
    
    guardar_datos(RUTA_PRODUCTOS, stock_actual)

def actualizar_estado_pedido(index, nuevo_estado):
    pedidos = cargar_datos(RUTA_HISTORIAL_PEDIDOS)
    pedidos[index]["Estado"] = nuevo_estado
    guardar_datos(RUTA_HISTORIAL_PEDIDOS, pedidos)

def ingreso_pedidos(parent):
    # Limpiar el contenido anterior
    for widget in parent.winfo_children():
        widget.destroy()

    frame = tk.Frame(parent)
    frame.pack(fill="both", expand=True)

    # Título de la lista de pedidos
    tk.Label(frame, text="Ingreso de Pedidos", font=("Helvetica", 16)).grid(row=0, columnspan=4, pady=10)

    pedidos = cargar_datos(RUTA_HISTORIAL_PEDIDOS)

    # Crear la tabla de pedidos con scrollbars
    columns = ["Fecha", "Proveedor", "Productos", "Estado"]

    tree_frame = tk.Frame(frame)
    tree_frame.grid(row=1, column=0, columnspan=4, pady=10, sticky="nsew")

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

    def color_fila(estado):
        if estado == "Llegó":
            return "lightgreen"
        elif estado == "En Espera":
            return "lightyellow"
        elif estado == "Cancelado":
            return "lightcoral"
        return "white"

    for i, pedido in enumerate(pedidos):
        estado = pedido.get("Estado", "En Espera")
        tree.insert("", "end", values=[pedido["Fecha"], pedido["Proveedor"], ", ".join([f"{producto['Nombre']} (Cantidad: {producto['Cantidad']})" for producto in pedido["Productos"]]), estado], tags=(estado,))

    # Ajustar el ancho de las columnas al contenido
    for col in columns:
        max_len = max([len(str(tree.set(item, col))) for item in tree.get_children()]) * 10
        tree.column(col, width=max_len)

    for estado in ["Llegó", "En Espera", "Cancelado"]:
        tree.tag_configure(estado, background=color_fila(estado))

    frame.grid_rowconfigure(1, weight=1)
    frame.grid_columnconfigure(0, weight=1)

    def confirmar_estado():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Por favor, selecciona un pedido.")
            return

        for item in selected_item:
            estado = tree.set(item, "Estado")
            if estado != "En Espera":
                messagebox.showwarning("Advertencia", "Este pedido ya ha sido actualizado.")
                return

            # Obtener los productos del pedido seleccionado
            index = tree.index(item)
            pedido = pedidos[index]
            productos_pedido = pedido["Productos"]

            # Crear una nueva ventana para confirmar los productos llegados
            confirmacion_ventana = tk.Toplevel(frame)
            confirmacion_ventana.title("Confirmar Productos Llegados")

            # Lista para almacenar los estados de los checkboxes
            productos_llegados = [tk.BooleanVar(value=True) for _ in productos_pedido]

            # Mostrar los productos con checkboxes
            for i, producto in enumerate(productos_pedido):
                producto_frame = tk.Frame(confirmacion_ventana)
                producto_frame.pack(fill="x", padx=10, pady=5)
                tk.Checkbutton(producto_frame, text=f"{producto['Nombre']} (Cantidad: {producto['Cantidad']})", variable=productos_llegados[i]).pack(side="left")

            def guardar_confirmacion():
                # Filtrar los productos que llegaron
                productos_confirmados = [producto for producto, llegado in zip(productos_pedido, productos_llegados) if llegado.get()]
                
                # Actualizar el stock solo para los productos confirmados
                actualizar_stock(productos_confirmados)
                
                # Cambiar el estado del pedido a "Llegó"
                actualizar_estado_pedido(index, "Llegó")
                tree.set(item, "Estado", "Llegó")
                tree.item(item, tags=("Llegó",))
                
                confirmacion_ventana.destroy()
                messagebox.showinfo("Información", "Stock actualizado exitosamente.")

            # Botón para guardar la confirmación
            tk.Button(confirmacion_ventana, text="Guardar", command=guardar_confirmacion).pack(pady=10)

    tk.Button(frame, text="Llegó el pedido", command=confirmar_estado, bg="green", fg="white").grid(row=2, column=0, columnspan=4, pady=10)