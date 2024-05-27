def tarea_to_dict(tarea) -> dict:
    return {"id":str(tarea["_id"]), 
            "titulo":tarea["titulo"], 
            "descripcion":tarea["descripcion"], 
            "estado_inicial":tarea["estado_inicial"]}


def user_to_dict(user) -> dict:
    return {"id":str(user["_id"]), 
            "username":user["username"], 
            "full_name":user["full_name"], 
            "email":user["full_name"], 
            "disabled":user["disabled"],
            "password":user["password"]}