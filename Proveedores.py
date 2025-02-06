import json
import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import ttk
import os
# Ajustar las rutas relativas a los archivos JSON
RUTA_ALMACEN_PROVEEDORES = os.path.join(os.path.dirname(__file__), "almacen_proveedores.json")
RUTA_PROVEEDORES = os.path.join(os.path.dirname(__file__), "proveedores.json")
RUTA_PEDIDOS = os.path.join(os.path.dirname(__file__), "pedidos.json")
RUTA_PRODUCTOS = os.path.join(os.path.dirname(__file__), "productos.json")

# Funciones para cargar y guardar datos
def cargar_datos(ruta):
    try:
        with open(ruta, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def guardar_datos(ruta, datos):
    with open(ruta, "w") as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)

# Función para agregar un proveedor
def agregar_proveedor():
    ventana = tk.Toplevel()
    ventana.title("Agregar Proveedor")

    tk.Label(ventana, text="Nombre:").grid(row=0, column=0)
    tk.Label(ventana, text="Número:").grid(row=1, column=0)
    tk.Label(ventana, text="Gmail:").grid(row=2, column=0)
    tk.Label(ventana, text="Ubicación:").grid(row=3, column=0)

    nombre = tk.Entry(ventana)
    numero = tk.Entry(ventana)
    gmail = tk.Entry(ventana)
    ubicacion = tk.Entry(ventana)

    nombre.grid(row=0, column=1)
    numero.grid(row=1, column=1)
    gmail.grid(row=2, column=1)
    ubicacion.grid(row=3, column=1)

    def guardar():
        proveedores = cargar_datos(RUTA_ALMACEN_PROVEEDORES)
        nuevo_proveedor = {
            "nombre": nombre.get(),
            "numero": numero.get(),
            "gmail": gmail.get(),
            "ubicacion": ubicacion.get()
        }
        proveedores.append(nuevo_proveedor)
        guardar_datos(RUTA_ALMACEN_PROVEEDORES, proveedores)
        ventana.destroy()
        messagebox.showinfo("Éxito", "Proveedor agregado correctamente")

    tk.Button(ventana, text="Guardar", command=guardar).grid(row=4, column=0, columnspan=2)

# Función para modificar o eliminar un proveedor
def modificar_eliminar_proveedor():
    ventana = tk.Toplevel()
    ventana.title("Modificar o Eliminar Proveedor")

    proveedores = cargar_datos(RUTA_ALMACEN_PROVEEDORES)
    nombres_proveedores = [proveedor["nombre"] for proveedor in proveedores]

    tk.Label(ventana, text="Selecciona un proveedor:").grid(row=0, column=0)
    seleccion = ttk.Combobox(ventana, values=nombres_proveedores)
    seleccion.grid(row=0, column=1)

    def modificar():
        nombre_seleccionado = seleccion.get()
        for proveedor in proveedores:
            if proveedor["nombre"] == nombre_seleccionado:
                proveedor["numero"] = simpledialog.askstring("Modificar Número", "Nuevo número:", initialvalue=proveedor["numero"])
                proveedor["gmail"] = simpledialog.askstring("Modificar Gmail", "Nuevo gmail:", initialvalue=proveedor["gmail"])
                proveedor["ubicacion"] = simpledialog.askstring("Modificar Ubicación", "Nueva ubicación:", initialvalue=proveedor["ubicacion"])
                guardar_datos(RUTA_ALMACEN_PROVEEDORES, proveedores)
                ventana.destroy()
                messagebox.showinfo("Éxito", "Proveedor modificado correctamente")
                return

    def eliminar():
        nombre_seleccionado = seleccion.get()
        for proveedor in proveedores:
            if proveedor["nombre"] == nombre_seleccionado:
                proveedores.remove(proveedor)
                guardar_datos(RUTA_ALMACEN_PROVEEDORES, proveedores)
                ventana.destroy()
                messagebox.showinfo("Éxito", "Proveedor eliminado correctamente")
                return

    tk.Button(ventana, text="Modificar", command=modificar, bg="#FF9800", fg="white", width=20).grid(row=1, column=0)
    tk.Button(ventana, text="Eliminar", command=eliminar, bg="red", fg="white", width=20).grid(row=1, column=1)

