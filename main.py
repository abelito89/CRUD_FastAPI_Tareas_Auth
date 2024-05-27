from fastapi import FastAPI, HTTPException
from db.Models.modelos_tareas import Tarea, TareaId
from db.client import client
from db.Schemas.esquemas_tareas import tarea_to_dict
from typing import List
from bson import ObjectId

app = FastAPI()


@app.post("/insertar_tarea", response_model=TareaId, summary="Endpoint que sirve para crear nuevas tareas")
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


@app.get("/tarea_dado_id/{id_buscar}", response_model=TareaId)
async def tarea_dado_id(id_buscar:str) -> TareaId:
    tarea_encontrada = tarea_to_dict(client.local.tareas.find_one({"_id":ObjectId(id_buscar)}))
    return TareaId(**tarea_encontrada)


