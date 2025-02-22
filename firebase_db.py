# firebase_db.py
import firebase_admin
from firebase_admin import credentials, firestore, exceptions
from datetime import datetime, timedelta
import os
import json
import logging
from dotenv import load_dotenv
from typing import Optional, Dict, Any

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('firebase.log'), logging.StreamHandler()]
)

load_dotenv()

class FirebaseManager:
    _instance = None
    LOCAL_LICENSES_FILE = "local_licenses.json"
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self.db = None
        self._initialize_firebase()
        self._setup_local_files()
        
    def _initialize_firebase(self):
        try:
            # Obtener el JSON de la variable de entorno
            firebase_creds = os.getenv("FIREBASE_CREDENTIALS")
            if not firebase_creds:
                raise ValueError("FIREBASE_CREDENTIALS no configurada")
    
            # Convertir el string JSON a un diccionario
            cred_dict = json.loads(firebase_creds)
    
            # Inicializar Firebase
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
            self.db = firestore.client()
            logging.info("Conexión a Firebase establecida exitosamente")

        except json.JSONDecodeError as e:
            logging.error(f"ERROR: JSON inválido en FIREBASE_CREDENTIALS. Detalle: {str(e)}")
        except Exception as e:
            logging.error(f"ERROR inicializando Firebase: {str(e)}")
    
    def _setup_local_files(self):
        """Configura archivos locales necesarios"""
        if not os.path.exists(self.LOCAL_LICENSES_FILE):
            with open(self.LOCAL_LICENSES_FILE, 'w') as f:
                json.dump({"pending": [], "activation_attempts": []}, f)
    
    def _save_local_license(self, license_data: Dict[str, Any]):
        """Guarda licencia pendiente localmente"""
        try:
            with open(self.LOCAL_LICENSES_FILE, 'r+') as f:
                data = json.load(f)
                data["pending"].append(license_data)
                f.seek(0)
                json.dump(data, f, indent=4, default=str)
        except Exception as e:
            logging.error(f"Error guardando licencia local: {str(e)}")
    
    def _sync_local_licenses(self):
        """Intenta sincronizar licencias locales con Firebase"""
        if not self.is_connected():
            return
        
        try:
            with open(self.LOCAL_LICENSES_FILE, 'r+') as f:
                data = json.load(f)
                
                # Sincronizar licencias pendientes
                for license_data in data["pending"]:
                    self.db.collection("licencias_pendientes").document(license_data["codigo"]).set(license_data)
                
                # Sincronizar intentos de activación
                for attempt in data["activation_attempts"]:
                    if self._process_activation(attempt["codigo"]):
                        data["activation_attempts"].remove(attempt)
                
                # Limpiar archivo local
                f.seek(0)
                f.truncate()
                json.dump({"pending": [], "activation_attempts": []}, f)
                
        except Exception as e:
            logging.error(f"Error sincronizando licencias locales: {str(e)}")
    
    def is_connected(self) -> bool:
        """Verifica conexión con Firebase"""
        return self.db is not None
    
    def guardar_licencia_pendiente(self, correo: str, codigo: str, codigo_activacion: str, duracion: int):
        license_data = {
            "correo": correo,
            "duracion": duracion,
            "codigo": codigo,  # UUID largo (para MercadoPago)
            "codigo_activacion": codigo_activacion,  # Código corto (para el usuario)
            "fecha_generacion": datetime.now().isoformat(),
            "activa": False
        }
        
        try:
            if self.is_connected():
                self.db.collection("licencias_pendientes").document(codigo).set(license_data)
                logging.info(f"Licencia {codigo} guardada en Firebase")
            else:
                self._save_local_license(license_data)
                logging.info(f"Licencia {codigo} guardada localmente")
                
            self._sync_local_licenses()
            
        except exceptions.FirebaseError as e:
            logging.error(f"Error de Firebase: {str(e)}")
            self._save_local_license(license_data)
        except Exception as e:
            logging.error(f"Error inesperado: {str(e)}")
    
    def _process_activation(self, codigo: str) -> bool:
        """Lógica central de activación de licencias"""
        try:
            licencia_ref = self.db.collection("licencias_pendientes").document(codigo)
            licencia = licencia_ref.get().to_dict()
            
            if not licencia or licencia["activa"]:
                return False
            
            fecha_expiracion = datetime.now() + timedelta(days=licencia["duracion"])
            licencia_activa = {
                "correo": licencia["correo"],
                "fecha_expiracion": fecha_expiracion.isoformat(),
                "activa": True,
                "fecha_activacion": datetime.now().isoformat()
            }
            
            # Usar run_transaction para manejar la transacción
            @firestore.transactional
            def update_license(transaction):
                transaction.set(
                    self.db.collection("licencias_activas").document(codigo),
                    licencia_activa
                )
                transaction.delete(licencia_ref)
            
            # Ejecutar la transacción
            transaction = self.db.transaction()
            update_license(transaction)
            
            logging.info(f"Licencia {codigo} activada exitosamente")
            return True
            
        except Exception as e:
            logging.error(f"Error activando licencia: {str(e)}")
            return False
    
    def activar_licencia(self, codigo: str) -> bool:
        try:
            if not self.is_connected():
                return False
                
            licencia_ref = self.db.collection("licencias_pendientes").document(codigo)
            licencia = licencia_ref.get().to_dict()
            
            if not licencia or licencia["activa"]:
                return False
            
            dias_a_agregar = licencia["duracion"]
            correo = licencia["correo"]
    
            # Buscar si el usuario ya tiene una suscripción activa
            licencias_ref = self.db.collection("licencias_activas").where("correo", "==", correo).where("activa", "==", True)
            docs = list(licencias_ref.stream())
    
            if docs:
                # Si ya tiene una suscripción activa, sumar los días
                licencia_actual = docs[0].to_dict()
                fecha_expiracion_actual = datetime.fromisoformat(licencia_actual["fecha_expiracion"])
    
                if fecha_expiracion_actual > datetime.now():
                    # Sumar los días a la fecha de expiración actual
                    nueva_fecha_expiracion = fecha_expiracion_actual + timedelta(days=dias_a_agregar)
                else:
                    # Si la suscripción ya venció, empezar desde hoy
                    nueva_fecha_expiracion = datetime.now() + timedelta(days=dias_a_agregar)
    
                licencia_actual["fecha_expiracion"] = nueva_fecha_expiracion.isoformat()
    
                @firestore.transactional
                def update_license(transaction):
                    transaction.update(docs[0].reference, {"fecha_expiracion": nueva_fecha_expiracion.isoformat()})
                    transaction.delete(licencia_ref)
    
                transaction = self.db.transaction()
                update_license(transaction)
    
            else:
                # Si no tiene una suscripción activa, crear una nueva
                fecha_expiracion = datetime.now() + timedelta(days=dias_a_agregar)
                licencia_activa = {
                    "correo": licencia["correo"],
                    "fecha_expiracion": fecha_expiracion.isoformat(),
                    "activa": True,
                    "fecha_activacion": datetime.now().isoformat()
                }
    
                @firestore.transactional
                def update_license(transaction):
                    transaction.set(
                        self.db.collection("licencias_activas").document(codigo),
                        licencia_activa
                    )
                    transaction.delete(licencia_ref)
    
                transaction = self.db.transaction()
                update_license(transaction)
    
            logging.info(f"✅ Licencia {codigo} activada correctamente.")
            return True
            
        except Exception as e:
            logging.error(f"❌ Error activando licencia: {str(e)}")
            return False
    
    def cleanup(self):
        if firebase_admin._apps:
            firebase_admin.delete_app(firebase_admin.get_app())
            self.db = None
            logging.info("🔌 Conexión Firebase cerrada")
