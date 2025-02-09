#aapp.py
from interfaz import crear_interfaz
from logo_de_carga import mostrar_logo_carga
from autenticacion import Autenticacion
from gestion_suscripciones import mostrar_registro_licencia, mostrar_activacion_licencia
from firebase_db import FirebaseManager
import tkinter as tk
from tkinter import messagebox
from dotenv import load_dotenv
import logging
import sys
import absl.logging
absl.logging.set_verbosity(absl.logging.ERROR)  # Ocultar logs de ABSL
# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('app.log'), logging.StreamHandler()]
)

def abrir_gestion_suscripciones(root, firebase_manager):
    """Abre la ventana de gestión de suscripciones"""
    try:
        mostrar_registro_licencia(root, firebase_manager)
    except Exception as e:
        logging.error(f"Error abriendo gestión de suscripciones: {str(e)}")
        messagebox.showerror("Error", "No se pudo abrir la gestión de suscripciones")

def verificar_suscripcion(usuario_actual, firebase_manager):
    """Verifica el estado de la suscripción del usuario"""
    try:
        if usuario_actual['rol'] != 'admin':
            from gestion_suscripciones import SubscriptionManager
            manager = SubscriptionManager(firebase_manager)
            status = manager.check_subscription_status(usuario_actual['username'])
            
            if status.get('status') != 'active':
                messagebox.showwarning(
                    "Suscripción Requerida",
                    "¡Tu licencia ha expirado o no tienes una suscripción activa!\n\n"
                    "Por favor, renueva tu suscripción para continuar usando el sistema."
                )
                abrir_gestion_suscripciones(root, firebase_manager)
                return False
        return True
    except Exception as e:
        logging.error(f"Error verificando suscripción: {str(e)}")
        return False

if __name__ == "__main__":
    try:
        # Cargar variables de entorno
        load_dotenv()
        
        # Inicializar Firebase
        firebase = FirebaseManager()
        
        # Crear ventana principal
        root = tk.Tk()
        root.withdraw()  # Ocultar inicialmente
        
        # Mostrar logo de carga
        mostrar_logo_carga(root)
        
        # Autenticación
        auth = Autenticacion(root)
        root.wait_window(auth.login_window)
        
        if hasattr(auth, 'usuario_actual'):
            # Verificar suscripción
            if not verificar_suscripcion(auth.usuario_actual, firebase):
                root.destroy()
                sys.exit()
            
            # Crear interfaz principal
            crear_interfaz(root, auth.usuario_actual, firebase)
            
            # Configurar menú de suscripciones
            def configurar_menu_suscripciones():
                from interfaz import menu_bar
                if menu_bar:
                    menu_bar.entryconfig(
                        "Administración",
                        menu=lambda: [
                            ("Gestión de Suscripciones", lambda: abrir_gestion_suscripciones(root, firebase)),
                            ("Activar Licencia", lambda: mostrar_activacion_licencia(root, firebase))
                        ]
                    )
            
            configurar_menu_suscripciones()
            
            root.mainloop()
        else:
            root.destroy()
            
    except Exception as e:
        logging.critical(f"Error en la aplicación: {str(e)}")
        messagebox.showerror("Error crítico", "Se produjo un error inesperado")
        sys.exit(1)
