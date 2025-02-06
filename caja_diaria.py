import json
import os
from tkinter import Toplevel, Label, Entry, Button, Tk, messagebox, StringVar, simpledialog, Frame
from datetime import datetime

RUTA_CAJAS = os.path.join(os.path.dirname(__file__), "cajas.json")
RUTA_VENTAS = os.path.join(os.path.dirname(__file__), "ventas.json")

def cargar_cajas():
    try:
        with open(RUTA_CAJAS, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def guardar_cajas(cajas):
    try:
        with open(RUTA_CAJAS, "w") as file:
            json.dump(cajas, file, indent=4)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar la caja: {e}")

def cargar_ventas():
    try:
        with open(RUTA_VENTAS, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def verificar_caja_abierta():
    cajas = cargar_cajas()
    for caja in cajas:
        if not caja.get("cerrada"):
            return True
    return False

def obtener_monto_inicial():
    root = Tk()
    root.withdraw()
    monto_inicial = simpledialog.askfloat("Abrir Caja", "Ingrese el monto inicial de la caja:")
    root.destroy()
    return monto_inicial

def abrir_ventana_caja_diaria():
    ventana = Toplevel()
    ventana.title("Caja Diaria")
    ventana.geometry("500x600")

    caja_inicial = StringVar(value="0.00")
    caja_actual = StringVar(value="0.00")
    otros_gastos = StringVar(value="0.00")
    otros_ingresos = StringVar(value="0.00")
    retiros = StringVar(value="0.00")

    def actualizar_cajas():
        cajas = cargar_cajas()
        caja_abierta = next((caja for caja in cajas if not caja.get("cerrada")), None)
        if caja_abierta:
            caja_inicial.set(f"{caja_abierta['monto_inicial']:.2f}")
            caja_actual.set(f"{calcular_caja_actual(caja_abierta):.2f}")
            otros_gastos.set(f"{sum(gasto['importe'] for gasto in caja_abierta.get('otros_gastos', [])):.2f}")
            otros_ingresos.set(f"{sum(ingreso['importe'] for ingreso in caja_abierta.get('otros_ingresos', [])):.2f}")
            retiros.set(f"{sum(retiro['importe'] for retiro in caja_abierta.get('retiros', [])):.2f}")
        else:
            caja_inicial.set("0.00")
            caja_actual.set("0.00")
            otros_gastos.set("0.00")
            otros_ingresos.set("0.00")
            retiros.set("0.00")

    def calcular_caja_actual(caja_abierta):
        ventas = cargar_ventas()
        fecha_apertura = datetime.strptime(caja_abierta["fecha_apertura"], "%Y-%m-%d %H:%M:%S")
        total_ventas = sum(
            venta.get("total", 0.0) 
            for venta in ventas 
            if datetime.strptime(venta.get("fecha"), "%Y-%m-%d %H:%M:%S") >= fecha_apertura
        )

        otros_ingresos = sum(ingreso["importe"] for ingreso in caja_abierta.get("otros_ingresos", []))
        otros_gastos = sum(gasto["importe"] for gasto in caja_abierta.get("otros_gastos", []))
        retiros = sum(retiro["importe"] for retiro in caja_abierta.get("retiros", []))

        return caja_abierta["monto_inicial"] + total_ventas + otros_ingresos - otros_gastos - retiros

    def crear_seccion(tipo):
        frame = Toplevel(ventana)
        frame.title(f"Ingresar {tipo.capitalize()}")

        Label(frame, text="Fecha (YYYY-MM-DD):").grid(row=0, column=0)
        fecha_entry = Entry(frame)
        fecha_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))  # Fecha actual sin hora
        fecha_entry.grid(row=0, column=1)

        Label(frame, text="Detalles:").grid(row=1, column=0)
        detalles_entry = Entry(frame)
        detalles_entry.grid(row=1, column=1)

        Label(frame, text="Importe:").grid(row=2, column=0)
        importe_entry = Entry(frame)
        importe_entry.grid(row=2, column=1)

        def guardar():
            fecha = fecha_entry.get()
            detalles = detalles_entry.get()
            try:
                importe = float(importe_entry.get())
            except ValueError:
                messagebox.showerror("Error", "El importe debe ser un número.")
                return

            if not fecha or not detalles or importe < 0:
                messagebox.showwarning("Advertencia", "Todos los campos deben ser válidos y el importe positivo.")
                return

            datos = {
                "fecha": fecha,
                "detalles": detalles,
                "importe": importe
            }
            agregar_dato(tipo, datos)
            frame.destroy()
            actualizar_cajas()

        Button(frame, text="Guardar", command=guardar).grid(row=3, column=0, columnspan=2)

    def agregar_dato(tipo, datos):
        cajas = cargar_cajas()
        for caja in cajas:
            if not caja.get("cerrada"):
                if tipo not in caja:
                    caja[tipo] = []
                caja[tipo].append(datos)
                guardar_cajas(cajas)
                messagebox.showinfo(f"{tipo.capitalize()} Agregado", f"El {tipo} ha sido agregado correctamente.")
                return

    # Crear un frame para organizar los elementos en una matriz
    frame = Frame(ventana)
    frame.pack(pady=10)

    # Caja Inicial y Caja Actual
    Label(frame, text="Caja Inicial:", font=("Arial", 14)).grid(row=0, column=0, padx=10, pady=10)
    caja_inicial_entry = Entry(frame, textvariable=caja_inicial, font=("Arial", 14), state='readonly')
    caja_inicial_entry.grid(row=0, column=1, padx=10, pady=10)

    Label(frame, text="Caja Actual:", font=("Arial", 14)).grid(row=1, column=0, padx=10, pady=10)
    caja_actual_entry = Entry(frame, textvariable=caja_actual, font=("Arial", 14), state='readonly')
    caja_actual_entry.grid(row=1, column=1, padx=10, pady=10)

    Button(frame, text="", command=actualizar_cajas, width=5, height=2).grid(row=2, column=0, columnspan=2, pady=10)

    # Sección Otros Gastos
    Label(frame, text="Otros Gastos", font=("Arial", 14)).grid(row=3, column=0, padx=10, pady=10)
    otros_gastos_entry = Entry(frame, textvariable=otros_gastos, font=("Arial", 14), state='readonly')
    otros_gastos_entry.grid(row=3, column=1, padx=10, pady=10)
    Button(frame, text="", command=lambda: crear_seccion("otros_gastos"), width=5, height=2).grid(row=3, column=2, padx=10, pady=10)

    # Sección Otros Ingresos
    Label(frame, text="Otros Ingresos", font=("Arial", 14)).grid(row=4, column=0, padx=10, pady=10)
    otros_ingresos_entry = Entry(frame, textvariable=otros_ingresos, font=("Arial", 14), state='readonly')
    otros_ingresos_entry.grid(row=4, column=1, padx=10, pady=10)
    Button(frame, text="", command=lambda: crear_seccion("otros_ingresos"), width=5, height=2).grid(row=4, column=2, padx=10, pady=10)

    # Sección Retiros
    Label(frame, text="Retiros", font=("Arial", 14)).grid(row=5, column=0, padx=10, pady=10)
    retiros_entry = Entry(frame, textvariable=retiros, font=("Arial", 14), state='readonly')
    retiros_entry.grid(row=5, column=1, padx=10, pady=10)
    Button(frame, text="", command=lambda: crear_seccion("retiros"), width=5, height=2).grid(row=5, column=2, padx=10, pady=10)

    # Botón Cerrar
    Button(frame, text="", command=ventana.destroy, width=5, height=2).grid(row=6, column=0, columnspan=3, pady=20)

    actualizar_cajas()