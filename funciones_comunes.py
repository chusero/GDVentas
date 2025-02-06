import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

def actualizar_tabla(tabla, productos):
    """
    Actualiza la tabla de productos en la interfaz con los productos dados.
    """
    for fila in tabla.get_children():
        tabla.delete(fila)
    for producto in productos:
        tabla.insert('', 'end', values=producto)

def mostrar_mensaje(titulo, mensaje):
    """
    Muestra un mensaje en la interfaz.
    """
    messagebox.showinfo(titulo, mensaje)

def cargar_imagen(nombre_archivo):
    """
    Carga una imagen desde la ruta especificada y la devuelve.
    """
    ruta_base = os.path.dirname(__file__)
    ruta_completa = os.path.join(ruta_base, nombre_archivo)
    try:
        img = Image.open(ruta_completa)
        img = img.resize((60, 60), Image.ANTIALIAS)  # Redimensionar la imagen
        img_tk = ImageTk.PhotoImage(img)
        return img_tk
    except Exception as e:
        print(f"Error al cargar la imagen {nombre_archivo}: {e}")
        return None