from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional
import re

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
    role: Optional[str] = Field("user", description="Rol del usuario, por defecto 'user'")
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        if not re.search(r'[A-Z]', v):
            raise ValueError('La contraseña debe contener al menos una letra mayúscula')
        if not re.search(r'[a-z]', v):
            raise ValueError('La contraseña debe contener al menos una letra minúscula')
        if not re.search(r'[0-9]', v):
            raise ValueError('La contraseña debe contener al menos un número')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('La contraseña debe contener al menos un carácter especial')
        return v
    
    @validator('role')
    def validate_role(cls, v):
        if v not in ('admin', 'user'):
            raise ValueError("El rol debe ser 'admin' o 'user'")
        return v


class UserDB(BaseModel):
    id:str = Field(..., description="id que se hereda del documento de mongodb")
    username:str = Field(..., description="Nombre de usuario")
    full_name:str = Field(..., description="Nombre y 2 apellidos del usuario")
    email:EmailStr = Field(..., description="Correo electrónico del usuario")
    disabled:bool = Field(..., description="Estado de habilitación del usuario")
    password:str = Field(..., min_length=8, description="Password del usuario")
    role: Optional[str] = Field("user", description="Rol del usuario, por defecto 'user'")

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        if not re.search(r'[A-Z]', v):
            raise ValueError('La contraseña debe contener al menos una letra mayúscula')
        if not re.search(r'[a-z]', v):
            raise ValueError('La contraseña debe contener al menos una letra minúscula')
        if not re.search(r'[0-9]', v):
            raise ValueError('La contraseña debe contener al menos un número')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('La contraseña debe contener al menos un carácter especial')
        return v
    
    @validator('role')
    def validate_role(cls, v):
        if v not in ('admin', 'user'):
            raise ValueError("El rol debe ser 'admin' o 'user'")
        return v


class Token(BaseModel):
    access_token: str = Field(description="Token de acceso único generado cuando un usuario inicia sesión correctamente en el sistema")
    token_type: str = Field(description="JWT")


class TokenData(BaseModel):
    username: Optional[str] = Field(description="Nombre de usuario asociado al token de acceso")


