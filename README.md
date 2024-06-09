# CRUD_FastAPI_Tareas_Auth

# README para Aplicación FastAPI

## Descripción del Proyecto

Esta es una aplicación de gestión de tareas desarrollada con FastAPI. La aplicación permite a los usuarios crear, consultar, modificar y eliminar tareas. Además, incluye autenticación de usuarios mediante OAuth2 y gestión de usuarios en una base de datos MongoDB. Incluye validación de validez de email y de contraseñas que sean de al menos 8 caracteres, con caracteres especiales, númereos, letras mayúsculas y letras minúsculas.

## Características

- **Crear tareas**: Permite a los usuarios crear nuevas tareas.
- **Consultar tareas**: Los usuarios pueden consultar todas las tareas existentes.
- **Buscar tarea por ID**: Permite encontrar una tarea específica dado su ID.
- **Modificar tareas**: Permite modificar una tarea existente.
- **Eliminar tareas**: Permite eliminar tareas por título.
- **Gestión de usuarios**: Creación y autenticación de usuarios. Validación de emails válidos y contraseñas que cumplan con los requerimientos.
- **Autenticación JWT**: Seguridad mediante tokens JWT para las operaciones de usuario.

## Requisitos

- Python 3.11.4
- MongoDB

## Instalación

1. Clona el repositorio:

   ```bash
   git clone https://github.com/abelito89/CRUD_FastAPI_Tareas_Auth.git
   ```

2. Crea y activa un entorno virtual:

   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows usa `venv\Scripts\activate`
   ```

3. Instala las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

4. Configura las variables de entorno:

   Crea un archivo `.env` en el directorio raíz del proyecto y añade las siguientes variables:

   ```env
   SECRET_KEY=tu_secreto
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

5. Inicia el servidor de desarrollo:

   ```bash
   uvicorn main:app --reload
   ```

## Uso

### Endpoints

#### Tareas

- **Crear una tarea**

  ```http
  POST /insertar_tarea
  ```

  Cuerpo de la solicitud (JSON):
  ```json
  {
    "titulo": "Titulo de la tarea",
    "descripcion": "Descripción de la tarea",
    "estado_inicial": "Pendiente"
  }
  ```

- **Consultar todas las tareas**

  ```http
  GET /consultar_total_de_tareas
  ```

- **Buscar tarea por ID**

  ```http
  GET /tarea_dado_id/{id_buscar}
  ```

- **Modificar una tarea**

  ```http
  PUT /modificar_tarea/{id_modificar}
  ```

  Cuerpo de la solicitud (JSON):
  ```json
  {
    "titulo_nuevo": "Nuevo título",
    "estado_inicial_nuevo": "En proceso",
    "descripcion_nueva": "Nueva descripción"
  }
  ```

- **Eliminar una tarea**

  ```http
  DELETE /eliminar_tarea/{titulo_eliminar}
  ```

#### Usuarios

- **Crear un usuario**

  ```http
  POST /insertar_user
  ```

  Cuerpo de la solicitud (JSON):
  ```json
  {
    "username": "usuario",
    "full_name": "Nombre Completo",
    "email": "correo@dominio.com",
    "disabled": false,
    "password": "contraseña"
  }
  ```

- **Consultar todos los usuarios**

  ```http
  GET /consultar_total_users
  ```

- **Buscar un usuario por nombre de usuario**

  ```http
  GET /search_user/{username}
  ```

- **Obtener token de acceso**

  ```http
  POST /token
  ```

  Formulario de solicitud:
  - `username`: Nombre de usuario.
  - `password`: Contraseña.

- **Leer datos del usuario autenticado**

  ```http
  GET /users/me
  ```

## Estructura del Proyecto

- `main.py`: Archivo principal con las rutas y lógica de la aplicación.
- `Autenticacion.py`: Contiene la lógica de autenticación y creación de tokens.
- `db/client.py`: Configuración del cliente de MongoDB.
- `db/Schemas/esquemas_tareas.py`: Esquemas para convertir datos de MongoDB a diccionarios Python.
- `db/Models/modelos_tareas.py`: Modelos de datos para Pydantic.
- `requirements.txt`: Lista de dependencias del proyecto.