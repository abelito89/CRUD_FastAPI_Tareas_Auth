from pydantic import BaseModel, Field, EmailStr, constr
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
    username:str = Field(..., description="Nombre de usuario")
    full_name:str = Field(..., description="Nombre y 2 apellidos del usuario")
    email:EmailStr = Field(..., description="Correo electrónico del usuario")
    disabled:bool = Field(..., description="Estado de habilitación del usuario")
    password: str = Field(..., min_length=8, description="Password del usuario")


class UserDB(BaseModel):
    id:str = Field(..., description="id que se hereda del documento de mongodb")
    username:str = Field(..., description="Nombre de usuario")
    full_name:str = Field(..., description="Nombre y 2 apellidos del usuario")
    email:EmailStr = Field(..., description="Correo electrónico del usuario")
    disabled:bool = Field(..., description="Estado de habilitación del usuario")
    password:str = Field(..., min_length=8, description="Password del usuario")


class Token(BaseModel):
    access_token: str = Field(description="Token de acceso único generado cuando un usuario inicia sesión correctamente en el sistema")
    token_type: str = Field(description="JWT")


class TokenData(BaseModel):
    username: Optional[str] = Field(description="Nombre de usuario asociado al token de acceso")


