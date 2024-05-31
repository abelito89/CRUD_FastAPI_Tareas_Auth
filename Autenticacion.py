from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from dotenv import load_dotenv
import os
from typing import Optional
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt

#Configuracion de OAuth2
load_dotenv() #Cargar variables de entorno desde .env
#Llave secreta para firmar los tokens. Esta llave debe ser generada aleatoriamente por alguna
#app externa y se coloca en el .env
SECRET_KEY = os.getenv("SECRET_KEY")
#Algoritmo de encriptación
ALGORITHM = os.getenv("ALGORITHM")
#Tiempo de expiración del token
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

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
