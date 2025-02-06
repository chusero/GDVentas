import json
import os
from tkinter import simpledialog, messagebox, Tk
from datetime import datetime, timedelta
RUTA_CAJAS = os.path.join(os.path.dirname(__file__), "cajas.json")

def cargar_cajas():
    try:
        with open(RUTA_CAJAS, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

def guardar_cajas(cajas):
    try:
        with open(RUTA_CAJAS, "w") as file:
            json.dump(cajas, file, indent=4)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar la caja: {e}")

def verificar_caja_abierta():
    cajas = cargar_cajas()
    for caja in cajas:
        if not caja.get("cerrada"):
            return True
    return False

def abrir_caja():
    root = Tk()
    root.withdraw()  # Ocultar la ventana principal

    monto_inicial = simpledialog.askfloat("Abrir Caja", "Ingrese el monto inicial de la caja:")
    if monto_inicial is None:
        messagebox.showwarning("Advertencia", "Debe ingresar un monto inicial para abrir la caja.")
        return

    nueva_caja = {
        "fecha_apertura": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "monto_inicial": monto_inicial,
        "monto_final": 0.0,
        "cerrada": False
    }
    cajas = cargar_cajas()
    cajas.append(nueva_caja)
    guardar_cajas(cajas)

    messagebox.showinfo("Caja Abierta", f"Caja abierta con un monto inicial de ${monto_inicial:.2f}")
    root.destroy()

def cerrar_caja():
    cajas = cargar_cajas()
    for caja in cajas:
        if not caja.get("cerrada"):
            root = Tk()
            root.withdraw()  # Ocultar la ventana principal
            monto_final = simpledialog.askfloat("Cerrar Caja", "Ingrese el monto final de la caja:")
            if monto_final is None:
                messagebox.showwarning("Advertencia", "Debe ingresar un monto final para cerrar la caja.")
                return

            caja["monto_final"] = monto_final
            caja["fecha_cierre"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            caja["cerrada"] = True
            guardar_cajas(cajas)

            messagebox.showinfo("Caja Cerrada", f"Caja cerrada con un monto final de ${monto_final:.2f}")
            root.destroy()
            return
