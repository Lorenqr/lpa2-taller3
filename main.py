from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from musica_api.database import create_db_and_tables
from musica_api.routers import usuarios, canciones, favoritos
from musica_api.config import settings


# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('musica_api.log')
    ]
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestor de ciclo de vida de la aplicación.
    Se ejecuta al iniciar y al cerrar la aplicación.
    """
    # Startup: Crear tablas en la base de datos
    logger.info("Iniciando aplicación API de Música...")
    create_db_and_tables()
    logger.info("Base de datos inicializada correctamente")
    yield
    
    # Shutdown: Limpiar recursos si es necesario
    logger.info("Cerrando aplicación...")
    print("cerrando aplicación...")


# Crear la instancia de FastAPI con metadatos apropiados
app = FastAPI(
    title=settings.app_name,
    description="API RESTful para gestionar usuarios, canciones y favoritos. Desarrollada con FastAPI, SQLModel y Pydantic.",
    version=settings.app_version,
    lifespan=lifespan,
    contact={
        "name": "Equipo de Desarrollo",
        "email": "contacto@musicapi.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)


# Configurar CORS para permitir solicitudes desde diferentes orígenes
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Incluir los routers de la aplicación
app.include_router(usuarios.router, prefix="/api/usuarios", tags=["Usuarios"])
app.include_router(canciones.router, prefix="/api/canciones", tags=["Canciones"])
app.include_router(favoritos.router, prefix="/api/favoritos", tags=["Favoritos"])


# Crear un endpoint raíz que retorne información básica de la API
@app.get("/", tags=["Root"])
async def root():
    """
    Endpoint raíz de la API.
    Retorna información básica y enlaces a la documentación.
    """
    logger.info("Acceso al endpoint raíz")
    return {
        "nombre": settings.app_name,
        "version": settings.app_version,
        "descripcion": "API RESTful para gestionar usuarios, canciones y favoritos",
        "documentacion": {
            "swagger": "/docs",
            "redoc": "/redoc"
        },
        "endpoints": {
            "usuarios": "/api/usuarios",
            "canciones": "/api/canciones",
            "favoritos": "/api/favoritos"
        }
    }


# Crear un endpoint de health check para monitoreo
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint para verificar el estado de la API.
    Útil para sistemas de monitoreo y orquestación.
    """
    from musica_api.database import engine
    
    # Verificar conexión a base de datos
    try:
        with engine.connect() as conn:
            db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "database": db_status,
        "environment": settings.environment,
    }


# TODO: Opcional - Agregar middleware para logging de requests



# TODO: Opcional - Agregar manejadores de errores personalizados


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )
