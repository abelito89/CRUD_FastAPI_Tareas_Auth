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