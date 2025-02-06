# email_sender.py
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from dotenv import load_dotenv
import logging

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('email.log'), logging.StreamHandler()]
)

load_dotenv()

class EmailSender:
    def __init__(self):
        self.sg = None
        self._initialize_sendgrid()
        self.templates = {
            'codigo_licencia': {
                'subject': '🔑 Código de Licencia | Software de Ventas',
                'html': """
                <h2 style="color: #2e6c80;">¡Gracias por tu compra!</h2>
                <p>Tu código de licencia es:</p>
                <div style="background: #f0f0f0; padding: 15px; text-align: center; margin: 20px 0;">
                    <h1 style="margin: 0;">{codigo}</h1>
                </div>
                <p>Duración: {duracion_dias} días</p>
                <hr>
                <p><small>¿Problemas? Contáctanos: soporte@tudominio.com</small></p>
                """
            },
            'licencia_activada': {
                'subject': '✅ Licencia Activada | Software de Ventas',
                'html': """
                <h2 style="color: #2e6c80;">¡Tu licencia ha sido activada!</h2>
                <p>Ahora puedes disfrutar de todas las funcionalidades del sistema.</p>
                <p><strong>Código:</strong> <code>{codigo}</code></p>
                <p><strong>Duración:</strong> {duracion_dias} días</p>
                <hr>
                <p><small>¿Problemas? Contáctanos: soporte@tudominio.com</small></p>
                """
            }
        }

    def _initialize_sendgrid(self):
        """Inicializa el cliente de SendGrid"""
        api_key = os.getenv('SENDGRID_API_KEY')
        if api_key:
            try:
                self.sg = SendGridAPIClient(api_key)
                logging.info("SendGrid inicializado correctamente")
            except Exception as e:
                logging.error(f"Error inicializando SendGrid: {str(e)}")
                self.sg = None

    def send_email(self, template_name: str, context: dict) -> bool:
        """Envía un email usando una plantilla"""
        try:
            template = self.templates.get(template_name)
            if not template:
                raise ValueError(f"Plantilla '{template_name}' no encontrada")
            
            message = Mail(
                from_email=Email(os.getenv('EMAIL_USER')),
                to_emails=To(context['destinatario']),
                subject=template['subject'],
                html_content=Content("text/html", template['html'].format(**context))
            )
            
            response = self.sg.send(message)
            
            if response.status_code == 202:
                logging.info(f"Email enviado a {context['destinatario']}")
                return True
            else:
                logging.error(f"Error SendGrid: {response.status_code} - {response.body}")
                return False
                
        except Exception as e:
            logging.error(f"Error enviando email: {str(e)}")
            return False