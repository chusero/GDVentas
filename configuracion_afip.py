import tkinter as tk
from tkinter import filedialog, messagebox
import json
import os

# Ruta del archivo de configuración
CONFIG_FILE = "config_afip.json"

def cargar_configuracion():
    """Carga la configuración desde un archivo JSON."""
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "cuit": "",
            "certificado": "",
            "clave_privada": "",
            "entorno": "homologation"  # Valor por defecto: homologación
        }

def guardar_configuracion(config):
    """Guarda la configuración en un archivo JSON."""
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def abrir_configuracion_afip(parent):
    """Abre la ventana de configuración de AFIP."""
    def seleccionar_archivo(entry):
        """Abre un diálogo para seleccionar un archivo."""
        ruta = filedialog.askopenfilename(filetypes=[("Certificados", "*.crt *.key")])
        if ruta:
            entry.delete(0, tk.END)
            entry.insert(0, ruta)

    def guardar_config():
        """Guarda la configuración ingresada por el vendedor."""
        config = {
            "cuit": entry_cuit.get(),
            "certificado": entry_certificado.get(),
            "clave_privada": entry_clave_privada.get(),
            "entorno": entorno_var.get()  # Obtener el entorno seleccionado
        }
        guardar_configuracion(config)
        messagebox.showinfo("Configuración Guardada", "¡Datos de AFIP guardados!")
        ventana_config.destroy()

    # Crear ventana de configuración
    ventana_config = tk.Toplevel(parent)
    ventana_config.title("Configurar AFIP")

    # Variables
    entorno_var = tk.StringVar(value="homologation")  # Valor por defecto: homologación

    # Campos de configuración
    tk.Label(ventana_config, text="CUIT:").grid(row=0, column=0, padx=10, pady=5)
    entry_cuit = tk.Entry(ventana_config, width=30)
    entry_cuit.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(ventana_config, text="Certificado (.crt):").grid(row=1, column=0, padx=10, pady=5)
    entry_certificado = tk.Entry(ventana_config, width=30)
    entry_certificado.grid(row=1, column=1, padx=10, pady=5)
    tk.Button(ventana_config, text="Seleccionar", command=lambda: seleccionar_archivo(entry_certificado)).grid(row=1, column=2, padx=10, pady=5)

    tk.Label(ventana_config, text="Clave Privada (.key):").grid(row=2, column=0, padx=10, pady=5)
    entry_clave_privada = tk.Entry(ventana_config, width=30)
    entry_clave_privada.grid(row=2, column=1, padx=10, pady=5)
    tk.Button(ventana_config, text="Seleccionar", command=lambda: seleccionar_archivo(entry_clave_privada)).grid(row=2, column=2, padx=10, pady=5)

    # Selección de entorno (Homologación o Producción)
    tk.Label(ventana_config, text="Entorno:").grid(row=3, column=0, padx=10, pady=5)
    tk.Radiobutton(ventana_config, text="Homologación (Pruebas)", variable=entorno_var, value="homologation").grid(row=3, column=1, sticky="w")
    tk.Radiobutton(ventana_config, text="Producción (Real)", variable=entorno_var, value="production").grid(row=4, column=1, sticky="w")

    # Botón para guardar la configuración
    tk.Button(ventana_config, text="Guardar", command=guardar_config).grid(row=5, columnspan=3, pady=10)

    # Cargar configuración existente
    config = cargar_configuracion()
    entry_cuit.insert(0, config.get("cuit", ""))
    entry_certificado.insert(0, config.get("certificado", ""))
    entry_clave_privada.insert(0, config.get("clave_privada", ""))
    entorno_var.set(config.get("entorno", "homologation"))  # Cargar entorno guardado

# Ejemplo de uso
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Ocultar ventana principal
    abrir_configuracion_afip(root)
    root.mainloop()