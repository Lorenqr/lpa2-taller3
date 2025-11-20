"""
Paquete principal de la aplicación API de Música.
Este módulo inicializa el paquete y expone los componentes principales.
"""

from musica_api.models import Usuario, Cancion, Favorito
from musica_api.database import create_db_and_tables, get_session, engine
from musica_api.config import settings, get_settings

__all__ = [
    "Usuario",
    "Cancion",
    "Favorito",
    "create_db_and_tables",
    "get_session",
    "engine",
    "settings",
    "get_settings",
]
