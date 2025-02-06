# config_impresora.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import win32print  # Para detección de impresoras en Windows

CONFIG_FILE = "config_impresora.json"

def cargar_configuracion():
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "empresa": "SU EMPRESA",
            "direccion": "DIRECCION",
            "telefono": "TELEFONO",
            "cuit": "CUIT",
            "mensaje": "GRACIAS POR SU COMPRA",
            "impresora": "",
            "puerto": "LPT1",
            "estilo": "Normal",
            "modelo": "EPSDN",
            "ancho_ticket": 7.5
        }

def guardar_configuracion(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def detectar_impresoras():
    impresoras = []
    try:
        for impresora in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL):
            impresoras.append(impresora[2])
    except:
        messagebox.showerror("Error", "No se pudieron detectar impresoras")
    return impresoras

def abrir_configuracion_impresora(parent):
    def guardar_config():
        config = {
            "empresa": entry_empresa.get(),
            "direccion": entry_direccion.get(),
            "telefono": entry_telefono.get(),
            "cuit": entry_cuit.get(),
            "mensaje": entry_mensaje.get(),
            "impresora": combo_impresoras.get(),
            "puerto": combo_puerto.get(),
            "estilo": combo_estilo.get(),
            "modelo": combo_modelo.get(),
            "ancho_ticket": float(entry_ancho.get())
        }
        guardar_configuracion(config)
        messagebox.showinfo("Configuración Guardada", "¡Configuración actualizada!")
        ventana.destroy()

    ventana = tk.Toplevel(parent)
    ventana.title("Configuración de Ticket")
    
    # Marco principal
    main_frame = ttk.Frame(ventana, padding=10)
    main_frame.pack(fill="both", expand=True)

    # Sección de datos de la empresa
    ttk.Label(main_frame, text="Datos de la Empresa:").grid(row=0, column=0, sticky="w", pady=5)
    
    ttk.Label(main_frame, text="Nombre:").grid(row=1, column=0, sticky="w")
    entry_empresa = ttk.Entry(main_frame, width=30)
    entry_empresa.grid(row=1, column=1, padx=5, pady=2)
    
    ttk.Label(main_frame, text="Dirección:").grid(row=2, column=0, sticky="w")
    entry_direccion = ttk.Entry(main_frame, width=30)
    entry_direccion.grid(row=2, column=1, padx=5, pady=2)
    
    ttk.Label(main_frame, text="Teléfono:").grid(row=3, column=0, sticky="w")
    entry_telefono = ttk.Entry(main_frame, width=30)
    entry_telefono.grid(row=3, column=1, padx=5, pady=2)
    
    ttk.Label(main_frame, text="CUIT:").grid(row=4, column=0, sticky="w")
    entry_cuit = ttk.Entry(main_frame, width=30)
    entry_cuit.grid(row=4, column=1, padx=5, pady=2)
    
    ttk.Label(main_frame, text="Mensaje Final:").grid(row=5, column=0, sticky="w")
    entry_mensaje = ttk.Entry(main_frame, width=30)
    entry_mensaje.grid(row=5, column=1, padx=5, pady=2)

    # Sección de configuración de impresión
    ttk.Label(main_frame, text="Configuración de Impresión:").grid(row=6, column=0, sticky="w", pady=10)
    
    ttk.Label(main_frame, text="Impresora:").grid(row=7, column=0, sticky="w")
    impresoras = detectar_impresoras()
    combo_impresoras = ttk.Combobox(main_frame, values=impresoras, width=27)
    combo_impresoras.grid(row=7, column=1, padx=5, pady=2)
    
    ttk.Label(main_frame, text="Puerto:").grid(row=8, column=0, sticky="w")
    combo_puerto = ttk.Combobox(main_frame, values=["LPT1", "USB", "Red"], width=27)
    combo_puerto.grid(row=8, column=1, padx=5, pady=2)
    
    ttk.Label(main_frame, text="Estilo:").grid(row=9, column=0, sticky="w")
    combo_estilo = ttk.Combobox(main_frame, values=["Normal", "Condensado", "Doble Ancho"], width=27)
    combo_estilo.grid(row=9, column=1, padx=5, pady=2)
    
    ttk.Label(main_frame, text="Modelo:").grid(row=10, column=0, sticky="w")
    combo_modelo = ttk.Combobox(main_frame, values=["EPSDN", "Térmica Genérica", "PDF"], width=27)
    combo_modelo.grid(row=10, column=1, padx=5, pady=2)
    
    ttk.Label(main_frame, text="Ancho Ticket (cm):").grid(row=11, column=0, sticky="w")
    entry_ancho = ttk.Combobox(main_frame, values=[ 7.5, 5.5], width=27)
    entry_ancho.grid(row=11, column=1, padx=5, pady=2)

    # Botones
    btn_frame = ttk.Frame(main_frame)
    btn_frame.grid(row=12, columnspan=2, pady=10)
    
    ttk.Button(btn_frame, text="Aceptar", command=guardar_config).pack(side="left", padx=5)
    ttk.Button(btn_frame, text="Cancelar", command=ventana.destroy).pack(side="left", padx=5)

    # Cargar configuración existente
    config = cargar_configuracion()
    entry_empresa.insert(0, config.get("empresa", ""))
    entry_direccion.insert(0, config.get("direccion", ""))
    entry_telefono.insert(0, config.get("telefono", ""))
    entry_cuit.insert(0, config.get("cuit", ""))
    entry_mensaje.insert(0, config.get("mensaje", ""))
    combo_impresoras.set(config.get("impresora", ""))
    combo_puerto.set(config.get("puerto", "LPT1"))
    combo_estilo.set(config.get("estilo", "Normal"))
    combo_modelo.set(config.get("modelo", "EPSDN"))
    entry_ancho.insert(0, str(config.get("ancho_ticket", 7.5)))