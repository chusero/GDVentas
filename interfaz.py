import tkinter as tk
from tkinter import ttk, Menu, messagebox
from funciones_comunes import cargar_imagen
import os
from agregar_productos import agregar_producto
from modificar_productos import modificar_producto
from stock import mostrar_stock
from ver_reportes import ver_reportes
from ventas import realizar_venta
from Proveedores import mostrar_proveedores
from agregar_clientes import agregar_cliente
from consultar_pedidos import consultar_pedidos
from ingreso_pedidos import ingreso_pedidos
from cajas import verificar_caja_abierta, abrir_caja, cerrar_caja
from caja_diaria import abrir_ventana_caja_diaria
from configuracion_afip import abrir_configuracion_afip
from config_impresora import abrir_configuracion_impresora
from bd_excel import leer_csv_y_agregar_a_json
from autenticacion import Autenticacion
import hashlib
from gestion_suscripciones import mostrar_registro_licencia, mostrar_activacion_licencia
from firebase_db import FirebaseManager
from gestion_suscripciones import SubscriptionManager


# Inicializar Firebase
firebase = FirebaseManager()
RUTA_CAJAS = os.path.join(os.path.dirname(__file__), "cajas.json")
# Para verificar estado de suscripción

def crear_interfaz(root, usuario_actual,firebase_manager):
    root.deiconify()
    root.title(f"Sistema de Gestión - {usuario_actual['username']} ({usuario_actual['rol']})")
    root.geometry("1024x600")
    root.state('zoomed')

    # Función de cierre
    def on_closing():
        if messagebox.askokcancel("Salir", "¿Realmente deseas salir?"):
            cerrar_caja()
            root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Frame izquierdo
    left_frame = tk.Frame(root, width=200, bg="#f0f0f0")
    left_frame.pack(side="left", fill="y")

    # Frame principal
    content_frame = tk.Frame(root, bg="#f0f0f0")
    content_frame.pack(side="right", expand=True, fill="both")

    bordered_frame = tk.Frame(content_frame, bg="#f0f0f0", bd=0)
    bordered_frame.pack(expand=True, fill="both", padx=30, pady=30)

    def limpiar_contenido():
        for widget in bordered_frame.winfo_children():
            widget.destroy()

    # Botones izquierda
    button_images = [
        cargar_imagen("agregar-producto.png"),
        cargar_imagen("diseno-de-producto.png"),
        cargar_imagen("en-stock.png"),
        cargar_imagen("informe-de-venta.png"),
        cargar_imagen("proveedor.png"),
        cargar_imagen("ventas.png"),
    ]
    root.button_images = button_images

    button_texts = ["Agregar Producto", "Modificar Producto", "Stock", "Ver Reportes", "Proveedores", "Ventas"]
    button_functions = [
        lambda: [limpiar_contenido(), agregar_producto(bordered_frame)],
        lambda: [limpiar_contenido(), modificar_producto(bordered_frame)],
        lambda: [limpiar_contenido(), mostrar_stock(bordered_frame)],
        lambda: [limpiar_contenido(), ver_reportes(bordered_frame)] if usuario_actual["rol"] == "admin" else messagebox.showerror("Acceso denegado", "Requiere permisos de administrador"),
        lambda: [limpiar_contenido(), mostrar_proveedores(bordered_frame)] if usuario_actual["rol"] == "admin" else messagebox.showerror("Acceso denegado", "Requiere permisos de administrador"),
        lambda: [limpiar_contenido(), realizar_venta(bordered_frame)],
    ]

    for i, (text, func) in enumerate(zip(button_texts, button_functions)):
        btn = tk.Button(left_frame, text=text, image=button_images[i], compound="top", command=func)
        btn.grid(row=i, column=0, sticky="nsew", padx=5, pady=5)
        left_frame.grid_rowconfigure(i, weight=1)

    if not verificar_caja_abierta():
        abrir_caja()

    # Menú superior
    menu_bar = Menu(root)

    # Menú Artículos
    articulos_menu = Menu(menu_bar, tearoff=0)
    articulos_menu.add_command(label="Agregar", command=lambda: [limpiar_contenido(), agregar_producto(bordered_frame)])
    articulos_menu.add_command(label="Modificar", command=lambda: [limpiar_contenido(), modificar_producto(bordered_frame)])
    menu_bar.add_cascade(label="Artículos", menu=articulos_menu)

    # Menú Clientes
    clientes_menu = Menu(menu_bar, tearoff=0)
    clientes_menu.add_command(label="Agregar/Modificar", command=lambda: [limpiar_contenido(), agregar_cliente(bordered_frame)])
    menu_bar.add_cascade(label="Clientes", menu=clientes_menu)

    # Menú Compras (solo admin)
    compras_menu = Menu(menu_bar, tearoff=0)
    compras_menu.add_command(label="Consultar Pedidos", command=lambda: [limpiar_contenido(), consultar_pedidos(bordered_frame)])
    compras_menu.add_command(label="Ingreso de Mercadería", command=lambda: [limpiar_contenido(), ingreso_pedidos(bordered_frame)])
    menu_bar.add_cascade(label="Compras", menu=compras_menu)

    # Menú Ventas
    ventas_menu = Menu(menu_bar, tearoff=0)
    ventas_menu.add_command(label="Facturas")
    ventas_menu.add_command(label="Cerrar Turno")
    ventas_menu.add_command(label="Consultar Ventas")
    ventas_menu.add_command(label="Consultar Turnos")
    ventas_menu.add_command(label="Salida de Mercadería")
    ventas_menu.add_command(label="Consulta de Salidas")
    menu_bar.add_cascade(label="Ventas", menu=ventas_menu)

    # Menú Caja (solo admin)
    caja_menu = Menu(menu_bar, tearoff=0)
    caja_menu.add_command(label="Caja Diaria", command=abrir_ventana_caja_diaria)
    menu_bar.add_cascade(label="Caja", menu=caja_menu)

    # Menú Proveedores (solo admin)
    proveedores_menu = Menu(menu_bar, tearoff=0)
    proveedores_menu.add_command(label="Agregar")
    proveedores_menu.add_command(label="Modificar")
    menu_bar.add_cascade(label="Proveedores", menu=proveedores_menu)

    # Menú Administración
    administracion_menu = Menu(menu_bar, tearoff=0)
    administracion_menu.add_command(label="Configurar AFIP", command=lambda: abrir_configuracion_afip(root))
    administracion_menu.add_command(label="Configurar Impresora", command=lambda: abrir_configuracion_impresora(root))
    administracion_menu.add_command(label="Importar CSV", command=leer_csv_y_agregar_a_json)
    

    administracion_menu.add_command(
        label="Gestión de Suscripciones",
        command=lambda: mostrar_registro_licencia(root, firebase_manager)
    )

    administracion_menu.add_command(
        label="Activar Licencia",
        command=lambda: mostrar_activacion_licencia(root, firebase_manager)
    )
    def mostrar_alerta_suscripcion():
        messagebox.showwarning(
        "Suscripción Requerida",
        "Debes tener una suscripción activa para acceder a esta funcionalidad.\n\n"
        "Por favor, contacta al administrador o renueva tu licencia."
    )
    def verificar_suscripcion(usuario):
        manager = SubscriptionManager(firebase_manager)
        status = manager.check_subscription_status(usuario['email'])
   
        if status['status'] != 'active':
            mostrar_alerta_suscripcion()
    # Gestión de usuarios (solo admin)
    def gestion_usuarios():
        if usuario_actual["rol"] != "admin":
            messagebox.showerror("Acceso denegado", "Requiere permisos de administrador")
            return

        ventana = tk.Toplevel(root)
        ventana.title("Gestión de Usuarios")
        
        tree = ttk.Treeview(ventana, columns=("Usuario", "Rol"), show="headings")
        tree.heading("Usuario", text="Usuario")
        tree.heading("Rol", text="Rol")
        tree.pack(padx=10, pady=10)

        frame_controles = tk.Frame(ventana)
        frame_controles.pack(pady=10)

        tk.Label(frame_controles, text="Usuario:").grid(row=0, column=0)
        entry_usuario = tk.Entry(frame_controles)
        entry_usuario.grid(row=0, column=1)

        tk.Label(frame_controles, text="Contraseña:").grid(row=1, column=0)
        entry_password = tk.Entry(frame_controles, show="*")
        entry_password.grid(row=1, column=1)

        tk.Label(frame_controles, text="Rol:").grid(row=2, column=0)
        combo_rol = ttk.Combobox(frame_controles, values=["admin", "usuario"])
        combo_rol.grid(row=2, column=1)

        def actualizar_lista():
            tree.delete(*tree.get_children())
            usuarios = Autenticacion.cargar_usuarios()
            for usuario, datos in usuarios.items():
                tree.insert("", "end", values=(usuario, datos["rol"]))

        def agregar_usuario():
            usuarios = Autenticacion.cargar_usuarios()
            nuevo_usuario = entry_usuario.get()
            
            if nuevo_usuario in usuarios:
                messagebox.showerror("Error", "Usuario ya existe")
                return
                
            usuarios[nuevo_usuario] = {
                "password": hashlib.sha256(entry_password.get().encode()).hexdigest(),
                "rol": combo_rol.get()
            }
            Autenticacion.guardar_usuarios(usuarios)
            actualizar_lista()

        def eliminar_usuario():
            seleccion = tree.selection()
            if not seleccion:
                return
                
            usuario = tree.item(seleccion[0])["values"][0]
            if usuario == "admin":
                messagebox.showerror("Error", "No se puede eliminar al admin principal")
                return
                
            usuarios = Autenticacion.cargar_usuarios()
            del usuarios[usuario]
            Autenticacion.guardar_usuarios(usuarios)
            actualizar_lista()

        tk.Button(frame_controles, text="Agregar", command=agregar_usuario, bg="green", fg="white").grid(row=3, column=0, pady=5)
        tk.Button(frame_controles, text="Eliminar", command=eliminar_usuario, bg="red", fg="white").grid(row=3, column=1, pady=5)

        actualizar_lista()

    administracion_menu.add_command(label="Gestión de Usuarios", command=gestion_usuarios)
    menu_bar.add_cascade(label="Administración", menu=administracion_menu)

    # Configurar permisos
    def configurar_permisos():
        if usuario_actual["rol"] != "admin":
            menu_bar.entryconfig("Proveedores", state="disabled")
            menu_bar.entryconfig("Compras", state="disabled")
            menu_bar.entryconfig("Caja", state="disabled")
            menu_bar.entryconfig("Administración",state="disabled")
            
            for btn in left_frame.winfo_children():
                if btn.cget("text") in ["Ver Reportes", "Proveedores"]:
                    btn.destroy()

    configurar_permisos()
    root.config(menu=menu_bar)
    root.mainloop()