# Función para seleccionar un proveedor
def seleccionar_proveedor():
    ventana = tk.Toplevel()
    ventana.title("Seleccionar Proveedor")

    proveedores = cargar_datos(RUTA_ALMACEN_PROVEEDORES)
    nombres_proveedores = [proveedor["nombre"] for proveedor in proveedores]

    tk.Label(ventana, text="Selecciona un proveedor:").grid(row=0, column=0)
    seleccion = ttk.Combobox(ventana, values=nombres_proveedores)
    seleccion.grid(row=0, column=1)

    def guardar_seleccion():
        nombre_seleccionado = seleccion.get()
        for proveedor in proveedores:
            if proveedor["nombre"] == nombre_seleccionado:
                proveedor_seleccionado = {
                    "nombre": proveedor["nombre"],
                    "numero": proveedor["numero"]
                }
                # Reemplazar el contenido de proveedores.json con el nuevo proveedor seleccionado
                guardar_datos(RUTA_PROVEEDORES, [proveedor_seleccionado])
                ventana.destroy()
                messagebox.showinfo("Éxito", "Proveedor seleccionado correctamente")
                return

    tk.Button(ventana, text="Guardar", command=guardar_seleccion).grid(row=1, column=0, columnspan=2)

# Función para definir un pre-mensaje
def definir_pre_mensaje():
    ventana = tk.Toplevel()
    ventana.title("Definir Pre-Mensaje")

    tk.Label(ventana, text="Pre-Mensaje:").grid(row=0, column=0)
    
    pre_mensaje = tk.Text(ventana, height=10, width=50)
    
    # Placeholder text
    placeholder_text = "Escribe tu pre-mensaje aquí..."
    
    # Function to clear placeholder on focus
    def on_focus_in(event):
        if pre_mensaje.get("1.0", tk.END).strip() == placeholder_text:
            pre_mensaje.delete("1.0", tk.END)
            pre_mensaje.config(fg='black')
    
    # Function to add placeholder on focus out if empty
    def on_focus_out(event):
        if not pre_mensaje.get("1.0", tk.END).strip():
            pre_mensaje.insert("1.0", placeholder_text)
            pre_mensaje.config(fg='grey')
    
    pre_mensaje.insert("1.0", placeholder_text)
    pre_mensaje.config(fg='grey')
    
    pre_mensaje.bind("<FocusIn>", on_focus_in)
    pre_mensaje.bind("<FocusOut>", on_focus_out)

    pre_mensaje.grid(row=1, column=0, columnspan=2)

    def guardar():
        mensaje = pre_mensaje.get("1.0", tk.END).strip()
        pedidos = cargar_datos(RUTA_PEDIDOS)
        if pedidos:
            pedidos[0]["Mensaje"] = mensaje
        else:
            pedidos.append({"Mensaje": mensaje, "Productos": []})
        guardar_datos(RUTA_PEDIDOS, pedidos)
        ventana.destroy()
        messagebox.showinfo("Éxito", "Pre-mensaje guardado correctamente")

    tk.Button(ventana, text="Guardar", command=guardar).grid(row=2, column=0, columnspan=2)
    


