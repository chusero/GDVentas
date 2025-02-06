import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timedelta
import json
import os
import hashlib
# Cargar credenciales
cred = credentials.Certificate("firebase-credenciales.json")

# Inicializar Firebase
firebase_admin.initialize_app(cred)

# Obtener referencia a Firestore
db = firestore.client()
RUTA_DATOS_LOCAL = os.path.join(os.path.dirname(__file__), "datos_local.json")
def cargar_datos_local():
    if not os.path.exists(RUTA_DATOS_LOCAL):
        return {"usuarios": {}, "licencias": {}}
    with open(RUTA_DATOS_LOCAL, "r") as f:
        return json.load(f)

def guardar_datos_local(datos):
    with open(RUTA_DATOS_LOCAL, "w") as f:
        json.dump(datos, f, indent=4)

print("Conexión exitosa y documento agregado.") 

def registrar_usuario(correo, contraseña):
    datos_local = cargar_datos_local()
    
    # Verificar si el correo ya existe
    if correo in datos_local["usuarios"]:
        return "El correo ya está registrado."
    
    # Hash de la contraseña
    contraseña_hash = hashlib.sha256(contraseña.encode()).hexdigest()
    
    # Crear usuario en Firebase (si hay conexión)
    try:
        db.collection("usuarios").document(correo).set({
            "contraseña": contraseña_hash,
            "fecha_expiracion": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),  # Licencia de prueba
            "dias_offline": 0
        })
    except Exception as e:
        # Guardar localmente si no hay conexión
        datos_local["usuarios"][correo] = {
            "contraseña": contraseña_hash,
            "fecha_expiracion": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
            "dias_offline": 0
        }
        guardar_datos_local(datos_local)
        return "Registro exitoso (modo offline)."
    
    return "Registro exitoso."