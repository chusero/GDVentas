import json
import os

# Ajustar la ruta relativa al archivo JSON
RUTA_PRODUCTOS = os.path.join(os.path.dirname(__file__), "productos.json")

# Función para guardar productos en JSON
def guardar_productos(productos):
    """
    Guarda la lista de productos en un archivo JSON.
    """
    try:
        with open(RUTA_PRODUCTOS, 'w') as f:
            json.dump(productos, f, indent=4)
    except Exception as e:
        print(f"Error al guardar productos: {e}")

# Función para cargar productos desde JSON
def cargar_productos():
    """
    Carga los productos desde un archivo JSON.
    Si el archivo no existe, retorna una lista vacía.
    """
    if os.path.exists(RUTA_PRODUCTOS):
        try:
            with open(RUTA_PRODUCTOS, 'r') as f:
                productos = json.load(f)
            return productos
        except json.JSONDecodeError:
            print("Error al leer el archivo JSON. El archivo podría estar dañado.")
            return []
    else:
        print("El archivo de productos no existe. Retornando lista vacía.")
        return []