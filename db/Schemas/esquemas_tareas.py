def tarea_to_dict(tarea) -> dict:
    """
    Convierte una tarea de MongoDB a un diccionario Python.

    Parámetros:
    - `tarea`: La tarea en formato MongoDB.

    Retorna:
    - `dict`: Un diccionario con los datos de la tarea.
    """
    return {"id":str(tarea["_id"]), 
            "titulo":tarea["titulo"], 
            "descripcion":tarea["descripcion"], 
            "estado_inicial":tarea["estado_inicial"]}


def user_to_dict(user) -> dict:
    """
    Convierte un usuario de MongoDB a un diccionario Python.

    Parámetros:
    - `user`: El usuario en formato MongoDB.

    Retorna:
    - `dict`: Un diccionario con los datos del usuario.
    """
    return {"id":str(user["_id"]), 
            "username":user["username"], 
            "full_name":user["full_name"], 
            "email":user["full_name"], 
            "disabled":user["disabled"],
            "password":user["password"]}