from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import queries, data

app = FastAPI(
    title="QueryBit API",
    description=(
        "Compilador QueryBit expuesto como API REST.\n\n"
        "**Flujo típico:**\n"
        "1. `POST /data/upload-csv` — sube tu CSV.\n"
        "2. `POST /queries/run` — manda tus queries como lista de strings, o\n"
        "3. `POST /queries/run-from-file` — sube un `.txt` con una query por línea.\n\n"
        "Cada query pasa por: **léxico → sintáctico → semántico → ejecución**. "
        "Si una falla, el resto del batch continúa."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # cambiar a la URL del frontend en producción
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(queries.router)
app.include_router(data.router)


@app.get("/", tags=["Root"])
def root():
    return {"message": "QueryBit API online. Visita /docs para Swagger UI."}