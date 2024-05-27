from pydantic import BaseModel, Field
from typing import Optional

class Tarea(BaseModel):
    titulo:str = Field(description="Título de la tarea programada")
    descripcion:Optional[str] = None
    estado_inicial:str = Field(description="Los estados pueden ser Pendiente, En proceso o Completada")


class TareaId(BaseModel):
    id:str = Field(description="id que se hereda del documento de mongodb")
    titulo:str = Field(description="Título de la tarea programada")
    descripcion:Optional[str] = None
    estado_inicial:str = Field(description="Los estados pueden ser Pendiente, En proceso o Completada")


class User(BaseModel):
    username:str = Field(description="Nombre de usuario")
    full_name:str = Field(description="Nombre y 2 apellidos del usuario")
    email:str = Field(description="Correo electrónico del usuario")
    disabled:bool = Field(description="Estado de habilitación del usuario")
    password:str = Field(description="Password del usuario")


class UserDB(BaseModel):
    id:str = Field(description="id que se hereda del documento de mongodb")
    username:str = Field(description="Nombre de usuario")
    full_name:str = Field(description="Nombre y 2 apellidos del usuario")
    email:str = Field(description="Correo electrónico del usuario")
    disabled:bool = Field(description="Estado de habilitación del usuario")
    password:str = Field(description="Password del usuario")
