from fastapi import FastAPI, HTTPException
from db.Models.modelos_tareas import Tarea, TareaId
from db.client import client
from db.Schemas.esquemas_tareas import tarea_to_dict
from typing import List, Optional
from bson import ObjectId
from pymongo import ReturnDocument

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


@app.get("/tarea_dado_id/{id_buscar}", response_model=TareaId, summary="Endpoint que encuentra una tarea dado un id")
async def tarea_dado_id(id_buscar:str) -> TareaId:
    tarea_encontrada = tarea_to_dict(client.local.tareas.find_one({"_id":ObjectId(id_buscar)}))
    return TareaId(**tarea_encontrada)


@app.put("/modificar_tarea/{id_modificar}", response_model=TareaId, summary="Endpoint que sirve para modificar una tarea dado un id")
async def modificar_tarea(id_modificar:str, titulo_nuevo:str, estado_inicial_nuevo:str, descripcion_nueva:Optional[str]=None) -> TareaId:
    instancia_nueva = Tarea( titulo=titulo_nuevo, estado_inicial=estado_inicial_nuevo, descripcion=descripcion_nueva)
    instancia_nueva_to_dict = instancia_nueva.dict()
    tarea_modificada = client.local.tareas.find_one_and_update({"_id":ObjectId(id_modificar)},
                                                               {"$set":instancia_nueva_to_dict},
                                                               return_document=ReturnDocument.AFTER)
    tarea_modificada_dict = tarea_to_dict(tarea_modificada)
    return tarea_modificada_dict


@app.delete("/eliminar_tarea/{titulo_eliminar}", response_model=dict, summary="Endpoint para eliminar tarea segun el título")
async def eliminar_tarea(titulo_eliminar:str) -> dict:    
    conteo_de_eliminados=client.local.tareas.delete_many({"titulo":titulo_eliminar}).deleted_count
    return {"Cantidad de tareas eliminadas":conteo_de_eliminados}


