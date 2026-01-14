from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import close_mongo_connection, connect_to_mongo
from app.routers import events


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestión del ciclo de vida de la aplicación.
    Se ejecuta al iniciar y al cerrar la aplicación.
    """
    # Startup: Conectar a MongoDB
    await connect_to_mongo()
    print(f"🚀 API iniciada: http://{settings.api_host}:{settings.api_port}")
    print(f"📚 Documentación: http://{settings.api_host}:{settings.api_port}/docs")

    yield

    # Shutdown: Cerrar conexión a MongoDB
    await close_mongo_connection()
    print("👋 API detenida")


# Crear aplicación FastAPI
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="""
    API RESTful para la gestión de eventos tecnológicos.

    ## Características principales:
    * ✅ CRUD completo de eventos
    * 🔍 Filtrado por fechas y tags
    * 📄 Paginación de resultados
    * ✉️ Validación de emails
    * 🔒 Soft delete de eventos
    * 📝 Timestamps automáticos

    ## Endpoints disponibles:
    * **POST /api/v1/events** - Crear evento
    * **GET /api/v1/events** - Listar eventos (con filtros)
    * **GET /api/v1/events/{id}** - Obtener evento por ID
    * **PUT /api/v1/events/{id}** - Actualizar evento
    * **DELETE /api/v1/events/{id}** - Eliminar evento
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(events.router)


@app.get("/", tags=["Health"])
async def root():
    """
    Endpoint raíz - Información básica de la API.
    """
    return {
        "message": "Tech Events API",
        "version": settings.api_version,
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint para verificar que la API está funcionando.
    """
    return {"status": "healthy", "database": "connected"}


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Manejador global de excepciones para errores no capturados.
    Retorna mensajes de error elegantes.
    """
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Ocurrió un error interno en el servidor. Por favor, inténtelo más tarde.",
            "type": "internal_server_error",
        },
    )
