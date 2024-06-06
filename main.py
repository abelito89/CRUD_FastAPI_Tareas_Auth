from fastapi import FastAPI, HTTPException, Depends, status
from db.Models.modelos_tareas import Tarea, TareaId, User, UserDB, Token, TokenData
from db.client import client
from db.Schemas.esquemas_tareas import tarea_to_dict, user_to_dict
from typing import List, Optional
from bson.objectid import ObjectId
from pymongo import ReturnDocument
from bson.errors import InvalidId
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from Autenticacion import get_user, verify_password, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, oauth2_scheme, SECRET_KEY, ALGORITHM
from datetime import datetime, timedelta
from jose import jwt, JWTError
import bcrypt

app = FastAPI()
oauth2 = OAuth2PasswordBearer(tokenUrl="login")



@app.post("/insertar_tarea", response_model=TareaId, status_code=201, summary="Endpoint que sirve para crear nuevas tareas")
async def insertar_tarea(nueva_tarea:Tarea) -> TareaId:
    nueva_tarea_dict = dict(nueva_tarea)
    id = client.local.tareas.insert_one(nueva_tarea_dict).inserted_id
    tarea_mongo = tarea_to_dict(client.local.tareas.find_one({"_id":id}))
    return TareaId(**tarea_mongo)


@app.get("/consultar_total_de_tareas", response_model=List[TareaId], summary="Endopoint que sirve para consultar todas las tareas creadas")
async def total_tareas() -> List[TareaId]:
    lista_total = []
    for doc in client.local.tareas.find():
        doc_dict = tarea_to_dict(doc)
        lista_total.append(TareaId(**doc_dict)) 
    return lista_total


@app.get("/tarea_dado_id/{id_buscar}", response_model=TareaId, summary="Endpoint que encuentra una tarea dado un id")
async def tarea_dado_id(id_buscar:str) -> TareaId:
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
    conteo_de_eliminados=client.local.tareas.delete_many({"titulo":titulo_eliminar}).deleted_count
    if conteo_de_eliminados != 0:    
        return {"Cantidad de tareas eliminadas":conteo_de_eliminados}
    else:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
#Creacion y autenticación de usuarios

@app.post("/insertar_user", response_model=UserDB, status_code=201, summary="Endpoint que sirve para crear nuevos usuarios")
async def insertar_user(nuevo_user:User) -> UserDB:
    hashed_password = bcrypt.hashpw(nuevo_user.password.encode('utf-8'), bcrypt.gensalt())
    nuevo_user_dict = dict(nuevo_user)
    nuevo_user_dict['password'] = hashed_password.decode('utf-8')
    id = client.local.users.insert_one(nuevo_user_dict).inserted_id
    user_mongo = user_to_dict(client.local.users.find_one({"_id":id}))
    return UserDB(**user_mongo)


@app.get("/consultar_total_users", response_model=List[UserDB], summary="Endpoint que me devuelve el total de usuarios en la base de datos")
async def consultar_total_users() -> List[UserDB]:
    lista_total = []
    for user in client.local.users.find():
        dict_user=user_to_dict(user)
        lista_total.append(UserDB(**dict_user))
    return lista_total


@app.get("/search_user/{username}", response_model=UserDB, status_code=200, summary="Endpoint que sirve para buscar un usuario específico" )
async def search_user(username:str) -> UserDB:
    if get_user(username):
        return get_user(username)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Usuario no encontrado",
    )
 #la funcion de buscar usuarios hay que traerla de un modulo extra

@app.post("/token", response_model=Token)
async def login_access_token(form_data:OAuth2PasswordRequestForm = Depends()):
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
