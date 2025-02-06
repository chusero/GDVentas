import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
import json
import os
import plotly.graph_objects as go
from tkcalendar import DateEntry
from PIL import Image, ImageTk
from io import BytesIO

# Ajustar las rutas relativas a los archivos JSON
RUTA_VENTAS = os.path.join(os.path.dirname(__file__), "ventas.json")
RUTA_PRODUCTOS = os.path.join(os.path.dirname(__file__), "productos.json")

# Función para cargar ventas desde un archivo JSON
def cargar_ventas():
    try:
        with open(RUTA_VENTAS, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Función para cargar productos desde un archivo JSON
def cargar_productos():
    try:
        with open(RUTA_PRODUCTOS, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Función principal para ver reportes
def ver_reportes(content_frame):
    # Limpiar contenido previo
    for widget in content_frame.winfo_children():
        widget.destroy()

    # Crear botones para seleccionar diferentes reportes
    botones_frame = tk.Frame(content_frame)
    botones_frame.pack(fill="x", pady=10)

    # Crear un marco dinámico para mostrar reportes
    report_frame = tk.Frame(content_frame)
    report_frame.pack(fill="both", expand=True)

    # Subfunción para limpiar y mostrar reportes específicos
    def mostrar_reporte(tipo_reporte):
        # Limpiar el contenido previo en el reporte
        for widget in report_frame.winfo_children():
            widget.destroy()

        ventas = cargar_ventas()
        productos = cargar_productos()

        # Crear un diccionario de categorías basado en productos.json
        categorias_productos = {p["Nombre"]: p.get("Categoría", "Sin Categoría") for p in productos}

        # Crear un diccionario con los costos de los productos y convertir a float
        costos_productos = {
            p['Nombre']: float(p.get('Costo', 0)) for p in productos
        }

        if tipo_reporte == "ventas_totales":
            # Función para aplicar el filtro de fecha
            def seleccionar_rango_fechas():
                fecha_inicio = cal_inicio.get_date()
                fecha_fin = cal_fin.get_date()

                ventas_filtradas = [
                    venta for venta in ventas
                    if fecha_inicio <= datetime.strptime(venta["fecha"], "%Y-%m-%d %H:%M:%S").date() <= fecha_fin
                ]

                # Mostrar tabla de ventas filtradas
                for widget in tabla_frame.winfo_children():
                    widget.destroy()

                tree = ttk.Treeview(tabla_frame, columns=("Fecha", "Total"), show="headings", height=10)
                tree.heading("Fecha", text="Fecha")
                tree.heading("Total", text="Total ($)")
                tree.pack(fill="both", expand=True)

                for venta in ventas_filtradas:
                    tree.insert("", "end", values=(venta["fecha"], f"${venta['total']:.2f}"))

            # Función para aplicar filtro rápido (hoy, mes actual, año actual)
            def filtrar_fecha(tipo):
                hoy = datetime.now().date()
                if tipo == "hoy":
                    cal_inicio.set_date(hoy)
                    cal_fin.set_date(hoy)
                elif tipo == "mes":
                    primer_dia_mes = hoy.replace(day=1)
                    ultimo_dia_mes = hoy.replace(day=28) + timedelta(days=4)
                    ultimo_dia_mes -= timedelta(days=ultimo_dia_mes.day)
                    cal_inicio.set_date(primer_dia_mes)
                    cal_fin.set_date(ultimo_dia_mes)
                elif tipo == "año":
                    cal_inicio.set_date(hoy.replace(month=1, day=1))
                    cal_fin.set_date(hoy.replace(month=12, day=31))

                seleccionar_rango_fechas()

            # Crear filtros de fecha
            filtros_frame = tk.Frame(report_frame)
            filtros_frame.pack(fill="x", pady=10)

            tk.Label(filtros_frame, text="Desde:").pack(side="left", padx=5)
            cal_inicio = DateEntry(filtros_frame, date_pattern="yyyy-mm-dd")
            cal_inicio.pack(side="left", padx=5)

            tk.Label(filtros_frame, text="Hasta:").pack(side="left", padx=5)
            cal_fin = DateEntry(filtros_frame, date_pattern="yyyy-mm-dd")
            cal_fin.pack(side="left", padx=5)

            # Botones de acceso rápido
            botones_fecha = tk.Frame(filtros_frame)
            botones_fecha.pack(side="left", padx=10)
            tk.Button(botones_fecha, text="Hoy", command=lambda: filtrar_fecha("hoy")).pack(side="left", padx=5)
            tk.Button(botones_fecha, text="Mes Actual", command=lambda: filtrar_fecha("mes")).pack(side="left", padx=5)
            tk.Button(botones_fecha, text="Año Actual", command=lambda: filtrar_fecha("año")).pack(side="left", padx=5)

            tk.Button(filtros_frame, text="Aplicar Filtro", command=seleccionar_rango_fechas, bg="#333333", fg="white", font=("Arial", 10)).pack(side="left", padx=5)

            # Marco para la tabla
            tabla_frame = tk.Frame(report_frame)
            tabla_frame.pack(fill="both", expand=True)

            # Filtro inicial
            filtrar_fecha("hoy")

        elif tipo_reporte == "productos":
            # Crear filtro desplegable
            filtro_frame = tk.Frame(report_frame)
            filtro_frame.pack(fill="x", pady=10)

            tk.Label(filtro_frame, text="Mostrar Gráfico por:").pack(side="left", padx=5)
            opciones = ["Productos", "Categorías"]
            filtro_seleccionado = ttk.Combobox(filtro_frame, values=opciones, state="readonly")
            filtro_seleccionado.set(opciones[0])
            filtro_seleccionado.pack(side="left", padx=5)

            # Función para mostrar el gráfico
            def mostrar_grafico():
                for widget in report_frame.winfo_children()[1:]:
                    widget.destroy()

                datos = {}
                if filtro_seleccionado.get() == "Productos":
                    for venta in ventas:
                        for producto in venta["productos"]:
                            nombre = producto["Nombre"]
                            datos[nombre] = datos.get(nombre, 0) + producto["cantidad"]
                elif filtro_seleccionado.get() == "Categorías":
                    for venta in ventas:
                        for producto in venta["productos"]:
                            nombre = producto["Nombre"]
                            categoria = categorias_productos.get(nombre, "Sin Categoría")
                            datos[categoria] = datos.get(categoria, 0) + producto["cantidad"]

                # Crear gráfico con Plotly
                fig = go.Figure(
                    data=[
                        go.Bar(
                            x=list(datos.keys()),
                            y=list(datos.values()),
                            text=list(datos.values()),
                            textposition='auto'
                        )
                    ],
                    layout_title_text=f"Gráfico de {filtro_seleccionado.get()}"
                )
                
                fig.update_layout(
                width=500,  # Ajustar ancho
                height=350  # Ajustar alto
                )
                # Convertir figura de Plotly a imagen y mostrarla en Tkinter
                img_bytes = fig.to_image(format="png")
                img_data = BytesIO(img_bytes)
                img = Image.open(img_data)
                img = ImageTk.PhotoImage(img)

                canvas = tk.Canvas(report_frame, width=img.width(), height=img.height())
                canvas.pack(fill="both", expand=True)
                canvas.create_image(0, 0, anchor="nw", image=img)
                canvas.image = img

            filtro_seleccionado.bind("<<ComboboxSelected>>", lambda e: mostrar_grafico())
            mostrar_grafico()

        elif tipo_reporte == "estadisticas":
            # Marco de estadísticas
            estadisticas_frame = tk.Frame(report_frame)
            estadisticas_frame.pack(fill="both", expand=True)

            # Checkbox para incluir/excluir IVA
            incluir_iva = tk.BooleanVar(value=True)
            tk.Checkbutton(
                estadisticas_frame, 
                text="Incluir IVA en el cálculo", 
                variable=incluir_iva
            ).pack(anchor="w", pady=5)

            # Función para calcular ganancias
            def calcular_ganancias():
                fecha_inicio = cal_inicio.get_date()
                fecha_fin = cal_fin.get_date()

                # Filtrar ventas por fecha
                ventas_filtradas = [
                    venta for venta in ventas
                    if fecha_inicio <= datetime.strptime(venta["fecha"], "%Y-%m-%d %H:%M:%S").date() <= fecha_fin
                ]

                # Limpiar la tabla anterior
                for widget in tabla_frame.winfo_children():
                    widget.destroy()

                # Crear la tabla
                tree = ttk.Treeview(tabla_frame, columns=("Fecha", "Total", "Costo", "Ganancia"), show="headings", height=10)
                tree.heading("Fecha", text="Fecha")
                tree.heading("Total", text="Total ($)")
                tree.heading("Costo", text="Costo ($)")
                tree.heading("Ganancia", text="Ganancia ($)")
                tree.pack(fill="both", expand=True)

                # Calcular ganancias
                ganancia_total = 0
                for venta in ventas_filtradas:
                    total = venta['total']
                    # Calcular el costo basado en productos.json, convirtiendo a float
                    costo = sum(
                        costos_productos.get(item['Nombre'], 0) * float(item.get('cantidad', 0))
                        for item in venta['productos']
                    )
                    if incluir_iva.get():
                        iva = 21 / 100
                        ganancia = total - costo 
                        ganancia = ganancia * iva
                        ganancia = (total - costo) - ganancia
                        ganancia_total += ganancia 
                    else:
                        ganancia = total - costo 
                        ganancia_total += ganancia

                    tree.insert("", "end", values=(
                        venta["fecha"], 
                        f"${total:.2f}", 
                        f"${costo:.2f}", 
                        f"${ganancia:.2f}"
                    ))

                # Mostrar ganancia total
                ganancia_label.config(text=f"Ganancia Total: ${ganancia_total:.2f}")

            # Crear filtros de fecha
            filtros_frame = tk.Frame(estadisticas_frame)
            filtros_frame.pack(fill="x", pady=10)

            tk.Label(filtros_frame, text="Desde:").pack(side="left", padx=5)
            cal_inicio = DateEntry(filtros_frame, date_pattern="yyyy-mm-dd")
            cal_inicio.pack(side="left", padx=5)

            tk.Label(filtros_frame, text="Hasta:").pack(side="left", padx=5)
            cal_fin = DateEntry(filtros_frame, date_pattern="yyyy-mm-dd")
            cal_fin.pack(side="left", padx=5)

            # Botón para aplicar el filtro de fechas y calcular ganancias
            tk.Button(filtros_frame, text="Calcular Ganancias", command=calcular_ganancias).pack(side="left", padx=5)

            # Mostrar la etiqueta de ganancia total
            ganancia_label = tk.Label(estadisticas_frame, text="Ganancia Total: $0.00", font=("Arial", 14))
            ganancia_label.pack(pady=10)

            # Crear la tabla para mostrar las ventas y ganancias
            tabla_frame = tk.Frame(estadisticas_frame)
            tabla_frame.pack(fill="both", expand=True)

        # Crear botones para ver diferentes tipos de reportes
    tk.Button(botones_frame, text="Ventas Totales", command=lambda: mostrar_reporte("ventas_totales"), bg="#4CAF50", fg="white", font=("Arial", 10)).pack(side="left", fill="x", expand=True, padx=5, pady=5)
    tk.Button(botones_frame, text="Graficos de Venta", command=lambda: mostrar_reporte("productos"), bg="#FF9800", fg="white", font=("Arial", 10)).pack(side="left", fill="x", expand=True, padx=5, pady=5)
    tk.Button(botones_frame, text="Estadísticas", command=lambda: mostrar_reporte("estadisticas"), bg="#2196F3", fg="white", font=("Arial", 10)).pack(side="left", fill="x", expand=True, padx=5, pady=5)

    # Mostrar el reporte inicial (ventas_totales)
    mostrar_reporte("ventas_totales")