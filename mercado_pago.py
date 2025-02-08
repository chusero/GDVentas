# mercado_pago.py
import os
import mercadopago
import logging
import uuid
from datetime import datetime
from typing import Dict, Optional, Tuple
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import json
# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('payments.log'), logging.StreamHandler()]
)

load_dotenv()

class PaymentGateway:
    def __init__(self, firebase_manager):
        self.sdk = None
        self.firebase = firebase_manager
        self._initialize_sdk()
        self.local_payments_file = "local_payments.json"
        
        # Configuración de precios dinámica
        self.price_tiers = {
            'testing': {7: 1.00, 30: 2.00, 90: 5.00, 365: 10.00},  # Precios de prueba
            'production': {7: 1.00, 30: 15000.00, 90: 40000.00, 365: 120000.00}
        }
    
    def _initialize_sdk(self):
        """Inicializa el SDK de MercadoPago con manejo de errores"""
        try:
            access_token = os.getenv('MERCADOPAGO_ACCESS_TOKEN')
            if not access_token:
                raise ValueError("MERCADOPAGO_ACCESS_TOKEN no configurado")
                
            self.sdk = mercadopago.SDK(access_token)
            logging.info("SDK de MercadoPago inicializado correctamente")
            
        except Exception as e:
            logging.error(f"Error inicializando SDK: {str(e)}")
            self.sdk = None
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((Exception,)),
        reraise=True
    )
    def create_payment_link(self, user_email: str, duration_days: int, metadata: Dict) -> Tuple[Optional[str], Optional[str]]:
    
        try:
            # Generar identificadores únicos
            payment_id = str(uuid.uuid4())
            external_reference = f"{user_email}|{payment_id}"
            
            # Configurar preferencia de pago
            preference = {
                "items": [
                    {
                        "title": f"Licencia de {duration_days} días",
                        "quantity": 1,
                        "unit_price": self._get_price(duration_days),
                        "description": f"Suscripción para {user_email}",
                        "currency_id": "ARS",
                    }
                ],
                "payer": {"email": user_email},
                "external_reference": external_reference,
                "auto_return": "approved",
                "notification_url": os.getenv('MERCADOPAGO_WEBHOOK_URL'),
                "back_urls": {
                    "success": f"{os.getenv('FRONTEND_URL')}/payment/success",
                    "failure": f"{os.getenv('FRONTEND_URL')}/payment/failure",
                    "pending": f"{os.getenv('FRONTEND_URL')}/payment/pending"
                },
                "metadata": {
                    "activation_code": metadata['activation_code'],  # Código corto
                    "payment_id": payment_id  # UUID interno
                }
            }
        
        # Resto del código igual...
            
            # Crear preferencia
            result = self.sdk.preference().create(preference)
            
            if result['status'] in [200, 201]:
                payment_link = result['response']['init_point']
                logging.info(f"Link de pago generado para {user_email}")
                self._store_payment_attempt(payment_id, user_email, duration_days, 'pending')
                return payment_link, payment_id
            
            logging.error(f"Error MercadoPago: {result['response']}")
            return None, None
            
        except Exception as e:
            logging.error(f"Error creando link de pago: {str(e)}")
            payment_id = self._store_local_payment(user_email, duration_days, metadata)
            return None, payment_id
    
    def _get_price(self, duration_days: int) -> float:
        """Obtiene el precio según el entorno y duración"""
        environment = os.getenv('ENVIRONMENT', 'production')
        return self.price_tiers[environment].get(duration_days, 1000.00)
    
    def _store_payment_attempt(self, payment_id: str, email: str, days: int, status: str):
        """Registra el intento de pago en Firebase"""
        try:
            payment_data = {
                'user_email': email,
                'duration_days': days,
                'status': status,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            if self.firebase.is_connected():
                self.firebase.db.collection("payment_attempts").document(payment_id).set(payment_data)
            else:
                self._store_local_payment(email, days, {'status': status})
                
        except Exception as e:
            logging.error(f"Error registrando pago: {str(e)}")
    
    def _store_local_payment(self, email: str, days: int, metadata: Dict) -> str:
        """Almacena pagos localmente cuando hay fallos de conexión"""
        try:
            payment_id = str(uuid.uuid4())
            payment_data = {
                'user_email': email,
                'duration_days': days,
                'metadata': metadata,
                'created_at': datetime.now().isoformat(),
                'local_storage': True
            }
            
            with open(self.local_payments_file, 'a') as f:
                f.write(f"{payment_id},{json.dumps(payment_data)}\n")
                
            return payment_id
            
        except Exception as e:
            logging.error(f"Error almacenando pago local: {str(e)}")
            return "local-error"
    
    def process_webhook_event(self, event_data: Dict) -> bool:
        try:
            payment_id = event_data.get('data', {}).get('id')
            if not payment_id:
                logging.error("No se encontró ID de pago")
                return False

            # Obtener detalles del pago
            payment_info = self.sdk.payment().get(payment_id)
            if payment_info['status'] != 200:
                return False

            payment_data = payment_info['response']
            metadata = payment_data.get('metadata', {})
            
            # Actualizar Firebase con ambos códigos
            return self._update_payment_status(
                external_ref=payment_data['external_reference'],
                status=payment_data['status'],
                activation_code=metadata.get('activation_code'),
                payment_id=metadata.get('payment_id')
            )

        except Exception as e:
            logging.error(f"Error procesando webhook: {str(e)}")
            return False
    
    # En mercado_pago.py
    def _update_payment_status(self, external_ref: str, status: str, activation_code: str, payment_id: str) -> bool:
        try:
            email, _ = external_ref.split('|')
            
            # Actualizar el documento en Firebase
            update_data = {
                "status": status,
                "activation_code": activation_code,
                "updated_at": datetime.now().isoformat()
            }
            
            self.firebase.db.collection("payment_attempts").document(payment_id).update(update_data)
            
            if status == "approved":
                self._activate_license(email, payment_id)
                
            return True
            
        except Exception as e:
            logging.error(f"Error actualizando estado: {str(e)}")
            return False
    
    def _activate_license(self, user_email: str, payment_id: str):
        """Activa una licencia después de pago exitoso"""
        try:
            # Obtener detalles del pago
            if self.firebase.is_connected():
                doc = self.firebase.db.collection("payment_attempts").document(payment_id).get()
                duration = doc.to_dict().get('duration_days', 30)
                activation_code = doc.to_dict().get('metadata', {}).get('activation_code', '')  # Obtener el código corto
            else:
                duration = 30  # Valor por defecto si no hay conexión
                activation_code = ''  # Valor por defecto
                
            # Lógica de activación
            self.firebase.guardar_licencia_pendiente(
                correo=user_email,  # Parámetro 1: correo
                codigo=payment_id,  # Parámetro 2: codigo (UUID)
                codigo_activacion=activation_code,  # Parámetro 3: código corto
                duracion=duration  # Parámetro 4: duración
            )
            self.firebase.activar_licencia(payment_id)
            
            logging.info(f"Licencia activada para {user_email}")
            
        except Exception as e:
            logging.error(f"Error activando licencia: {str(e)}")

    def sync_local_payments(self):
        """Sincroniza pagos locales con Firebase"""
        try:
            if not os.path.exists(self.local_payments_file):
                return
                
            with open(self.local_payments_file, 'r+') as f:
                for line in f:
                    payment_id, payment_data = line.strip().split(',', 1)
                    data = json.loads(payment_data)
                    
                    if self.firebase.is_connected():
                        self.firebase.db.collection("payment_attempts").document(payment_id).set(data)
                
                f.truncate(0)
                
            logging.info("Pagos locales sincronizados con Firebase")
            
        except Exception as e:
            logging.error(f"Error sincronizando pagos locales: {str(e)}")