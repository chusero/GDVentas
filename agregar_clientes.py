import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from tkcalendar import DateEntry

def agregar_cliente(parent):
    # Limpiar el contenido anterior
    for widget in parent.winfo_children():
        widget.destroy()

    frame = tk.Frame(parent)
    frame.pack(fill="both", expand=True)

    # Título del formulario
    tk.Label(frame, text="Nuevo Cliente", font=("Helvetica", 16)).grid(row=0, columnspan=4, pady=10)

    # Campos del formulario reorganizados
    campos = [
        ("Nombre", 1, 0, 2), ("Código", 1, 2, 1), ("Fecha de Nacimiento", 1, 3, 1),
        ("Dirección", 2, 0, 2), ("Código Postal", 2, 2, 1), ("Localidad", 2, 3, 1),
        ("Provincia", 3, 0, 2), ("Teléfono", 3, 2, 1), ("Celular", 3, 3, 1),
        ("Email", 4, 0, 2), ("Web", 4, 2, 2), 
        ("Número CUIT", 5, 0, 2), ("Tipo CUIT", 5, 2, 1), ("Límite de Cuenta Corriente", 5, 3, 1), 
        ("Observaciones", 6, 0, 4)
    ]

    entradas = {}
    for campo, row, col, colspan in campos:
        tk.Label(frame, text=campo).grid(row=row, column=col*2, sticky="e", padx=10, pady=5)
        if campo == "Fecha de Nacimiento":
            entrada = DateEntry(frame, width=30)
        elif campo == "Provincia":
            entrada = ttk.Combobox(frame, values=[
                "Buenos Aires", "Catamarca", "Chaco", "Chubut", "Córdoba", "Corrientes", "Entre Ríos",
                "Formosa", "Jujuy", "La Pampa", "La Rioja", "Mendoza", "Misiones", "Neuquén", 
                "Río Negro", "Salta", "San Juan", "San Luis", "Santa Cruz", "Santa Fe", 
                "Santiago del Estero", "Tierra del Fuego", "Tucumán"
            ], width=27)
        elif campo == "Tipo CUIT":
            entrada = ttk.Combobox(frame, values=[
                "Responsable Inscripto", "Consumidor Final", "No Responsable", "Exento"
            ], width=27)
        else:
            entrada = tk.Entry(frame, width=30)
        entrada.grid(row=row, column=col*2+1, columnspan=colspan, pady=5, sticky="we")
        entradas[campo] = entrada

    # Función para guardar el cliente en clientes.json
    def guardar_cliente():
        cliente_info = {campo: entradas[campo].get() for campo, _, _, _ in campos}

        if os.path.exists('clientes.json'):
            with open('clientes.json', 'r', encoding='utf-8') as file:
                clientes = json.load(file)
        else:
            clientes = []

        clientes.append(cliente_info)

        with open('clientes.json', 'w', encoding='utf-8') as file:
            json.dump(clientes, file, indent=4, ensure_ascii=False)

        messagebox.showinfo("Guardar Cliente", "Cliente guardado con éxito.")
        mostrar_clientes(parent)

    # Función para limpiar los campos del formulario
    def limpiar_campos():
        for entrada in entradas.values():
            entrada.delete(0, tk.END)

    # Botones de Guardar, Cancelar y Modificar Cliente
    tk.Button(frame, text="Guardar", command=guardar_cliente, bg="green", fg="white").grid(row=7, column=0, columnspan=1, pady=10, sticky="we")
    tk.Button(frame, text="Cancelar", command=limpiar_campos, bg="red", fg="white").grid(row=7, column=1, columnspan=1, pady=10, sticky="we")
    tk.Button(frame, text="Mostrar clientes", command=lambda: mostrar_clientes(parent), bg="blue", fg="white").grid(row=7, column=2, columnspan=2, pady=10, sticky="we")

