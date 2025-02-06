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
        """Inicialización segura de Firebase con manejo de errores"""
        try:
            cred_path = os.getenv("FIREBASE_CREDENTIALS")
            if not cred_path or not os.path.exists(cred_path):
                raise FileNotFoundError("Credenciales de Firebase no válidas")
            
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            self.db = firestore.client()
            logging.info("Conexión a Firebase establecida exitosamente")
            
        except Exception as e:
            logging.error(f"Error inicializando Firebase: {str(e)}")
            self.db = None
    
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
    
    def guardar_licencia_pendiente(self, correo: str, codigo: str, duracion: int):
        """Guarda una licencia pendiente con manejo offline"""
        license_data = {
            "correo": correo,
            "duracion": duracion,
            "codigo": codigo,
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
            
            # Transaction para asegurar consistencia
            @firestore.transactional
            def update_license(transaction):
                transaction.set(
                    self.db.collection("licencias_activas").document(codigo),
                    licencia_activa
                )
                transaction.delete(licencia_ref)
            
            transaction = firestore.transaction()
            update_license(transaction)
            
            logging.info(f"Licencia {codigo} activada exitosamente")
            return True
            
        except Exception as e:
            logging.error(f"Error activando licencia: {str(e)}")
            return False
    
    def activar_licencia(self, codigo: str) -> bool:
        """Intenta activar una licencia con manejo offline"""
        try:
            if self.is_connected():
                result = self._process_activation(codigo)
                if result:
                    return True
                
            # Si falla o está offline, guardar intento local
            with open(self.LOCAL_LICENSES_FILE, 'r+') as f:
                data = json.load(f)
                data["activation_attempts"].append({
                    "codigo": codigo,
                    "timestamp": datetime.now().isoformat()
                })
                f.seek(0)
                json.dump(data, f, indent=4)
            
            return False
            
        except Exception as e:
            logging.error(f"Error en activación: {str(e)}")
            return False
    
    def cleanup(self):
        """Limpieza de recursos"""
        if self.is_connected():
            firebase_admin.delete_app(firebase_admin.get_app())
            self.db = None
            logging.info("Conexión Firebase cerrada")