# Función para mostrar productos y seleccionar
def mostrar_productos(content_frame):
    productos = cargar_datos(RUTA_PRODUCTOS)

    # Crear un contenedor para el Treeview y la barra de desplazamiento
    table_frame = tk.Frame(content_frame)
    table_frame.pack(pady=10, fill=tk.BOTH, expand=True)

    # Crear la barra de desplazamiento
    scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Crear el Treeview con la barra de desplazamiento
    tree = ttk.Treeview(
        table_frame, 
        columns=("Nombre", "Cantidad", "Código de Barras"), 
        show="headings", 
        yscrollcommand=scrollbar.set
    )
    tree.heading("Nombre", text="Nombre")
    tree.heading("Cantidad", text="Cantidad")
    tree.heading("Código de Barras", text="Código de Barras")
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Conectar la barra de desplazamiento con el Treeview
    scrollbar.config(command=tree.yview)

    # Insertar productos en la tabla
    for producto in productos:
        tree.insert("", tk.END, values=(producto["Nombre"], 0, producto["Código de Barras"]))
    
    # Configurar el tag "seleccionado" con un color verde claro
    tree.tag_configure("seleccionado", background="lightgreen")

    # Función para seleccionar un producto con Enter
    def seleccionar_producto(event):
        try:
            item = tree.selection()[0]  # Obtener el producto seleccionado
            valores = tree.item(item, "values")
            nueva_cantidad = simpledialog.askinteger("Modificar Cantidad", f"Cantidad para {valores[0]}:", initialvalue=valores[1])
            if nueva_cantidad is not None:
                # Actualizar la cantidad y marcar como seleccionado
                tree.item(item, values=(valores[0], nueva_cantidad, valores[2]), tags=("seleccionado",))
        except IndexError:
            messagebox.showerror("Error", "Por favor, selecciona un producto primero.")

    # Función para deseleccionar un producto (con Delete)
    def deseleccionar_producto(event):
        try:
            item = tree.selection()[0]
            tree.item(item, tags=())  # Eliminar el tag de selección
        except IndexError:
            messagebox.showerror("Error", "Por favor, selecciona un producto primero.")

    # Asociar eventos:
    tree.bind("<Return>", seleccionar_producto)  # Enter para seleccionar y cambiar color
    tree.bind("<Delete>", deseleccionar_producto)  # Delete para deseleccionar y restaurar color

    # No se alteran los colores predeterminados de selección con mouse o flechas
    style = ttk.Style()
    style.map("Treeview", background=[("selected", "#cce5ff")], foreground=[("selected", "black")])

    # Función para guardar la selección
    def guardar_seleccion():
        seleccionados = []
        for item in tree.get_children():
            if "seleccionado" in tree.item(item, "tags"):
                valores = tree.item(item, "values")
                seleccionados.append({
                    "Nombre": valores[0],
                    "Cantidad": valores[1],
                    "Código de Barras": valores[2]
                })
        pedidos = cargar_datos(RUTA_PEDIDOS)
        if pedidos:
            pedidos[0]["Productos"] = seleccionados
        else:
            pedidos.append({"Productos": seleccionados})
        guardar_datos(RUTA_PEDIDOS, pedidos)
        messagebox.showinfo("Éxito", "Productos seleccionados correctamente")

    # Crear el botón "Guardar Selección"
    boton_guardar = tk.Frame(content_frame)
    boton_guardar.pack(pady=10)
    tk.Button(boton_guardar, text="Guardar Selección", command=guardar_seleccion, bg="#FF9800", fg="white", width=20).pack(side=tk.LEFT, padx=5)
    tk.Button(boton_guardar, text="Enviar", command=enviar_pedidos, bg="#4CAF50", fg="white", width=20).pack(side=tk.LEFT, padx=5)

    
    
# Función principal para mostrar proveedores y botón de envío
def mostrar_proveedores(content_frame):
    for widget in content_frame.winfo_children():
        widget.destroy()


    # Título de la página con diseño
    titulo_label = tk.Label(content_frame, text="Proveedores / Pedidos", font=("Helvetica", 24, "bold"), bg="#4CAF50", fg="white",).pack( pady=10, padx=120)

    # Botones para agregar y modificar/eliminar proveedores
    frame_botones = tk.Frame(content_frame)
    frame_botones.pack(pady=10)

    tk.Button(frame_botones, text="Agregar Proveedor", command=agregar_proveedor, bg="#4CAF50", fg="white", width=20).pack(side=tk.LEFT, padx=5)
    tk.Button(frame_botones, text="Modificar/Eliminar", command=modificar_eliminar_proveedor, bg="#FF9800", fg="white", width=20).pack(side=tk.LEFT, padx=5)
    tk.Button(frame_botones, text="Seleccionar Proveedor", command=seleccionar_proveedor, bg="#2196F3", fg="white", width=20).pack(side=tk.LEFT, padx=5)
    tk.Button(frame_botones, text="Definir Pre-Mensaje", command=definir_pre_mensaje, bg="#2196F3", fg="white", width=20).pack(side=tk.LEFT, padx=5)
    # Línea de separación
    ttk.Separator(content_frame, orient='horizontal').pack(fill='x', pady=10)

    # Subtítulo para seleccionar proveedor y definir pre-mensaje
    tk.Label(content_frame, text="Seleccionar Pedido", font=("Helvetica", 14)).pack(pady=5)

    # Mostrar productos directamente debajo de los botones
    mostrar_productos(content_frame)
    
# Función para enviar pedidos
def enviar_pedidos():
    from whatsapp import main as enviar_mensajes
    enviar_mensajes()