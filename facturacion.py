import tkinter as tk
from tkinter import messagebox
import json
import os
from datetime import datetime
from config_impresora import cargar_configuracion as cargar_conf_impresora
from configuracion_afip import cargar_configuracion as cargar_conf_afip
from afip import Afip
from fpdf import FPDF
import subprocess
import win32print
import requests
from jinja2 import Template  # Para renderizar la plantilla HTML

RUTA_VENTAS = os.path.join(os.path.dirname(__file__), "ventas.json")
import os

def crear_carpetas_comprobantes():
    """Crea las carpetas para almacenar facturas y tickets si no existen."""
    carpetas = ["comprobantes/facturas", "comprobantes/tickets"]
    for carpeta in carpetas:
        if not os.path.exists(carpeta):
            os.makedirs(carpeta)
# ========== CORE AFIP ==========
def generar_factura_electronica(venta):
    """Genera factura electrónica con validación de numeración AFIP"""
    try:
        config = cargar_conf_afip()
        config_imp = cargar_conf_impresora()
        
        # Configurar cliente AFIP
        afip = Afip({"CUIT": config["cuit"] or 20409378472})
        
        if not str(config["cuit"]) == "20409378472":
            afip.set_certificate(config["certificado"], config["clave_privada"])
            afip.environment = config["entorno"]

        # Obtener último autorizado desde AFIP
        pto_vta = config_imp.get("pto_vta", 1)
        try:
            ultimo_autorizado = afip.ElectronicBilling.getLastVoucher(pto_vta, 6)  # 6 = Factura B
        except:
            ultimo_autorizado = 0
            
        nuevo_numero = ultimo_autorizado + 1
        
        # Calcular neto e iva con precisión decimal
        neto = 0.0
        iva = 0.0
        
        for p in venta["productos"]:
            precio_unitario = round(p["precio"] / (1 + p.get("IVA", 21)/100), 2)
            subtotal_neto = precio_unitario * p["cantidad"]
            subtotal_iva = (p["precio"] * p["cantidad"]) - subtotal_neto
            
            neto += subtotal_neto
            iva += subtotal_iva

        # Redondear y formatear valores para AFIP
        neto = round(neto, 2)
        iva = round(iva, 2)
        total = round(neto + iva, 2)

        # Validar longitud máxima
        if len(str(int(neto))) > 13:
            raise ValueError("El importe neto excede los 13 dígitos permitidos")

        # Formatear fecha AFIP
        fecha_afip = datetime.now().strftime("%Y%m%d")  # Formato yyyymmdd
        
        data = {
            "MonId": "PES",
            "CantReg": 1,
            "PtoVta": pto_vta,
            "CbteTipo": 6,
            "Concepto": 1,
            "DocTipo": 99,
            "DocNro": 0,
            "CbteDesde": nuevo_numero,
            "CbteHasta": nuevo_numero,
            "CbteFch": fecha_afip,
            "ImpTotal": total,
            "ImpNeto": neto,
            "ImpIVA": iva,
            "MonCotiz": 1,
            "Iva": [{"Id": 5, "BaseImp": neto, "Importe": iva}]
        }
        
        res = afip.ElectronicBilling.createVoucher(data)
        
        if res.get("CAE"):
            venta.update({
                "cbte_numero": nuevo_numero,
                "cae": res["CAE"],
                "cae_vto": res["CAEFchVto"],
                "impuestos": {"neto": neto, "iva": iva, "total": total},
                "pto_vta": pto_vta,
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            return True
            
        messagebox.showerror("AFIP Error", f"Error: {res.get('message', 'Sin detalles')}")
        return False

    except Exception as e:
        messagebox.showerror("Error AFIP", f"Excepción: {str(e)}")
        return False

# ========== IMPRESIÓN ==========
def imprimir_comprobante(venta):
    """Maneja todos los tipos de salida"""
    config = cargar_conf_impresora()
    
    if config.get("modelo", "PDF") == "PDF":
        generar_pdf(venta)
    else:
        imprimir_termico(venta)

def generar_pdf(venta):
    """Genera factura PDF con diseño profesional"""
    try:
        # Primera instancia: Usar el SDK de AFIP para generar el PDF
        if generar_pdf_con_afipsdk(venta):
            return  # Si tiene éxito, salir de la función
        else:
            # Si falla, usar la implementación actual
            generar_pdf_con_fpdf(venta)
    except Exception as e:
        messagebox.showerror("PDF Error", f"Error al generar PDF: {str(e)}")

def generar_pdf_con_afipsdk(venta):
    """Genera el PDF utilizando el SDK de AFIP"""
    try:
        config = cargar_conf_impresora()
        crear_carpetas_comprobantes()
        # Cargar la plantilla HTML desde el archivo
        with open("factura_template.html", "r", encoding="utf-8") as file:
            template_html = file.read()

        # Renderizar la plantilla con los datos de la venta
        template = Template(template_html)
        html_final = template.render(
            bill={
                "type": "B",  # Tipo de factura (B)
                "point_of_sale": venta["pto_vta"],
                "number": venta["cbte_numero"],
                "date": venta["fecha"],
                "CAE": venta["cae"],
                "CAE_expiration": venta["cae_vto"],
            },
            business_data={
                "business_name": config["empresa"],
                "address": config["direccion"],
                "vat_condition": "Responsable Inscripto",  # Condición frente al IVA
                "tax_id": config["cuit"],
                "gross_income_id": "123456789",  # Ingresos brutos (puedes ajustar)
                "start_date": "01/01/2020",  # Fecha de inicio de actividades (puedes ajustar)
            },
            billing_data={
                "tax_id": "00-00000000-0",  # CUIT del cliente (puedes ajustar)
                "name": "Cliente Final",  # Nombre del cliente
                "vat_condition": "Consumidor Final",  # Condición frente al IVA del cliente
                "address": "Sin especificar",  # Domicilio del cliente
                "payment_method": "Contado",  # Condición de venta
            },
            items=[
                {
                    "code": idx + 1,
                    "name": p["Nombre"],
                    "quantity": p["cantidad"],
                    "measurement_unit": "unidad",  # Unidad de medida (puedes ajustar)
                    "price": p["precio"],
                    "percent_subsidized": 0,  # Porcentaje de bonificación (puedes ajustar)
                    "impost_subsidized": 0,  # Importe de bonificación (puedes ajustar)
                    "subtotal": p["precio"] * p["cantidad"],
                }
                for idx, p in enumerate(venta["productos"])
            ],
            overall={
                "subtotal": venta["impuestos"]["neto"],
                "impost_tax": 0,  # Otros tributos (puedes ajustar)
                "total": venta["impuestos"]["total"],
            },
            qr_code_image="https://example.com/qr.png",  # URL del QR (puedes ajustar)
        )

        # Crear instancia de Afip
        CUIT = config.get("cuit", 20409378472)  # Usar CUIT de desarrollo si no está configurado
        afip = Afip({"CUIT": CUIT})

        # Opciones para el PDF
        options = {
            "width": 8,          # Ancho de la página en pulgadas
            "marginLeft": 0.4,   # Margen izquierdo
            "marginRight": 0.4,  # Margen derecho
            "marginTop": 0.4,    # Margen superior
            "marginBottom": 0.4  # Margen inferior
        }

        # Generar el PDF
        res = afip.ElectronicBilling.createPDF({
            "html": html_final,
            "file_name": f"Factura_{venta['cbte_numero']}",  # Nombre del archivo
            "options": options
        })

        # Descargar y guardar el PDF
        response = requests.get(res['file'])
        nombre_archivo = f"comprobantes/facturas/Factura_{venta['cbte_numero']}.pdf"
        with open(nombre_archivo, 'wb') as f:
            f.write(response.content)

        # Abrir el PDF automáticamente
        subprocess.Popen([nombre_archivo], shell=True)
        return True  # Indicar que el PDF se generó correctamente

    except Exception as e:
        print(f"Error al generar PDF con AFIP SDK: {str(e)}")
        return False  # Indicar que falló

def generar_pdf_con_fpdf(venta):
    """Genera factura PDF con FPDF (implementación actual)"""
    try:
        config = cargar_conf_impresora()
        crear_carpetas_comprobantes()
        pdf = FPDF()
        pdf.add_page()
        
        # ========== ESTILOS ==========
        primary_color = (0, 0, 0)  # Negro
        secondary_color = (64, 64, 64)  # Gris oscuro
        accent_color = (41, 128, 185)  # Azul corporativo
        
        # ========== ENCABEZADO ==========
        pdf.set_font("Helvetica", "B", 16)
        pdf.set_text_color(*primary_color)
        pdf.cell(0, 10, config['empresa'], 0, 1, "R")
        
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(*secondary_color)
        pdf.cell(0, 5, config['direccion'], 0, 1, "R")
        pdf.cell(0, 5, f"CUIT: {config['cuit']} | Tel: {config['telefono']}", 0, 1, "R")
        pdf.ln(15)
        
        # ========== DATOS FACTURA ==========
        pdf.set_fill_color(240, 240, 240)
        pdf.rect(10, 45, 190, 25, "F")
        
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(*accent_color)
        pdf.cell(95, 10, f"FACTURA N°: {venta['cbte_numero']}", 0, 0)
        pdf.cell(95, 10, f"Fecha: {venta['fecha']}", 0, 1, "R")
        
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(*secondary_color)
        pdf.cell(95, 5, f"Punto de Venta: {venta['pto_vta']}", 0, 0)
        pdf.cell(95, 5, f"CAE: {venta['cae']}", 0, 1, "R")
        pdf.cell(95, 5, f"Vencimiento CAE: {venta['cae_vto']}", 0, 1, "R")
        pdf.ln(10)
        
        # ========== DATOS CLIENTE ==========
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(*primary_color)
        pdf.cell(0, 10, "Cliente", 0, 1)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(*secondary_color)
        pdf.cell(0, 5, "Nombre: Cliente Final", 0, 1)
        pdf.cell(0, 5, "CUIT/CUIL: 00-00000000-0", 0, 1)
        pdf.cell(0, 5, "Condición de IVA: Consumidor Final", 0, 1)
        pdf.ln(10)
        
        # ========== TABLA DE PRODUCTOS ==========
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(*primary_color)
        pdf.set_fill_color(230, 230, 230)
        pdf.cell(100, 8, "Descripción", 1, 0, "C", 1)
        pdf.cell(30, 8, "Cantidad", 1, 0, "C", 1)
        pdf.cell(30, 8, "P. Unitario", 1, 0, "C", 1)
        pdf.cell(30, 8, "Total", 1, 1, "C", 1)
        
        # Productos
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(*secondary_color)
        for p in venta["productos"]:
            pdf.cell(100, 8, p["Nombre"][:50], 1, 0)
            pdf.cell(30, 8, str(p["cantidad"]), 1, 0, "C")
            pdf.cell(30, 8, f"${p['precio']:.2f}", 1, 0, "R")
            pdf.cell(30, 8, f"${p['precio'] * p['cantidad']:.2f}", 1, 1, "R")
        
        # ========== TOTALES ==========
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(*primary_color)
        pdf.cell(160, 10, "Subtotal:", 0, 0, "R")
        pdf.cell(30, 10, f"${venta['impuestos']['neto']:.2f}", 0, 1, "R")
        
        pdf.cell(160, 10, "IVA 21%:", 0, 0, "R")
        pdf.cell(30, 10, f"${venta['impuestos']['iva']:.2f}", 0, 1, "R")
        
        pdf.set_text_color(*accent_color)
        pdf.cell(160, 10, "Total:", 0, 0, "R")
        pdf.cell(30, 10, f"${venta['impuestos']['total']:.2f}", 0, 1, "R")
        
        # ========== PIE DE PÁGINA ==========
        pdf.set_y(-30)
        pdf.set_font("Helvetica", "I", 8)
        pdf.set_text_color(*secondary_color)
        pdf.multi_cell(0, 5, config['mensaje'] + "\nEste documento es un comprobante electrónico válido según normativa RG AFIP 4291/16", 0, "C")
        
        # Guardar PDF en la carpeta de facturas
        nombre_archivo = f"comprobantes/facturas/Factura_{venta['cbte_numero']}.pdf"
        pdf.output(nombre_archivo)
        subprocess.Popen([nombre_archivo], shell=True)
        
    except Exception as e:
        messagebox.showerror("PDF Error", f"Error al generar PDF: {str(e)}")

def imprimir_termico(venta):
    """Impresión para tickets térmicos con formato profesional"""
    try:
        config = cargar_conf_impresora()
        crear_carpetas_comprobantes()
        # Encabezado
        contenido = [
            f"{config['empresa'].center(32)}",
            f"CUIT: {config['cuit']}",
            "-" * 32,
            f"Fecha: {venta['fecha']}",
            f"CAE: {venta['cae']}",
            "-" * 32,
            "Producto          Cant   Precio".ljust(32),
            "-" * 32
        ]
        
        # Detalle de productos
        total = 0.0
        for p in venta["productos"]:
            nombre = p["Nombre"][:15].ljust(15)
            cantidad = str(p["cantidad"]).center(5)
            precio_unit = f"${p['precio']:.2f}".rjust(8)
            linea = f"{nombre} {cantidad} {precio_unit}"
            contenido.append(linea)
            total += p["precio"] * p["cantidad"]
        
        # Totales
        contenido.extend([
            "-" * 32,
            f"TOTAL: ${total:.2f}".rjust(32),
            "-" * 32,
            config['mensaje'].center(32)
        ])
        # Guardar el ticket en la carpeta de tickets
        nombre_archivo = f"comprobantes/tickets/Ticket_{venta['cbte_numero']}.txt"
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            f.write("\n".join(contenido))

        # Impresión
        if config["impresora"] == "Microsoft Print to PDF":
            generar_pdf_termico(contenido)  # Nueva función para PDF térmico
        else:
            imprimir_texto_termico("\n".join(contenido), config["impresora"])

    except Exception as e:
        messagebox.showerror("Impresión Error", f"Error: {str(e)}")

def generar_pdf_termico(contenido):
    """Genera PDF con formato de ticket térmico"""
    try:
        pdf = FPDF(orientation='P', unit='mm', format=(80, 200))
        pdf.add_page()
        pdf.set_font("Courier", size=10)
        
        for linea in contenido:
            pdf.cell(0, 5, txt=linea, ln=1)
        
        nombre = f"ticket_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf.output(nombre)
        subprocess.Popen([nombre], shell=True)
        
    except Exception as e:
        messagebox.showerror("PDF Error", f"Error: {str(e)}")

def imprimir_texto_termico(contenido, impresora):
    """Envía texto directamente a la impresora térmica"""
    try:
        hprinter = win32print.OpenPrinter(impresora)
        win32print.StartDocPrinter(hprinter, 1, ("Ticket", None, "RAW"))
        win32print.StartPagePrinter(hprinter)
        win32print.WritePrinter(hprinter, contenido.encode("latin-1"))
        win32print.EndPagePrinter(hprinter)
        win32print.ClosePrinter(hprinter)
    except Exception as e:
        messagebox.showerror("Error Impresora", f"No se pudo imprimir: {str(e)}")

# ========== INTERFAZ ==========
def iniciar_proceso_facturacion(venta):
    """Flujo completo de facturación"""
    if generar_factura_electronica(venta):
        respuesta = messagebox.askyesno(
            "Impresión", 
            "¿Desea imprimir el comprobante?",
            detail="Seleccione Sí para imprimir, No para solo generar PDF"
        )
        if respuesta:
            imprimir_comprobante(venta)
        else:
            generar_pdf(venta)