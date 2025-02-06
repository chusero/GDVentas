import tkinter as tk
from tkinter import ttk
import os
from agregar_productos import cargar_productos  # Asegúrate de que esta función esté definida en agregar_productos.py

# Ajustar la ruta relativa al archivo JSON
RUTA_PRODUCTOS = os.path.join(os.path.dirname(__file__), "productos.json")

def mostrar_stock(content_frame):
    # Limpiar el contenido existente del marco
    for widget in content_frame.winfo_children():
        widget.destroy()

    # Cargar productos desde el archivo JSON
    productos = cargar_productos()

    if not productos:
        tk.Label(content_frame, text="No hay productos en stock.").grid(row=0, column=0, pady=10)
        return

    # Crear el contenedor para el título y los filtros
    filtros_frame = tk.Frame(content_frame)
    filtros_frame.grid(row=0, column=0, pady=10, sticky="nsew")
    content_frame.grid_rowconfigure(0, weight=0)  # La primera fila (filtros) no se expande
    content_frame.grid_columnconfigure(0, weight=1)  # La primera columna (filtros) se expande para ocupar todo el ancho

    # Centrar el frame de filtros en el contenido
    filtros_frame.grid_rowconfigure(0, weight=1)
    filtros_frame.grid_columnconfigure(0, weight=1)

    # Crear un frame interno para centrar el contenido
    filtros_inner_frame = tk.Frame(filtros_frame)
    filtros_inner_frame.grid(row=0, column=0, pady=10, padx=10, sticky="w")
    filtros_inner_frame.grid_rowconfigure(0, weight=1)
    filtros_inner_frame.grid_columnconfigure(0, weight=1)

    # Título de la página con diseño
    titulo_label = tk.Label(filtros_inner_frame, text="Stock", font=("Helvetica", 18, "bold"), bg="#4CAF50", fg="white", pady=5, padx=20, relief="ridge", bd=2)
    titulo_label.grid(row=0, column=0, pady=10, columnspan=4, sticky="ew")

    # Añadir separador debajo del título
    separador_titulo = ttk.Separator(filtros_inner_frame, orient='horizontal')
    separador_titulo.grid(row=1, column=0, columnspan=4, sticky="ew")

    # Filtros (centrado)
    tk.Label(filtros_inner_frame, text="Categoría:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
    filtro_categoria_combobox = ttk.Combobox(filtros_inner_frame, values=[""] + [producto["Categoría"] for producto in productos], state="readonly")
    filtro_categoria_combobox.grid(row=2, column=1, padx=5, pady=5, sticky="w")

    # Filtro de productos a repostar
    filtro_repostar_var = tk.BooleanVar()
    filtro_repostar_checkbutton = tk.Checkbutton(filtros_inner_frame, text="Mostrar solo productos a repostar", variable=filtro_repostar_var)
    filtro_repostar_checkbutton.grid(row=2, column=2, padx=5, pady=5, sticky="w")

    # Opción para ordenar alfabéticamente (A-Z)
    ordenar_abc_var = tk.BooleanVar()
    ordenar_abc_checkbutton = tk.Checkbutton(filtros_inner_frame, text="Ordenar productos de A a Z", variable=ordenar_abc_var)
    ordenar_abc_checkbutton.grid(row=2, column=3, padx=5, pady=5, sticky="w")

    # Botón de aplicar filtro (centrado)
    tk.Button(filtros_inner_frame, text="Aplicar Filtro", command=lambda: aplicar_filtro(productos, filtro_categoria_combobox, filtro_repostar_var, ordenar_abc_var)).grid(row=3, column=0, columnspan=4, pady=10)

    # Añadir separador entre los filtros y la tabla
    separador_filtros = ttk.Separator(content_frame, orient='horizontal')
    separador_filtros.grid(row=1, column=0, pady=10, sticky="ew")

    # Crear el lienzo (Canvas) para dibujar la tabla
    canvas = tk.Canvas(content_frame)
    canvas.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
    content_frame.grid_rowconfigure(2, weight=1)  # La fila que contiene la tabla se expande
    content_frame.grid_columnconfigure(0, weight=1)  # La columna que contiene la tabla se expande

    # Añadir una barra de desplazamiento vertical
    scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
    scrollbar.grid(row=2, column=1, sticky="ns")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Crear un frame dentro del canvas para contener las filas
    table_frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=table_frame, anchor="nw")

    # Configuración de las columnas de la tabla
    columns = ["Nombre", "Costo", "Precio", "Cantidad", "Categoría", "Código"]

    # Mostrar las filas de productos
    def mostrar_tabla(productos_a_mostrar):
        # Limpiar las filas existentes de la tabla antes de agregar nuevas
        for widget in table_frame.winfo_children():
            widget.destroy()

        # Calcular el ancho máximo de la columna "Nombre"
        max_nombre_width = max(
            [len(str(producto.get("Nombre", ""))) for producto in productos_a_mostrar] + [len("Nombre")]
        )

        # Crear los encabezados nuevamente con tamaño reducido
        for col_num, col_name in enumerate(columns):
            label = tk.Label(table_frame, text=col_name, font=("Arial", 9, "bold"), anchor="w", bd=1)
            label.grid(row=0, column=col_num, sticky="ew")

        # Insertar los productos en la tabla
        for row_num, producto in enumerate(productos_a_mostrar, start=1):
            fila = [
                producto.get("Nombre", ""),
                producto.get("Costo", ""),
                producto.get("Precio de Venta", ""),
                producto.get("Cantidad", ""),
                producto.get("Categoría", ""),
                producto.get("Código de Barras", "N/A")
            ]

            try:
                cantidad = int(producto.get("Cantidad", "0"))
            except ValueError:
                cantidad = 0

            # Determinar el color de la fila
            color_fondo = "red" if cantidad < 6 else "white"
            color_texto = "white" if cantidad < 6 else "black"

            # Insertar cada valor en la fila y darle el color de fondo
            for col_num, valor in enumerate(fila):
                # Ajustar el ancho de la columna "Nombre" dinámicamente
                if col_num == 0:  # Columna "Nombre"
                    label = tk.Label(table_frame, text=valor, background=color_fondo, foreground=color_texto, anchor="w", width=max_nombre_width, bd=1)
                else:
                    label = tk.Label(table_frame, text=valor, background=color_fondo, foreground=color_texto, anchor="w", width=15, bd=1)
                label.grid(row=row_num, column=col_num, sticky="ew")

        # Actualizar el tamaño del canvas para que se ajuste al contenido
        table_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

    # Filtros
    def aplicar_filtro(productos, filtro_categoria_combobox, filtro_repostar_var, ordenar_abc_var):
        filtro_categoria = filtro_categoria_combobox.get()
        filtro_repostar = filtro_repostar_var.get()
        ordenar_abc = ordenar_abc_var.get()

        productos_filtrados = []

        # Filtrar productos
        for producto in productos:
            if filtro_repostar and int(producto.get("Cantidad", 0)) >= 6:
                continue

            if filtro_categoria and producto.get("Categoría") != filtro_categoria:
                continue

            productos_filtrados.append(producto)

        if ordenar_abc:
            productos_filtrados.sort(key=lambda x: x.get("Nombre", "").lower())

        mostrar_tabla(productos_filtrados)

    # Mostrar todos los productos por defecto
    mostrar_tabla(productos)