def tarea_to_dict(tarea) -> dict:
    return {"id":str(tarea["_id"]), "titulo":tarea["titulo"], "descripcion":tarea["descripcion"], "estado_inicial":tarea["estado_inicial"]}