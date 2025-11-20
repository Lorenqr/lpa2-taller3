"""
Esquemas de validación usando Pydantic.
Define los esquemas para request y response de la API.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


# ESQUEMAS: AUTENTICACIÓN


class Token(BaseModel):
    """Esquema de respuesta para el token JWT."""

    access_token: str
    token_type: str = "bearer"
    rol: str


class TokenData(BaseModel):
    """Datos contenidos en el token JWT."""

    correo: Optional[str] = None
    rol: Optional[str] = None


class LoginRequest(BaseModel):
    """Esquema para la solicitud de login."""

    correo: EmailStr = Field(description="Correo electrónico del usuario")
    contraseña: str = Field(min_length=6, description="Contraseña del usuario")


# ESQUEMAS: USUARIO


class UsuarioBase(BaseModel):
    """Esquema base para Usuario."""

    nombre: str = Field(min_length=2, max_length=100, description="Nombre del usuario")
    correo: EmailStr = Field(description="Correo electrónico único del usuario")


class UsuarioCreate(UsuarioBase):
    """Esquema para crear un Usuario."""

    contraseña: str = Field(min_length=6, description="Contraseña del usuario")
    rol: Optional[str] = Field(
        default="usuario", description="Rol del usuario (usuario o administrador)"
    )


class UsuarioRegister(BaseModel):
    """Esquema para registro público de usuarios (siempre rol usuario)."""

    nombre: str = Field(min_length=2, max_length=100, description="Nombre del usuario")
    correo: EmailStr = Field(description="Correo electrónico único del usuario")
    contraseña: str = Field(min_length=6, description="Contraseña del usuario")


class UsuarioUpdate(BaseModel):
    """Esquema para actualizar un Usuario (todos los campos opcionales)."""

    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    correo: Optional[EmailStr] = None
    contraseña: Optional[str] = Field(
        None, min_length=6, description="Nueva contraseña (opcional)"
    )


class UsuarioRead(UsuarioBase):
    """Esquema para leer un Usuario (response)."""

    id: int
    rol: str
    activo: bool
    fecha_registro: datetime

    model_config = {"from_attributes": True}


# ESQUEMAS: CANCIÓN


class CancionBase(BaseModel):
    """Esquema base para Canción."""

    titulo: str = Field(
        min_length=1, max_length=200, description="Título de la canción"
    )
    artista: str = Field(max_length=200, description="Artista o intérprete")
    album: Optional[str] = Field(None, max_length=200, description="Álbum")
    duracion: int = Field(gt=0, description="Duración en segundos")
    año: Optional[int] = Field(None, ge=1900, le=2100, description="Año de lanzamiento")
    genero: Optional[str] = Field(None, max_length=100, description="Género musical")

    @field_validator("duracion")
    @classmethod
    def validar_duracion(cls, v: int) -> int:
        """Valida que la duración esté en un rango razonable."""
        if v <= 0:
            raise ValueError("La duración debe ser mayor a 0 segundos")
        if v > 7200:  # 2 horas
            raise ValueError("La duración no puede ser mayor a 2 horas (7200 segundos)")
        return v

    @field_validator("año")
    @classmethod
    def validar_año(cls, v: Optional[int]) -> Optional[int]:
        """Valida que el año sea razonable."""
        if v is not None:
            current_year = datetime.now().year
            if v > current_year + 1:
                raise ValueError(f"El año no puede ser mayor a {current_year + 1}")
        return v


class CancionCreate(CancionBase):
    """Esquema para crear una Canción."""

    pass


class CancionUpdate(BaseModel):
    """Esquema para actualizar una Canción (todos los campos opcionales)."""

    titulo: Optional[str] = Field(None, min_length=1, max_length=200)
    artista: Optional[str] = Field(None, max_length=200)
    album: Optional[str] = Field(None, max_length=200)
    duracion: Optional[int] = Field(None, gt=0)
    año: Optional[int] = Field(None, ge=1900, le=2100)
    genero: Optional[str] = Field(None, max_length=100)


class CancionRead(CancionBase):
    """Esquema para leer una Canción (response)."""

    id: int
    fecha_creacion: datetime

    model_config = {"from_attributes": True}


# ESQUEMAS: FAVORITO


class FavoritoBase(BaseModel):
    """Esquema base para Favorito."""

    id_usuario: int = Field(gt=0, description="ID del usuario")
    id_cancion: int = Field(gt=0, description="ID de la canción")


class FavoritoCreate(FavoritoBase):
    """Esquema para crear un Favorito."""

    pass


class FavoritoRead(FavoritoBase):
    """Esquema para leer un Favorito (response)."""

    id: int
    fecha_marcado: datetime

    model_config = {"from_attributes": True}


class FavoritoConDetalles(BaseModel):
    """Esquema para Favorito con detalles de usuario y canción."""

    id: int
    fecha_marcado: datetime
    usuario: UsuarioRead
    cancion: CancionRead

    model_config = {"from_attributes": True}
