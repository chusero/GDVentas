import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

# Ruta al archivo JSON donde se almacenan los productos
RUTA_PRODUCTOS = os.path.join(os.path.dirname(__file__), "productos.json")

# Función para cargar productos desde el archivo JSON
def cargar_productos():
    try:
        with open(RUTA_PRODUCTOS, "r") as archivo:
            return json.load(archivo)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Función para guardar productos en el archivo JSON
def guardar_productos(productos):
    with open(RUTA_PRODUCTOS, "w") as archivo:
        json.dump(productos, archivo, indent=4)

# Función para agregar un producto
def agregar_producto(content_frame):
    # Limpiar el content_frame para evitar duplicados
    for widget in content_frame.winfo_children():
        widget.destroy()

    # Título "Agregar Producto"
       # Título de la página con diseño
    titulo_label = tk.Label(content_frame, text="Agregar Producto", font=("Helvetica", 24, "bold"), bg="#4CAF50", fg="white", pady=10, padx=10, relief="ridge", bd=2)
    titulo_label.grid(row=0, column=0, pady=10, columnspan=4, sticky="nsew")

    # Cargar productos existentes para obtener las categorías
    productos = cargar_productos()
    categorias = set([producto["Categoría"] for producto in productos])  # Obtener categorías únicas

    # Campos del formulario
    fields = {
        "Nombre": tk.Entry(content_frame, width=30),
        "Costo": tk.Entry(content_frame, width=30),
        "Precio de Venta": tk.Entry(content_frame, width=30),
        "IVA": tk.Entry(content_frame, width=5),
        "Moneda": ttk.Combobox(content_frame, values=["ARS", "USD", "EUR"], width=27),
        "Cantidad": tk.Entry(content_frame, width=30),
        "Categoría": ttk.Combobox(content_frame, values=list(categorias), state="normal", width=27),
        "Código de Barras": tk.Entry(content_frame, width=30),  # Nuevo campo para código de barras
    }

    # Crear los campos del formulario en el content_frame
    row = 3  # Comenzamos desde la segunda fila para dejar espacio para el título
    for label, entry in fields.items():
        tk.Label(content_frame, text=label, anchor="w").grid(row=row, column=0, padx=5, pady=5, sticky="w")
        entry.grid(row=row, column=1, padx=5, pady=5, sticky="w")  # Usamos "w" para que los campos no se expandan
        row += 1

    # Valor predeterminado para la combobox de Moneda
    fields["Moneda"].set("ARS")

    # Crear la tabla de productos (debajo del formulario)
    columnas = ("Nombre", "Costo", "Precio de Venta", "IVA", "Moneda", "Cantidad", "Categoría", "Código de Barras")
    tabla_productos = ttk.Treeview(content_frame, columns=columnas, show="headings", height=5)

    # Configurar las cabeceras de la tabla
    for col in columnas:
        tabla_productos.heading(col, text=col)

    # Reducir el ancho de las columnas de la tabla
    tabla_productos.column("Nombre", width=100)
    tabla_productos.column("Costo", width=80)
    tabla_productos.column("Precio de Venta", width=100)
    tabla_productos.column("IVA", width=50)
    tabla_productos.column("Moneda", width=60)
    tabla_productos.column("Cantidad", width=70)
    tabla_productos.column("Categoría", width=100)
    tabla_productos.column("Código de Barras", width=120)

    # Colocar la tabla en el content_frame debajo del formulario
    tabla_productos.grid(row=row + 1, column=0, columnspan=2, padx=10, pady=20, sticky="nsew")

    # Función para agregar el producto a la tabla y al archivo JSON
    def guardar():
        producto = {campo: entrada.get() for campo, entrada in fields.items()}

        # Verificar que todos los campos tengan valores
        if all(producto.values()):
            # Guardar el producto en el archivo JSON
            productos = cargar_productos()
            productos.append(producto)
            guardar_productos(productos)

            # Agregar el producto a la tabla
            tabla_productos.insert("", "end", values=( 
                producto["Nombre"],
                producto["Costo"],
                producto["Precio de Venta"],
                producto["IVA"],
                producto["Moneda"],
                producto["Cantidad"],
                producto["Categoría"],
                producto["Código de Barras"]
            ))

            messagebox.showinfo("Éxito", "Producto agregado correctamente.")
            
            # Limpiar los campos del formulario
            for entry in fields.values():
                entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Todos los campos deben ser completados.")

    # Botón "Guardar" se coloca debajo del formulario, entre el formulario y la tabla
    tabla_productos.grid(row=row + 1, column=0, columnspan=2, padx=10, pady=20, sticky="nsew")
    tk.Button(content_frame, text="Guardar", command=guardar,width=10).grid(row=row, column=0, columnspan=1, pady=10,sticky="e")

    # Centrar los elementos dentro del content_frame
    content_frame.grid_columnconfigure(0, weight=0)
    content_frame.grid_columnconfigure(1, weight=1)
