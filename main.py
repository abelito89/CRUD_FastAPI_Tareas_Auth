from fastapi import FastAPI, HTTPException
from db.Models.modelos_tareas import Tarea, TareaId
from db.client import client
from db.Schemas.esquemas_tareas import tarea_to_dict

app = FastAPI()


@app.post("/insertar_tarea", response_model=TareaId, summary="Endpoint que sirve para crear nuevas tareas")
async def insertar_tarea(nueva_tarea:Tarea) -> TareaId:
    nueva_tarea_dict = dict(nueva_tarea)
    id = client.local.tareas.insert_one(nueva_tarea_dict).inserted_id
    tarea_mongo = tarea_to_dict(client.local.tareas.find_one({"_id":id}))
    return TareaId(**tarea_mongo)



@app.get("/")
def read_root():
    return {"Hello": "World"}