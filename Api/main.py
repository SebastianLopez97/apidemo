from fastapi import FastAPI
from sqlalchemy import MetaData, Table, Column, Integer, String, Float,DateTime
from databases import Database

# Conexión a la base de datos MySQL
DATABASE_URL = "mysql+asyncmy://remoto:password@127.0.0.1/demo"

database = Database(DATABASE_URL)
metadata = MetaData()

# Ejemplo de tabla
mezclas = Table(
    "Mezclas",
    metadata,
    Column("IdoP", String(50)),
    Column("FolioOp", Integer),
    Column("Mezcla", String(50)),
    Column("FechaInicio", DateTime), 
    Column("FechaTermino", DateTime), 
)

app = FastAPI()

# Evento para conectar a la base de datos al iniciar la aplicación
@app.on_event("startup")
async def startup():
    await database.connect()

# Evento para desconectar de la base de datos al cerrar la aplicación
@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/mezclas")
async def read_mezclas():
    query = mezclas.select()
    mezclas_result = await database.fetch_all(query) 
    if mezclas_result is None:
        return {"error": "mezclas not found"}
    result = [dict(mezcla) for mezcla in mezclas_result]
    return {"Mezclas": result}


@app.get("/mezclas/{mezcla}")
async def read_mezcla(mezcla: int):
    query = mezclas.select().where(mezclas.c.Mezcla == mezcla)
    mezcla_result = await database.fetch_one(query)
    if mezcla_result is None:
        return {"error": "mezcla not found"}
    return {"Mezcla": dict(mezcla_result)}


