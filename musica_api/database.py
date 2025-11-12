"""
Configuración de la base de datos.
Maneja la conexión y sesiones de SQLModel.
"""

from sqlmodel import Session, SQLModel, create_engine
from musica_api.config import get_settings

# Obtener la configuración
settings = get_settings()

# Crear el engine de la base de datos
# connect_args solo se necesita para SQLite
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(
    settings.database_url,
    echo=settings.debug,  # Muestra las queries SQL en consola si debug=True
    connect_args=connect_args
)


def create_db_and_tables():
    """
    Crea todas las tablas definidas en los modelos.
    Se ejecuta al iniciar la aplicación.
    """
    SQLModel.metadata.create_all(engine)


def get_session():
    """
    Generador de sesiones de base de datos.
    Se usa como dependencia en FastAPI.
    
    Yields:
        Session: Sesión de base de datos
    """
    with Session(engine) as session:
        yield session
