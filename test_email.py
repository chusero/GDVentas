from email_sender import enviar_codigo_licencia

if __name__ == "__main__":
    if enviar_codigo_licencia("destinatario@ejemplo.com", "TEST123", 30):
        print("Correo enviado exitosamente!")
    else:
        print("Falló el envío del correo.")