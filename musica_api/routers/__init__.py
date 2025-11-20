"""
Inicialización de routers.
Exporta todos los routers de la aplicación.
"""

from musica_api.routers import usuarios, canciones, favoritos

__all__ = ["usuarios", "canciones", "favoritos"]