def mostrar_clientes(parent):
    # Limpiar el contenido anterior
    for widget in parent.winfo_children():
        widget.destroy()

    frame = tk.Frame(parent)
    frame.pack(fill="both", expand=True)

    # Título de la lista de clientes
    tk.Label(frame, text="Lista de Clientes", font=("Helvetica", 16)).grid(row=0, columnspan=4, pady=10)

    # Cargar clientes desde el archivo JSON
    if os.path.exists('clientes.json'):
        with open('clientes.json', 'r', encoding='utf-8') as file:
            clientes = json.load(file)
            print("Clientes cargados:", clientes)  # Mensaje de depuración
    else:
        clientes = []
        print("No se encontró el archivo clientes.json")  # Mensaje de depuración

    # Tabla de clientes
    columns = ["Código", "Nombre", "Dirección", "Localidad", "Provincia", "Código Postal", "Teléfono", "Celular", "Email", "Web", "Número CUIT", "Tipo CUIT", "Límite de Cuenta Corriente", "Fecha de Nacimiento", "Observaciones"]
    
    tree = ttk.Treeview(frame, columns=columns, show="headings")
    tree.grid(row=1, column=0, columnspan=4, pady=10, sticky="nsew")

    # Agregar barra de desplazamiento horizontal
    scrollbar_x = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
    scrollbar_x.grid(row=2, column=0, columnspan=4, sticky="ew")
    tree.configure(xscrollcommand=scrollbar_x.set)

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100, stretch=tk.YES)
    
    for cliente in clientes:
        try:
            tree.insert("", "end", values=[cliente[col] for col in columns])
        except KeyError as e:
            print(f"Error: La clave {e} no se encontró en el cliente {cliente}")

    # Ajustar el ancho de las columnas al contenido
    for col in columns:
        tree.column(col, width=tk.font.Font().measure(col))
        for item in tree.get_children():
            col_width = tk.font.Font().measure(tree.set(item, col))
            if tree.column(col, width=None) < col_width:
                tree.column(col, width=col_width)

    frame.grid_rowconfigure(1, weight=1)
    frame.grid_columnconfigure(0, weight=1)

    def make_editable(event):
        # Verificar si hay un elemento seleccionado
        if not tree.selection():
            return

        # Obtener el elemento seleccionado
        item = tree.selection()[0]
        column = tree.identify_column(event.x)
        column_index = int(column[1:]) - 1
        value = tree.item(item, "values")[column_index]

        # Obtener coordenadas precisas de la celda
        x, y, width, height = tree.bbox(item, column)

        # Crear una entrada directamente sobre la celda para editar
        entry = tk.Entry(tree)
        entry.insert(0, value)
        entry.place(x=x, y=y, width=width, height=height)

        def save_edit(event):
            tree.set(item, column, entry.get())
            entry.destroy()

        entry.bind("<Return>", save_edit)
        entry.bind("<FocusOut>", save_edit)
        entry.focus()

    tree.bind("<Double-1>", make_editable)

    def guardar_cambios():
        items = tree.get_children()
        clientes_modificados = []
        for item in items:
            cliente = {columns[i]: tree.item(item)["values"][i] for i in range(len(columns))}
            clientes_modificados.append(cliente)
        with open('clientes.json', 'w', encoding='utf-8') as file:
            json.dump(clientes_modificados, file, indent=4, ensure_ascii=False)
        messagebox.showinfo("Guardar Cambios", "Cambios guardados con éxito.")

    def borrar_cliente():
        selected_item = tree.selection()[0]
        tree.delete(selected_item)

    tk.Button(frame, text="Guardar Cambios", command=guardar_cambios, bg="green", fg="white").grid(row=3, column=0, pady=10, sticky="we")
    tk.Button(frame, text="Borrar Cliente", command=borrar_cliente, bg="orange", fg="white").grid(row=3, column=1, pady=10, sticky="we")
    tk.Button(frame, text="Agregar Cliente", command=lambda: agregar_cliente(parent), bg="blue", fg="white").grid(row=3, column=2, pady=10, sticky="we")
    tk.Button(frame, text="Limpiar Pantalla", command=lambda: limpiar_pantalla(parent), bg="red", fg="white").grid(row=3, column=3, pady=10, sticky="we")

    for i in range(4):
        frame.grid_columnconfigure(i, weight=1)

def limpiar_pantalla(parent):
    for widget in parent.winfo_children():
        widget.destroy()