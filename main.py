from fastapi import FastAPI, HTTPException, Depends, status, Query
from db.Models.modelos_tareas import Tarea, TareaId, User, UserDB, Token, TokenData
from db.client import client
from db.Schemas.esquemas_tareas import tarea_to_dict, user_to_dict
from typing import List, Optional
from bson.objectid import ObjectId
from pymongo import ReturnDocument
from bson.errors import InvalidId
from fastapi.security import OAuth2PasswordRequestForm
from Autenticacion import get_user, verify_password, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, oauth2_scheme, SECRET_KEY, ALGORITHM
from datetime import datetime, timedelta
from jose import jwt, JWTError
import bcrypt
from email_sender import send_email

app = FastAPI()


@app.post("/insertar_tarea", response_model=TareaId, status_code=201, summary="Endpoint que sirve para crear nuevas tareas")
async def insertar_tarea(nueva_tarea:Tarea) -> TareaId:
    """
    Crea una nueva tarea.

    Parámetros:
    - `nueva_tarea`: La nueva tarea a ser creada.

    Retorna:
    - `TareaId`: El ID de la tarea creada.
    """
    nueva_tarea_dict = dict(nueva_tarea)
    id = client.local.tareas.insert_one(nueva_tarea_dict).inserted_id
    tarea_mongo = tarea_to_dict(client.local.tareas.find_one({"_id":id}))
    return TareaId(**tarea_mongo)


@app.get("/consultar_total_de_tareas", response_model=List[TareaId], summary="Endpoint que sirve para consultar todas las tareas creadas")
async def total_tareas(skip: int = Query(0,description="Número de datos a omitir(skip)"), limit:int = Query(5, description="Cantidad de tareas a mostrar por cada página")) -> List[TareaId]:
    """
    Consulta todas las tareas creadas.
    Parámetros:
    - `skip`: Número de datos a omitir(skip).
    - `limit`: Cantidad de tareas a mostrar por cada página.

    Retorna:
    - Lista[TareaId]: Lista de todas las tareas creadas por páginas de hasta 5 tareas.
    """
    lista_total = []
    for doc in client.local.tareas.find().skip(skip).limit(limit):
        doc_dict = tarea_to_dict(doc)
        lista_total.append(TareaId(**doc_dict)) 
    return lista_total


@app.get("/tarea_dado_id/{id_buscar}", response_model=TareaId, summary="Endpoint que encuentra una tarea dado un id")
async def tarea_dado_id(id_buscar:str) -> TareaId:
    """
    Encuentra una tarea dado un ID.

    Parámetros:
    - `id_buscar`: El ID de la tarea a buscar.

    Retorna:
    - `TareaId`: La tarea encontrada.
    """
    try:
        ObjectId(id_buscar)
    except InvalidId:
        raise HTTPException(status_code=400, detail="ID no válido")
    tarea_encontrada = client.local.tareas.find_one({"_id":ObjectId(id_buscar)})
    if tarea_encontrada is None:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    dict_tarea_encontrada = tarea_to_dict(tarea_encontrada)
    return TareaId(**dict_tarea_encontrada)


@app.put("/modificar_tarea/{id_modificar}", response_model=TareaId, summary="Endpoint que sirve para modificar una tarea dado un id")
async def modificar_tarea(id_modificar:str, titulo_nuevo:str, estado_inicial_nuevo:str, descripcion_nueva:Optional[str]=None) -> TareaId:
    """
    Modifica una tarea dado un ID.

    Parámetros:
    - `id_modificar`: El ID de la tarea a modificar.
    - `titulo_nuevo`: El nuevo título de la tarea.
    - `estado_inicial_nuevo`: El nuevo estado inicial de la tarea.
    - `descripcion_nueva`: La nueva descripción de la tarea (opcional).

    Retorna:
    - `TareaId`: La tarea modificada.
    """
    try:
        ObjectId(id_modificar)
    except InvalidId:
        raise HTTPException(status_code=400, detail="ID no válido")
    instancia_nueva = Tarea( titulo=titulo_nuevo, estado_inicial=estado_inicial_nuevo, descripcion=descripcion_nueva)
    instancia_nueva_to_dict = instancia_nueva.dict()
    tarea_modificada = client.local.tareas.find_one_and_update({"_id":ObjectId(id_modificar)},
                                                               {"$set":instancia_nueva_to_dict},
                                                               return_document=ReturnDocument.AFTER)
    if tarea_modificada:
        tarea_modificada_dict = tarea_to_dict(tarea_modificada)
        return tarea_modificada_dict
    else:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")


