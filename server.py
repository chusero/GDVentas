# server.py
from flask import Flask, request, jsonify
from firebase_db import FirebaseManager
from mercado_pago import PaymentGateway
import logging
import os
from dotenv import load_dotenv

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('server.log'), logging.StreamHandler()]
)

# Cargar variables de entorno
load_dotenv()

# Inicializar Firebase y MercadoPago
firebase = FirebaseManager()
payment_gateway = PaymentGateway(firebase)

# Crear aplicación Flask
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    try:
        # Obtener datos del webhook
        event_data = request.json
        logging.info(f"Webhook recibido: {event_data}")

        # Procesar el evento de pago
        if payment_gateway.process_webhook_event(event_data):
            return jsonify({"status": "success"}), 200
        else:
            return jsonify({"status": "error", "message": "Error procesando webhook"}), 400

    except Exception as e:
        logging.error(f"Error en webhook: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)