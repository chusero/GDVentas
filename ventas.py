import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime
import facturacion
# Ajustar las rutas relativas a los archivos JSON
RUTA_PRODUCTOS = os.path.join(os.path.dirname(__file__), "productos.json")
RUTA_VENTAS = os.path.join(os.path.dirname(__file__), "ventas.json")

# Función para cargar los productos desde productos.json
def obtener_productos():
    try:
        with open(RUTA_PRODUCTOS, "r") as file:
            productos = json.load(file)
        return productos
    except FileNotFoundError:
        messagebox.showerror("Error", "El archivo productos.json no se encuentra.")
        return []
    except json.JSONDecodeError:
        messagebox.showerror("Error", "Error al leer el archivo productos.json.")
        return []

# Función para guardar cambios en productos.json
def guardar_productos(productos):
    try:
        with open(RUTA_PRODUCTOS, "w") as file:
            json.dump(productos, file, indent=4)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar los cambios: {e}")

# Función para obtener las ventas desde ventas.json
def obtener_ventas():
    try:
        with open(RUTA_VENTAS, "r") as file:
            ventas = json.load(file)
        return ventas
    except FileNotFoundError:
        return []  # Si el archivo no existe, retornamos una lista vacía
    except json.JSONDecodeError:
        messagebox.showerror("Error", "Error al leer el archivo ventas.json.")
        return []

# Función para guardar ventas en ventas.json
def guardar_ventas(nueva_venta):
    try:
        ventas = obtener_ventas()
        ventas.append(nueva_venta)
        with open(RUTA_VENTAS, "w") as file:
            json.dump(ventas, file, indent=4)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar la venta: {e}")

# Función para buscar productos
def buscar_producto(query):
    resultados = []
    productos = obtener_productos()
    for producto in productos:
        nombre = producto.get("Nombre", "").lower()
        codigo_barras = producto.get("Código de Barras", "").lower()
        if query.lower() in nombre or query.lower() in codigo_barras:
            resultados.append(producto)
    return resultados