@app.delete("/eliminar_tarea/{titulo_eliminar}", response_model=dict, summary="Endpoint para eliminar tarea segun el título")
async def eliminar_tarea(titulo_eliminar:str) -> dict:
    """
    Elimina una tarea según el título.

    Parámetros:
    - `titulo_eliminar`: El título de la tarea a eliminar.

    Retorna:
    - `dict`: Diccionario con la cantidad de tareas eliminadas.
    """  
    conteo_de_eliminados=client.local.tareas.delete_many({"titulo":titulo_eliminar}).deleted_count
    if conteo_de_eliminados != 0:    
        return {"Cantidad de tareas eliminadas":conteo_de_eliminados}
    else:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
#Creacion y autenticación de usuarios

@app.post("/insertar_user", response_model=UserDB, status_code=201, summary="Endpoint que sirve para crear nuevos usuarios")
async def insertar_user(nuevo_user:User) -> UserDB:
    """
    Crea un nuevo usuario.

    Parámetros:
    - `nuevo_user`: El nuevo usuario a ser creado.

    Retorna:
    - `UserDB`: El usuario creado.
    """
    email_existente = client.local.users.find_one({"email": nuevo_user.email})
    username_existente = client.local.users.find_one({"username": nuevo_user.username})
    if email_existente:
        raise HTTPException(status_code=409, detail="El correo electrónico ya está en uso")
    elif username_existente:
        raise HTTPException(status_code=409, detail="El nombre de usuario ya está en uso, por favor elija otro")    
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


@app.get("/consultar_total_users", response_model=List[UserDB], summary="Endpoint que me devuelve el total de usuarios en la base de datos")
async def consultar_total_users(skip:int = Query(0, description="Cantidad de usuarios a omitir"), limit:int = Query(3, description="Cantidad de usuarios que se muestra en cada página")) -> List[UserDB]:
    """
    Consulta el total de usuarios en la base de datos.
    Parámetros:
    - `skip`: Número de datos a omitir(skip).
    - `limit`: Cantidad de usuarios a mostrar por cada página.

    Retorna:
    - Lista[UserDB]: Lista de todos los usuarios en la base de datos.
    """
    lista_total = []
    for user in client.local.users.find().skip(skip).limit(limit):
        dict_user=user_to_dict(user)
        lista_total.append(UserDB(**dict_user))
    return lista_total


@app.get("/search_user/{username}", response_model=UserDB, status_code=200, summary="Endpoint que sirve para buscar un usuario específico" )
async def search_user(username:str) -> UserDB:
    """
    Busca un usuario específico.

    Parámetros:
    - `username`: El nombre de usuario a buscar.

    Retorna:
    - `UserDB`: El usuario encontrado.

    Raise:
    - `HTTPException`: Si el usuario no es encontrado.
    """
    if get_user(username):
        return get_user(username)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Usuario no encontrado",
    )
 #la funcion de buscar usuarios hay que traerla de un modulo extra

#@app.delete("/eliminar_usuario/{username}", response_model="")

@app.post("/token", response_model=Token)
async def login_access_token(form_data:OAuth2PasswordRequestForm = Depends()) -> Token:
    """
    Genera un token de acceso para un usuario.

    Parámetros:
    - `form_data`: Datos del formulario de solicitud de contraseña.

    Retorna:
    - `Token`: El token de acceso generado.
    """
    user_db = get_user(form_data.username)
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate":"Bearer"}
        )
    user_dict = user_db.dict()
    user = User(**user_dict)
    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos"
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub":user.username}, expires_delta=access_token_expires
    )
    return {"access_token":access_token, "token_type":"bearer"}


@app.get("/users/me")
async def read_users_me(token: str = Depends(oauth2_scheme)):
    """
    Lee los datos del usuario actualmente autenticado.

    Parámetros:
    - `token`: El token de acceso del usuario.

    Retorna:
    - `User`: Los datos del usuario autenticado.

    Raise:
    - `HTTPException`: Si las credenciales no son válidas.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate":"Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user