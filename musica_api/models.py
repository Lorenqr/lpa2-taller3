"""
Modelos de datos para la API de Música.
Define las tablas de la base de datos usando SQLModel.
"""

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, Relationship
from enum import Enum


class RolUsuario(str, Enum):
    """Roles disponibles en el sistema."""

    ADMINISTRADOR = "administrador"
    USUARIO = "usuario"


# MODELO: USUARIO


class Usuario(SQLModel, table=True):
    """
    Modelo de Usuario.
    Representa un usuario registrado en el sistema.
    """

    __tablename__ = "usuarios"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(index=True, min_length=2, max_length=100)
    correo: str = Field(unique=True, index=True, max_length=255)
    contraseña_hash: str = Field(description="Contraseña hasheada del usuario")
    rol: str = Field(default=RolUsuario.USUARIO, description="Rol del usuario")
    activo: bool = Field(default=True, description="Estado del usuario")
    fecha_registro: datetime = Field(default_factory=datetime.now)

    # Relación con Favoritos
    favoritos: list["Favorito"] = Relationship(back_populates="usuario")

    class Config:
        json_schema_extra = {
            "example": {
                "nombre": "Juan Pérez",
                "correo": "juan.perez@example.com",
                "rol": "usuario",
            }
        }


# MODELO: CANCIÓN


class Cancion(SQLModel, table=True):
    """
    Modelo de Canción.
    Representa una canción en el catálogo musical.
    """

    __tablename__ = "canciones"

    id: Optional[int] = Field(default=None, primary_key=True)
    titulo: str = Field(index=True, min_length=1, max_length=200)
    artista: str = Field(index=True, max_length=200)
    album: Optional[str] = Field(default=None, max_length=200)
    duracion: int = Field(gt=0, description="Duración en segundos")
    año: Optional[int] = Field(default=None, ge=1900, le=2100)
    genero: Optional[str] = Field(default=None, index=True, max_length=100)
    fecha_creacion: datetime = Field(default_factory=datetime.now)

    # Relación con Favoritos
    favoritos: list["Favorito"] = Relationship(back_populates="cancion")

    class Config:
        json_schema_extra = {
            "example": {
                "titulo": "Bohemian Rhapsody",
                "artista": "Queen",
                "album": "A Night at the Opera",
                "duracion": 354,
                "año": 1975,
                "genero": "Rock",
            }
        }


# MODELO: FAVORITO


class Favorito(SQLModel, table=True):
    """
    Modelo de Favorito.
    Representa la relación entre un usuario y una canción favorita.
    """

    __tablename__ = "favoritos"

    id: Optional[int] = Field(default=None, primary_key=True)
    id_usuario: int = Field(foreign_key="usuarios.id", index=True)
    id_cancion: int = Field(foreign_key="canciones.id", index=True)
    fecha_marcado: datetime = Field(default_factory=datetime.now)

    # Relaciones
    usuario: Usuario = Relationship(back_populates="favoritos")
    cancion: Cancion = Relationship(back_populates="favoritos")

    class Config:
        json_schema_extra = {"example": {"id_usuario": 1, "id_cancion": 1}}
