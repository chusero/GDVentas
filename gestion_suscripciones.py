# gestion_suscripciones.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from firebase_db import FirebaseManager
from mercado_pago import PaymentGateway
from email_sender import EmailSender
import webbrowser
import logging
import random
import string

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('subscriptions.log'), logging.StreamHandler()]
)

class SubscriptionManager:
    def __init__(self, firebase_manager: FirebaseManager):
        self.firebase = firebase_manager
        self.payment_gateway = PaymentGateway(firebase_manager)
        self.email_sender = EmailSender()
        self.sent_codes = {}  # Almacena códigos enviados por correo

    def create_subscription(self, user_email: str, duration_days: int) -> tuple:
        try:
            # Generar código corto (8 caracteres)
            activation_code = self._generate_activation_code()  # Ej: "FU6NUTE4"
            
            # Generar payment_id (UUID para MercadoPago)
            payment_link, payment_id = self.payment_gateway.create_payment_link(
                user_email,
                duration_days,
                {'activation_code': activation_code}  # Enviar código corto como metadata
            )

            if payment_link:
                # Guardar AMBOS códigos en Firebase
                self.firebase.guardar_licencia_pendiente(
                    correo=user_email,
                    codigo=payment_id,          # UUID largo (para referencia interna)
                    codigo_activacion=activation_code,  # Código corto
                    duracion=duration_days
                )
                
                # Enviar solo el código corto por correo
                self.email_sender.send_email('codigo_licencia', {
                    'destinatario': user_email,
                    'codigo': activation_code,  # Código corto
                    'duracion_dias': duration_days
                })
                
                return payment_link, payment_id

            return None, None

        except Exception as e:
            logging.error(f"Error creando suscripción: {str(e)}")
            return None, None

    def activate_subscription(self, user_email: str, activation_code: str) -> bool:
        """Activa una suscripción validando el código"""
        try:
            # Verificar código
            if self.sent_codes.get(user_email) != activation_code:
                messagebox.showerror("Error", "Código de activación inválido")
                return False
                
            # Buscar pago correspondiente
            if self.firebase.is_connected():
                docs = self.firebase.db.collection("licencias_pendientes") \
                    .where("correo", "==", user_email) \
                    .where("codigo_activacion", "==", activation_code) \
                    .stream()
                    
                licencia = next((doc.to_dict() for doc in docs), None)
                
                if licencia and licencia.get("activa", False):
                    # Activar licencia
                    self.firebase.activar_licencia(licencia['codigo'])
                    del self.sent_codes[user_email]  # Eliminar código usado
                    return True
                    
            return False

        except Exception as e:
            logging.error(f"Error activando suscripción: {str(e)}")
            return False

    def _generate_activation_code(self) -> str:
        """Genera un código de activación único"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def mostrar_registro_licencia(parent, firebase_manager):
    """Muestra la ventana de registro de suscripción"""
    manager = SubscriptionManager(firebase_manager)
    
    ventana = tk.Toplevel(parent)
    ventana.title("Registro de Suscripción")
    ventana.geometry("400x300")
    
    # Campo para correo
    ttk.Label(ventana, text="Correo electrónico:").pack(pady=10)
    entry_correo = ttk.Entry(ventana, width=30)
    entry_correo.pack(pady=5)
    
    # Selección de duración
    ttk.Label(ventana, text="Duración:").pack(pady=10)
    combo_duracion = ttk.Combobox(ventana, values=[7, 30, 90, 365], state="readonly")
    combo_duracion.pack(pady=5)
    combo_duracion.set(30)
    
    # Botón de pago
    def procesar_pago():
        correo = entry_correo.get().strip()
        duracion = int(combo_duracion.get())
        
        if "@" not in correo:
            messagebox.showerror("Error", "Correo inválido")
            return
            
        payment_link, _ = manager.create_subscription(correo, duracion)
        
        if payment_link:
            webbrowser.open(payment_link)
            ventana.destroy()
        else:
            messagebox.showerror("Error", "No se pudo generar el pago")
    
    ttk.Button(ventana, text="Pagar con MercadoPago", command=procesar_pago).pack(pady=20)

def mostrar_activacion_licencia(parent, firebase_manager):
    """Muestra la ventana de activación de licencia"""
    manager = SubscriptionManager(firebase_manager)
    
    ventana = tk.Toplevel(parent)
    ventana.title("Activar Licencia")
    ventana.geometry("400x200")
    
    # Campo para correo
    ttk.Label(ventana, text="Correo electrónico:").pack(pady=10)
    entry_correo = ttk.Entry(ventana, width=30)
    entry_correo.pack(pady=5)
    
    # Campo para código
    ttk.Label(ventana, text="Código de activación:").pack(pady=10)
    entry_codigo = ttk.Entry(ventana, width=25)
    entry_codigo.pack(pady=5)
    
    # Botón de activación
    def activar():
        correo = entry_correo.get().strip()
        codigo = entry_codigo.get().strip()
        
        if not correo or "@" not in correo:
            messagebox.showerror("Error", "Correo inválido")
            return
            
        if not codigo or len(codigo) != 8:
            messagebox.showerror("Error", "Código inválido")
            return
            
        if manager.activate_subscription(correo, codigo):
            messagebox.showinfo("Éxito", "Licencia activada correctamente")
            ventana.destroy()
        else:
            messagebox.showerror("Error", "Código inválido o pago no verificado")
    
    ttk.Button(ventana, text="Activar", command=activar).pack(pady=20)