def realizar_venta(content_frame):
    for widget in content_frame.winfo_children():
        widget.destroy()

    titulo_label = tk.Label(content_frame, text="Realizar Venta", font=("Helvetica", 24, "bold"), bg="#4CAF50", fg="white")
    titulo_label.pack(pady=10, padx=10)

    # Variables
    busqueda_var = tk.StringVar()
    total_var = tk.DoubleVar(value=0.0)

    # Entrada de búsqueda
    busqueda_entry = tk.Entry(content_frame, textvariable=busqueda_var, font=("Arial", 12))
    busqueda_entry.pack(pady=10)

    # Listbox de sugerencias
    sugerencias_listbox = tk.Listbox(content_frame, height=5, font=("Arial", 12))
    sugerencias_listbox.pack(pady=5, fill="x")

    # Tabla de ventas
    columnas_venta = ["Producto", "Precio", "Cantidad", "Total"]
    venta_lista = ttk.Treeview(content_frame, columns=columnas_venta, show="headings", height=10)
    for col in columnas_venta:
        venta_lista.heading(col, text=col)
        venta_lista.column(col, width=200)
    venta_lista.pack(pady=10, fill="both", expand=True)

    # Función para mantener el foco en el campo de búsqueda
    def mantener_foco(event=None):
        busqueda_entry.focus_set()

    # Actualizar sugerencias
    def actualizar_sugerencias(event=None):
        query = busqueda_var.get()
        sugerencias_listbox.delete(0, tk.END)
        if not query:
            mantener_foco()
            return
        productos_encontrados = buscar_producto(query)
        for producto in productos_encontrados:
            sugerencias_listbox.insert(tk.END, producto["Nombre"])
        mantener_foco()

    # Seleccionar sugerencia con Enter
    def seleccionar_sugerencia_con_enter(event):
        seleccion = sugerencias_listbox.curselection()
        if seleccion:
            busqueda_var.set(sugerencias_listbox.get(seleccion[0]))
            sugerencias_listbox.delete(0, tk.END)
            mantener_foco()  # Forzar el foco en el campo de búsqueda después de seleccionar

    # Vincular la tecla Enter a la selección de sugerencias
    sugerencias_listbox.bind("<Return>", seleccionar_sugerencia_con_enter)

    # Función para buscar y agregar productos
    def buscar_y_agregar_producto():
        query = busqueda_var.get()
        if not query:
            confirmar_venta()
            return
        productos_encontrados = buscar_producto(query)
        mantener_foco()
        # Verificar coincidencias exactas
        producto = next((p for p in productos_encontrados if p["Nombre"].lower() == query.lower() or p["Código de Barras"].lower() == query.lower()), None)

        if not producto:
            messagebox.showinfo("No encontrado", "No se encontró el producto.")
            mantener_foco()
            return

        busqueda_var.set("")  # Limpia el campo de búsqueda
        sugerencias_listbox.delete(0, tk.END)  # Limpia las sugerencias

        for item in venta_lista.get_children():
            item_valores = venta_lista.item(item, 'values')
            if item_valores[0] == producto["Nombre"]:
                nueva_cantidad = int(item_valores[2]) + 1
                nuevo_total = nueva_cantidad * float(item_valores[1])
                venta_lista.item(item, values=(item_valores[0], item_valores[1], nueva_cantidad, nuevo_total))
                actualizar_total()
                mantener_foco()
                return

        total = float(producto["Precio de Venta"])
        venta_lista.insert("", "end", values=(producto["Nombre"], producto["Precio de Venta"], 1, total))
        actualizar_total()
        mantener_foco()

    # Función para actualizar el total
    def actualizar_total():
        total = 0.0
        for item in venta_lista.get_children():
            total += float(venta_lista.item(item, 'values')[3])
        total_var.set(total)

    # Confirmar venta
    def confirmar_venta():
        if not venta_lista.get_children():
            messagebox.showinfo("Venta Vacía", "No hay productos en la venta.")
            return
        mostrar_detalles_venta()

    # Mostrar ventana emergente de detalles de la venta
    def mostrar_detalles_venta():
        detalles_ventana = tk.Toplevel()
        detalles_ventana.title("Detalles de la Venta")
        total = total_var.get()

        # Total de la venta
        tk.Label(detalles_ventana, text=f"Total de la venta: ${total:.2f}", font=("Arial", 12)).grid(row=0, column=0, sticky="w", padx=10, pady=5)

        # Monto con el que paga el cliente
        pago_var = tk.DoubleVar(value=total)  # Inicializar con el total de la venta
        tk.Label(detalles_ventana, text="Monto con el que paga el cliente:", font=("Arial", 12)).grid(row=1, column=0, sticky="w", padx=10, pady=5)
        pago_entry = tk.Entry(detalles_ventana, textvariable=pago_var, font=("Arial", 12))
        pago_entry.grid(row=1, column=1, padx=10, pady=5)

        # Función para mostrar el vuelto
        def mostrar_vuelto():
            monto_pagado = pago_var.get()
            if monto_pagado >= total:
                vuelto = monto_pagado - total
                vuelto_label.config(text=f"Vuelto: ${vuelto:.2f}")
            else:
                vuelto_label.config(text="")

        # Etiqueta para el vuelto
        vuelto_label = tk.Label(detalles_ventana, text="Vuelto: $0.00", font=("Arial", 12))
        vuelto_label.grid(row=2, column=0, columnspan=2, sticky="w", padx=10, pady=5)

        # Vincular la función de mostrar el vuelto a cada cambio en el monto
        pago_entry.bind("<KeyRelease>", lambda event: mostrar_vuelto())

        # Confirmar pago
        def confirmar_pago():
            monto_pagado = pago_var.get()
            if monto_pagado < total_var.get():
                messagebox.showerror("Pago Insuficiente", "El monto con el que paga el cliente es insuficiente.")
                return

            productos = obtener_productos()  # Cargar productos de productos.json
            venta_actual = {
                "productos": [],  # Lista de productos vendidos
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Formato que luego se convert
                "total": total_var.get(),  # Total de la venta
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Fecha y hora de la venta
                "cliente": "Cliente X",  # Puedes adaptar esta parte si tienes sistema de clientes
                "IVA": 0.0  # IVA total de la venta
            }

            # Procesar cada producto en la lista de ventas
            for item in venta_lista.get_children():
                producto_vendido = venta_lista.item(item, 'values')
                nombre_vendido = producto_vendido[0]  # Nombre del producto
                precio_vendido = float(producto_vendido[1])  # Precio unitario
                cantidad_vendida = int(producto_vendido[2])  # Cantidad vendida
                subtotal_vendido = float(producto_vendido[3])  # Subtotal del producto

                # Buscar el IVA correspondiente al producto
                iva_producto = 0
                for producto in productos:
                    if producto["Nombre"] == nombre_vendido:
                        iva_producto = float(producto.get("IVA", 0))  # Tomar IVA desde productos.json

                # Registrar el producto vendido
                producto_registro = {
                    "Nombre": nombre_vendido,
                    "precio": precio_vendido,
                    "cantidad": cantidad_vendida,
                    "subtotal": subtotal_vendido,
                    "IVA": iva_producto
                }
                venta_actual["productos"].append(producto_registro)  # Agregar producto a la lista

                # Sumar al total del IVA de la venta
                venta_actual["IVA"] += subtotal_vendido * iva_producto / 100

                # Actualizar el stock
                for producto in productos:
                    if producto["Nombre"] == nombre_vendido:
                        producto["Cantidad"] = str(int(producto["Cantidad"]) - cantidad_vendida)
                        if int(producto["Cantidad"]) < 0:
                            messagebox.showerror("Error", f"No hay suficiente stock de {nombre_vendido}.")
                            return

            # Guardar la venta en ventas.json
            guardar_ventas(venta_actual)
            facturacion.iniciar_proceso_facturacion(venta_actual)
            # Limpiar la tabla de ventas y reiniciar el total
            venta_lista.delete(*venta_lista.get_children())
            total_var.set(0.0)

            # Confirmar al usuario que la venta fue registrada
            vuelto = monto_pagado - total_var.get()
            messagebox.showinfo("Venta Confirmada", f"Venta realizada por un total de ${total_var.get():.2f}\nMonto con el que paga el cliente: ${monto_pagado:.2f}\nVuelto: ${vuelto:.2f}")
            detalles_ventana.destroy()

            # Guardar los productos actualizados
            guardar_productos(productos)

        # Botones
        tk.Button(detalles_ventana, text="Confirmar", font=("Arial", 12), command=confirmar_pago, bg="green", fg="white").grid(row=3, column=0, padx=10, pady=10)
        detalles_ventana.focus_set()

        detalles_ventana.mainloop()

    # Configuración de los frames
    total_frame = tk.Frame(content_frame)
    total_frame.pack(side="right", anchor="ne", padx=10, pady=10, fill="x")

    # Etiqueta total
    total_label = tk.Label(total_frame, text="Total: $", font=("Arial", 14))
    total_label.grid(row=4, column=0, padx=10)

    # Campo de texto para el total
    total_field = tk.Entry(total_frame, textvariable=total_var, font=("Arial", 14), state="readonly")
    total_field.grid(row=4, column=1, padx=10)

    # Eliminar producto seleccionado
    def eliminar_producto(event=None):
        selected_item = venta_lista.selection()
        if not selected_item:
            return
        for item in selected_item:
            venta_lista.delete(item)
        actualizar_total()
        mantener_foco()

    # Asociar eventos
    busqueda_entry.bind("<Return>", lambda event: buscar_y_agregar_producto())
    mantener_foco()

    # Crear un frame para los botones
    botones_frame = tk.Frame(content_frame)
    botones_frame.pack(fill="x", pady=10)

    # Botones para confirmar y eliminar
    confirmar_button = tk.Button(botones_frame, text="Confirmar Venta", font=("Arial", 12), command=confirmar_venta, bg="green", fg="white", height=2)
    confirmar_button.pack(side="left", fill="both", expand=True)

    eliminar_button = tk.Button(botones_frame, text="Eliminar Producto", font=("Arial", 12), command=eliminar_producto, bg="red", fg="white", height=2)
    eliminar_button.pack(side="left", fill="both", expand=True)

    # Función para seleccionar cantidad al presionar Enter en la tabla
    def seleccionar_cantidad(event):
        selected_item = venta_lista.selection()
        if not selected_item:
            return
        item = selected_item[0]
        item_valores = venta_lista.item(item, 'values')

        # Crear ventana para ingresar cantidad
        cantidad_ventana = tk.Toplevel()
        cantidad_ventana.title("Seleccionar Cantidad")

        tk.Label(cantidad_ventana, text="Cantidad:", font=("Arial", 12)).pack(pady=10)
        cantidad_var = tk.IntVar(value=int(item_valores[2]))
        cantidad_entry = tk.Entry(cantidad_ventana, textvariable=cantidad_var, font=("Arial", 12))
        cantidad_entry.pack(pady=10)

        def confirmar_cantidad():
            nueva_cantidad = cantidad_var.get()
            nuevo_total = nueva_cantidad * float(item_valores[1])
            venta_lista.item(item, values=(item_valores[0], item_valores[1], nueva_cantidad, nuevo_total))
            actualizar_total()
            cantidad_ventana.destroy()
            mantener_foco()

        tk.Button(cantidad_ventana, text="Confirmar", command=confirmar_cantidad, font=("Arial", 12), bg="green", fg="white").pack(pady=10)
        cantidad_entry.bind("<Return>", lambda event: confirmar_cantidad())
        cantidad_entry.focus_set()

    # Eventos
    busqueda_entry.bind("<KeyRelease>", actualizar_sugerencias)
    mantener_foco()

    # Asociar evento Enter a la tabla de ventas
    venta_lista.bind("<Return>", seleccionar_cantidad)

    # Forzar el foco en el campo de búsqueda después de cualquier interacción
    content_frame.bind("<Button-1>", mantener_foco)
    sugerencias_listbox.bind("<Button-1>", mantener_foco)
    venta_lista.bind("<Button-1>", mantener_foco)