from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from dotenv import load_dotenv
import os
from typing import Optional, Union
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
import bcrypt
from db.client import client
from db.Models.modelos_tareas import User, UserDB, TokenData
from db.Schemas.esquemas_tareas import user_to_dict
from fastapi import HTTPException, Security, status, Depends

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
    """
    Crea un token de acceso JWT.

    Parámetros:
    - `data`: Datos que se codificarán en el token.
    - `expires_delta`: Duración de validez del token (opcional).

    Retorna:
    - `str`: Token de acceso JWT.
    """
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
    """
    Verifica si una contraseña en texto plano coincide con una contraseña hasheada.

    Parámetros:
    - `plain_password`: Contraseña en texto plano.
    - `hashed_password`: Contraseña hasheada.

    Retorna:
    - `bool`: True si las contraseñas coinciden, False en caso contrario.
    """
    # Convierte la contraseña en texto plano a bytes, si no lo está ya
    if isinstance(plain_password, str):
        plain_password = plain_password.encode('utf-8')
    # Convierte la contraseña hasheada a bytes, si no lo está ya
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')
    
    # Usa bcrypt para verificar si la contraseña en texto plano corresponde a la hasheada
    return bcrypt.checkpw(plain_password, hashed_password)


def get_user(username:str) -> UserDB:
    """
    Obtiene un usuario por su nombre de usuario.

    Parámetros:
    - `username`: Nombre de usuario a buscar.

    Retorna:
    - `UserDB`: Datos del usuario encontrado o None si no se encuentra.
    """
    user_data = client.local.users.find_one({"username": username})
    if user_data:
        user_dict = user_to_dict(user_data)
        return UserDB(**user_dict)
    return None


def get_current_user(token: str = Depends(oauth2_scheme)) -> UserDB:
    """
    Obtiene el usuario actual autenticado.

    Parámetros:
    - `token`: El token de acceso del usuario.

    Retorna:
    - `UserDB`: Los datos del usuario autenticado.

    Lanza:
    - `HTTPException`: Si el token no es válido o el usuario no se encuentra.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  # Decodificar el token JWT
        username: str = payload.get("sub")  # Obtener el nombre de usuario del token
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception  # Lanzar excepción si hay un error con el token
    user = get_user(username=token_data.username)  # Obtener el usuario de la base de datos
    if user is None:
        raise credentials_exception  # Lanzar excepción si el usuario no se encuentra
    return user  # Retornar el usuario autenticado


# Función para verificar el rol del usuario
def verify_role(role: str):
    """
    Verifica si el usuario actual tiene el rol especificado.

    Parámetros:
    - `role`: El rol requerido para acceder al endpoint.

    Retorna:
    - `Callable`: Una función que verifica el rol del usuario actual.

    Lanza:
    - `HTTPException`: Si el usuario no tiene el rol requerido.
    """
    def role_verification(current_user: UserDB = Security(get_current_user)):
        """
        Verifica el rol del usuario actual.

        Parámetros:
        - `current_user`: El usuario actual obtenido a través de la seguridad de FastAPI.

        Retorna:
        - `UserDB`: El usuario actual si tiene el rol requerido.

        Lanza:
        - `HTTPException`: Si el usuario no tiene el rol requerido.
        """
        if current_user.role != role:
            # Si el rol del usuario no coincide con el rol requerido, se lanza una excepción HTTP 403
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permiso para realizar esta acción"
            )
        return current_user  # Retornar el usuario actual si tiene el rol requerido
    return role_verification  # Retornar la función de verificación de rol


first_user_created = False

# Función para verificar si hay usuarios en la base de datos
def check_first_user():
    global first_user_created
    if not first_user_created:
        user_count = client.local.users.count_documents({})
        if user_count == 0:
            first_user_created = True