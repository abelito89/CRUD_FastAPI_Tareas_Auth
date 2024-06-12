from db.client import client
from db.Models.modelos_tareas import UserDB, User
import bcrypt
from db.Schemas.esquemas_tareas import user_to_dict
from email_sender import send_email
from dotenv import load_dotenv
import os

load_dotenv()


def create_first_user_admin():
    """
    Crea el primer usuario administrador en la base de datos si no existe ningún usuario.

    Retorna:
    - `UserDB` o None: Los datos del usuario administrador creado si se creó correctamente, 
      o None si ya existía un usuario en la base de datos.
    """
    if client.local.users.count_documents({}) == 0:
        nuevo_user = User(
            username="administrator", 
            full_name="Administrador", 
            email="abelito.prueba@gmail.com", 
            disabled=False, 
            password=os.getenv("USER_ADMIN_DEFAULT_PASSWORD"),
            role='admin'
        )
        hashed_password = bcrypt.hashpw(nuevo_user.password.encode('utf-8'), bcrypt.gensalt())
        nuevo_user_dict = dict(nuevo_user)
        nuevo_user_dict['password'] = hashed_password.decode('utf-8')
        id = client.local.users.insert_one(nuevo_user_dict).inserted_id
        user_mongo = user_to_dict(client.local.users.find_one({"_id":id}))
        to_email = user_mongo['email']
        subject = 'Correo de confirmación de creación de usuario nuevo'
        body = f'Se ha creado el usuario {user_mongo["username"]} satisfactoriamente'
        send_email(to_email, subject, body)
        return UserDB(**user_mongo)