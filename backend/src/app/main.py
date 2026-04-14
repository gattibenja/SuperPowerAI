from contextlib import asynccontextmanager
from fastapi import FastAPI
from pydantic_ai.ag_ui import AGUIApp
import logfire
from app.agents import cecilia_cura
from app.db.db import create_db_and_tables
from app.api.routes.chatRoutes import router as paciente_router
import app.db.dBmodels  # importar para que SQLModel registre los modelos

logfire.configure()

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(paciente_router, prefix="/api")

#mount para montar una subaplicacion dentro de la app para no tener que crear un backend diferente y que no se tengan autentificar ni nada
app.mount("/doctorAgent", AGUIApp(cecilia_cura), name="agui")
 

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)