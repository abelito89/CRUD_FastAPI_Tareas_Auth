import smtplib
import email.utils
from email.message import EmailMessage
from dotenv import load_dotenv
import os
import ssl

load_dotenv()

# Configuración del servidor de correo electrónico
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 465
EMAIL_USER = os.getenv('EMAIL_USER') #el que recibe el correo
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
EMAIL_FROM = os.getenv('EMAIL_FROM') #desde donde se envía el correo

context = ssl.create_default_context()

def send_email(to_email, subject, body):
    """
    Envía un correo de confirmación al usuario recién creado.

    Parámetros:
    - `to_email`: La dirección de correo electrónico del destinatario.
    - `username`: El nombre del usuario que se acaba de crear.

    """
    # Configurar el mensaje de correo
    msg = EmailMessage()
    msg['From'] = EMAIL_FROM
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.set_content(body)
    # Establecer conexión con el servidor SMTP y enviar correo
    with smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT, context=context) as server:
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.sendmail(EMAIL_FROM, to_email, msg.as_string())