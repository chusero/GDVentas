import pywhatkit
import json
import os
from datetime import datetime

# Ajustar las rutas relativas a los archivos JSON
RUTA_PROVEEDORES = os.path.join(os.path.dirname(__file__), "proveedores.json")
RUTA_PEDIDOS = os.path.join(os.path.dirname(__file__), "pedidos.json")
RUTA_HISTORIAL_PEDIDOS = os.path.join(os.path.dirname(__file__), "historial_pedidos.json")

def cargar_proveedores():
    try:
        with open(RUTA_PROVEEDORES, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: No se encontró el archivo 'proveedores.json'.")
        return None

def cargar_pedidos():
    try:
        with open(RUTA_PEDIDOS, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: No se encontró el archivo 'pedidos.json'.")
        return None

def guardar_historial_pedidos(pedidos, proveedor):
    historial = []
    try:
        with open(RUTA_HISTORIAL_PEDIDOS, "r") as f:
            historial = json.load(f)
    except FileNotFoundError:
        pass

    for pedido in pedidos:
        pedido_historial = {
            "Fecha": datetime.now().strftime("%y-%m-%d %H:%M:%S"),
            "Proveedor": proveedor,
            "Productos": pedido["Productos"]
        }
        historial.append(pedido_historial)

    with open(RUTA_HISTORIAL_PEDIDOS, "w") as f:
        json_str = json.dumps(historial, ensure_ascii=False, indent=4)
        f.write(json_str.replace("Categoría", "Categor\u00eda").replace("Código de Barras", "C\u00f3digo de Barras"))

def enviar_mensaje(proveedor, numero, mensaje):
    if not numero.startswith("+"):
        numero = "+54" + numero  # Añade el código de país de Argentina si falta

    # Usando PyWhatKit para enviar el mensaje
    hora_envio = datetime.now().hour
    minuto_envio = datetime.now().minute + 2  # Añadir 2 minutos para dar tiempo de ejecución

    pywhatkit.sendwhatmsg(numero, mensaje, hora_envio, minuto_envio)
    print(f"Mensaje enviado a {proveedor}.")

def generar_mensaje(pedido):
    mensaje = pedido["Mensaje"] + "\n\n"
    
    # Crear la lista de productos en forma de texto sin incluir el precio y agregando el código de barras
    for producto in pedido["Productos"]:
        mensaje += "- {} (Cantidad: {}, Código de Barras: {})\n".format(producto['Nombre'], producto['Cantidad'], producto.get('C\u00f3digo de Barras'))

    return mensaje

def vaciar_base_datos(ruta):
    with open(ruta, "w") as f:
        json.dump([], f, ensure_ascii=False, indent=4)

def main():
    proveedores = cargar_proveedores()
    pedidos = cargar_pedidos()
    if not proveedores or not pedidos:
        return

    # Asegurarse de que solo hay un proveedor en proveedores.json
    if len(proveedores) != 1:
        print("Error: Se esperaba un único proveedor en proveedores.json.")
        return

    proveedor_seleccionado = proveedores[0]
    nombre_proveedor = proveedor_seleccionado["nombre"]
    numero_proveedor = proveedor_seleccionado["numero"]

    # Guardar el historial de pedidos antes de enviarlos
    guardar_historial_pedidos(pedidos, nombre_proveedor)

    for pedido in pedidos:
        try:
            mensaje = generar_mensaje(pedido)
            enviar_mensaje(nombre_proveedor, numero_proveedor, mensaje)
        except KeyError as e:
            print(f"Error: Clave no encontrada en el pedido: {e}")
            print(pedido)  # Añadir esta línea para depurar el contenido del pedido
        except TypeError as e:
            print(f"Error: Tipo de dato incorrecto en el pedido: {e}")

    # Vaciar la base de datos proveedores.json y pedidos.json al finalizar la ejecución
    vaciar_base_datos(RUTA_PROVEEDORES)
    vaciar_base_datos(RUTA_PEDIDOS)

if __name__ == "__main__":
    main()
