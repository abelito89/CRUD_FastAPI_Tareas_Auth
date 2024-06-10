import smtplib
import email.utils
'''
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
'''
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

msg = EmailMessage()

context = ssl.create_default_context()

def send_email(to_email):
    # Configurar el mensaje de correo
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_USER
    msg['Subject'] = 'Correo de confirmación de creación de usuario nuevo'
    msg.set_content('Se ha creado el usuario satisfactoriamente')  
    # Establecer conexión con el servidor SMTP y enviar correo
    with smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT, context=context) as server:
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.sendmail(EMAIL_FROM, to_email, msg.as_string())

