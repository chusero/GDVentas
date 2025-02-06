import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

# Ajustar la ruta relativa al archivo JSON
RUTA_PRODUCTOS = os.path.join(os.path.dirname(__file__), "productos.json")

def cargar_productos():
    try:
        with open(RUTA_PRODUCTOS, "r") as archivo:
            return json.load(archivo)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def guardar_productos(productos):
    with open(RUTA_PRODUCTOS, "w") as archivo:
        json.dump(productos, archivo, indent=4)

def modificar_producto(content_frame):
    def abrir_ventana_modificar(producto):
        def guardar_cambios():
            producto["Nombre"] = entry_nombre.get()
            producto["Costo"] = entry_costo.get()
            producto["Precio de Venta"] = entry_precio.get()
            producto["IVA"] = entry_iva.get()
            producto["Moneda"] = combobox_moneda.get()
            producto["Cantidad"] = entry_cantidad.get()
            producto["Categoría"] = combobox_categoria.get()
            producto["Código de Barras"] = entry_codigo.get()

            for i, prod in enumerate(productos):
                if prod["Código de Barras"] == producto["Código de Barras"]:
                    productos[i] = producto
                    break

            guardar_productos(productos)
            actualizar_tabla()
            messagebox.showinfo("Éxito", "Producto modificado correctamente.")
            ventana_modificar.destroy()

        def eliminar_producto():
            if messagebox.askyesno("Eliminar Producto", "¿Estás seguro de que deseas eliminar este producto?"):
                productos.remove(producto)
                guardar_productos(productos)
                actualizar_tabla()
                messagebox.showinfo("Éxito", "Producto eliminado correctamente.")
                ventana_modificar.destroy()

        ventana_modificar = tk.Toplevel(content_frame)
        ventana_modificar.title("Modificar Producto")

        tk.Label(ventana_modificar, text="Nombre").grid(row=0, column=0, padx=5, pady=5)
        entry_nombre = tk.Entry(ventana_modificar)
        entry_nombre.insert(0, producto["Nombre"])
        entry_nombre.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(ventana_modificar, text="Costo").grid(row=1, column=0, padx=5, pady=5)
        entry_costo = tk.Entry(ventana_modificar)
        entry_costo.insert(0, producto["Costo"])
        entry_costo.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(ventana_modificar, text="Precio de Venta").grid(row=2, column=0, padx=5, pady=5)
        entry_precio = tk.Entry(ventana_modificar)
        entry_precio.insert(0, producto["Precio de Venta"])
        entry_precio.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(ventana_modificar, text="IVA").grid(row=3, column=0, padx=5, pady=5)
        entry_iva = tk.Entry(ventana_modificar)
        entry_iva.insert(0, producto["IVA"])
        entry_iva.grid(row=3, column=1, padx=5, pady=5)

        tk.Label(ventana_modificar, text="Moneda").grid(row=4, column=0, padx=5, pady=5)
        combobox_moneda = ttk.Combobox(ventana_modificar, values=["ARS", "USD", "EUR"])
        combobox_moneda.set(producto["Moneda"])
        combobox_moneda.grid(row=4, column=1, padx=5, pady=5)

        tk.Label(ventana_modificar, text="Cantidad").grid(row=5, column=0, padx=5, pady=5)
        entry_cantidad = tk.Entry(ventana_modificar)
        entry_cantidad.insert(0, producto["Cantidad"])
        entry_cantidad.grid(row=5, column=1, padx=5, pady=5)

        tk.Label(ventana_modificar, text="Categoría").grid(row=6, column=0, padx=5, pady=5)
        combobox_categoria = ttk.Combobox(ventana_modificar, values=["Electrónica", "Ropa", "Alimentos"])
        combobox_categoria.set(producto["Categoría"])
        combobox_categoria.grid(row=6, column=1, padx=5, pady=5)

        tk.Label(ventana_modificar, text="Código de Barras").grid(row=7, column=0, padx=5, pady=5)
        entry_codigo = tk.Entry(ventana_modificar)
        entry_codigo.insert(0, producto.get("Código de Barras", ""))
        entry_codigo.grid(row=7, column=1, padx=5, pady=5)

        tk.Button(ventana_modificar, text="Guardar Cambios", command=guardar_cambios).grid(row=8, column=0, columnspan=2, pady=10)
        tk.Button(ventana_modificar, text="Eliminar Producto", command=eliminar_producto, bg="red", fg="white").grid(row=9, column=0, columnspan=2, pady=10)
    
    # Título de la página con diseño
    titulo = tk.Label(content_frame, text="Modificar Producto", font=("Helvetica", 24, "bold"), bg="#4CAF50", fg="white", pady=10, padx=180, relief="ridge", bd=2)
    titulo.pack(pady=10)
    
    def actualizar_tabla():
        for item in tabla_productos.get_children():
            tabla_productos.delete(item)

        busqueda = busqueda_texto.get().lower()
        productos_filtrados = [
            producto for producto in productos
            if busqueda in producto["Nombre"].lower() or
            busqueda in producto["Categoría"].lower() or
            busqueda in producto.get("Código de Barras", "").lower()
        ]

        for idx, producto in enumerate(productos_filtrados):
            tag = "even" if idx % 2 == 0 else "odd"
            tabla_productos.insert(
                "",
                "end",
                values=(
                    producto["Nombre"],
                    producto["Costo"],
                    producto["Precio de Venta"],
                    producto["IVA"],
                    producto["Moneda"],
                    producto["Cantidad"],
                    producto["Categoría"],
                    producto.get("Código de Barras", "N/A"),
                ),
                tags=(tag,),
            )

        # Asignar productos filtrados a una variable global para mantener el contexto
        global productos_mostrados
        productos_mostrados = productos_filtrados

    productos = cargar_productos()
    

    frame_modificar = tk.Frame(content_frame)
    frame_modificar.pack(fill="both", expand=True)


    tk.Label(frame_modificar, text="Buscar por Nombre, Categoría o Código de Barras:").pack(pady=5)

    frame_busqueda = tk.Frame(frame_modificar)
    frame_busqueda.pack(pady=5)

    busqueda_texto = tk.Entry(frame_busqueda)
    busqueda_texto.pack(side="left", padx=5)

    # Asignar evento para búsqueda automática
    busqueda_texto.bind("<KeyRelease>", lambda event: actualizar_tabla())

    columnas = (
        "Nombre",
        "Costo",
        "Precio de Venta",
        "IVA",
        "Moneda",
        "Cantidad",
        "Categoría",
        "Código de Barras",
    )
    tabla_productos = ttk.Treeview(frame_modificar, columns=columnas, show="headings", height=6)

    tabla_productos.place(relx=0.15, rely=0.3, relwidth=0.7, relheight=0.4)

    tabla_productos.tag_configure("even", background="#f0f0f0")
    tabla_productos.tag_configure("odd", background="#ffffff")

    tabla_productos.column("Nombre", width=100)
    tabla_productos.column("Costo", width=50)
    tabla_productos.column("Precio de Venta", width=70)
    tabla_productos.column("IVA", width=30)
    tabla_productos.column("Moneda", width=40)
    tabla_productos.column("Cantidad", width=50)
    tabla_productos.column("Categoría", width=80)
    tabla_productos.column("Código de Barras", width=100)

    for col in columnas:
        tabla_productos.heading(col, text=col, anchor="center")

    tabla_productos.bind("<Double-1>", lambda event: abrir_ventana_modificar(
        productos_mostrados[tabla_productos.index(tabla_productos.selection()[0])]
    ))

    scrollbar_vertical = ttk.Scrollbar(frame_modificar, orient="vertical", command=tabla_productos.yview)
    scrollbar_vertical.place(relx=0.85, rely=0.3, relheight=0.4)
    tabla_productos.configure(yscrollcommand=scrollbar_vertical.set)

    actualizar_tabla()
