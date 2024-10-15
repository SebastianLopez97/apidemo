from fastapi import FastAPI
from sqlalchemy import MetaData, Table, Column, Integer, String, Float,DateTime
from databases import Database
from pydantic import BaseModel

# Conexión a la base de datos MySQL
DATABASE_URL = "mysql+asyncmy://remoto:password@127.0.0.1/demo"

database = Database(DATABASE_URL)
metadata = MetaData()

usuarios = Table(
    "Users",
    metadata,
    Column("Id", Integer, primary_key=True),
    Column("User", String(50)),
    Column("Password", String(50))
)

mezclas = Table(
    "Mezclas",
    metadata,
    Column("IdoP", String(50)),
    Column("FolioOp", Integer),
    Column("Mezcla", String(50)),
    Column("FechaInicio", DateTime), 
    Column("FechaTermino", DateTime), 
    Column("TotalKg", Float),
)

consumos = Table(
    "Consumos",
    metadata,
    Column("IdOp", String(50)),
    Column("Mezcla", Integer),
    Column("Codigo", String(50)),
    Column("MateriaPrima", String(100)), 
    Column("Deseado", Float),
    Column("Dosificado", Float), 
)
ordenes = Table(
    "Ordenes",
    metadata,
    Column("IdoP", String(50)),
    Column("FolioOp", String(20)),
    Column("Mezclas", Integer),
    Column("MezclasRealizadas", Integer), 
    Column("Formula", String(50)), 
    Column("TotalKg", Float),
)

eficiencia = Table(
    "Eficiencia",
    metadata,
    Column("Fecha", DateTime),
    Column("Eficiencia", Float),
)


class UserAuth(BaseModel):
    User: str
    Password: str

app = FastAPI()

# Evento para conectar a la base de datos al iniciar la aplicación
@app.on_event("startup")
async def startup():
    await database.connect()

# Evento para desconectar de la base de datos al cerrar la aplicación
@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.post("/login")
async def login(user: UserAuth):
    query = usuarios.select().where(usuarios.c.User == user.User).where(usuarios.c.Password == user.Password)
    user_record = await database.fetch_one(query)
    
    if user_record is None:
        return {"validate": False , "message": "Invalid username or password"}
    
    return {"validate": True, "message": "Login successful"}

@app.get("/Ordenes")
async def read_ordenes():
    query = ordenes.select()
    ordenes_result = await database.fetch_all(query) 
    if ordenes_result is None:
        return {"error": "ordenes not found"}
    result = [dict(orden) for orden in ordenes_result]
    return {"Ordenes": result}

@app.get("/Mezclas/{idop}")
async def read_mezclas(idop):
    query = mezclas.select().where(mezclas.c.IdoP == idop)
    print(str(query))
    mezclas_result = await database.fetch_all(query)
    
    if not mezclas_result:  
        return {"error": "mezclas not found"}
    
    result = [dict(mezcla) for mezcla in mezclas_result]
    return {"Mezclas": result}


@app.get("/Mezclas/{idop}/{mezcla}")
async def read_consumos(idop,mezcla: int):
    query = consumos.select().where((consumos.c.IdOp == idop) & (consumos.c.Mezcla == mezcla) )
    print(query)
    consumos_r = await database.fetch_all(query)

    if not consumos_r:
        return {"error": "Consumos not found"}

    result = [dict(consumo) for consumo in consumos_r]
    return {"Consumos": result}



@app.get("/Eficiencia")
async def read_eficiencia():
    query = eficiencia.select().order_by(eficiencia.c.Fecha).limit(20)
    efi_result = await database.fetch_all(query) 
    if efi_result is None:
        return {"error": "eficiencia not found"}
    result = [dict(efi) for efi in efi_result]
    return {"Eficiencia": result}
