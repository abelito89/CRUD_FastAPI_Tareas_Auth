from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from dotenv import load_dotenv
import os
from typing import Optional, Union
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
import bcrypt
from db.client import client
from db.Models.modelos_tareas import User, UserDB
from db.Schemas.esquemas_tareas import user_to_dict

#Configuracion de OAuth2
load_dotenv() #Cargar variables de entorno desde .env
#Llave secreta para firmar los tokens. Esta llave debe ser generada aleatoriamente por alguna
#app externa y se coloca en el .env
SECRET_KEY = os.getenv("SECRET_KEY")
#Algoritmo de encriptación
ALGORITHM = os.getenv("ALGORITHM")
#Tiempo de expiración del token
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

#Dependencia que indica dónde se enviarán las credenciales para obtener el token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

#Crear funciones auxiliares
#Crear un token de acceso
def create_access_token(data:dict, expires_delta: Optional[timedelta] = None):
    #expires_delta define la duración de la validez de un token de acceso (JWT). 
    #Es un objeto del tipo timedelta que representa la cantidad de tiempo que el token será válido desde el momento en que se emite
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp":expire}) #Se añade una nueva clave exp al diccionario to_encode con el valor de la fecha de expiración calculada
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Función para verificar la contraseña. Se intenta no comparar contraseñas en texto plano por seguridad
def verify_password(plain_password: Union[str,bytes], hashed_password: Union[str,bytes]) -> bool:
    # Convierte la contraseña en texto plano a bytes, si no lo está ya
    if isinstance(plain_password, str):
        plain_password = plain_password.encode('utf-8')
    # Convierte la contraseña hasheada a bytes, si no lo está ya
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')
    
    # Usa bcrypt para verificar si la contraseña en texto plano corresponde a la hasheada
    return bcrypt.checkpw(plain_password, hashed_password)


def get_user(username:str) -> UserDB:
    user_data = client.local.users.find_one({"username": username})
    if user_data:
        user_dict = user_to_dict(user_data)
        return UserDB(**user_dict)
    return None


