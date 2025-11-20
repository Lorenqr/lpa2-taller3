"""
Router para gestionar Favoritos.
Endpoints para CRUD de favoritos (relación usuario-canción).
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlmodel import Session, select

from musica_api.database import get_session
from musica_api.models import Favorito, Usuario, Cancion, RolUsuario
from musica_api.schemas import FavoritoCreate, FavoritoRead, FavoritoConDetalles
from musica_api.auth import obtener_usuario_actual

router = APIRouter()


# ENDPOINTS CRUD: FAVORITOS


@router.get(
    "/", response_model=List[FavoritoRead], summary="Listar todos los favoritos"
)
def listar_favoritos(
    session: Session = Depends(get_session),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
    skip: int = 0,
    limit: int = 100,
):
    """
    Obtiene una lista de favoritos.

    **Los usuarios regulares solo ven sus propios favoritos. Los administradores ven todos.**

    - **skip**: Número de registros a saltar (para paginación)
    - **limit**: Número máximo de registros a retornar
    """
    statement = select(Favorito).offset(skip).limit(limit)

    # Si es usuario regular, filtrar solo sus favoritos
    if usuario_actual.rol != RolUsuario.ADMINISTRADOR:
        statement = statement.where(Favorito.id_usuario == usuario_actual.id)

    favoritos = session.exec(statement).all()
    return favoritos


@router.post(
    "/",
    response_model=FavoritoRead,
    status_code=status.HTTP_201_CREATED,
    summary="Marcar una canción como favorita",
)
def crear_favorito(
    favorito: FavoritoCreate,
    session: Session = Depends(get_session),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    """
    Marca una canción como favorita para un usuario.

    **Los usuarios pueden marcar favoritos en su propia cuenta. Los administradores pueden marcar para cualquier usuario.**

    - **id_usuario**: ID del usuario
    - **id_cancion**: ID de la canción a marcar como favorita
    """
    # Verificar permisos: el usuario puede marcar sus propios favoritos o ser admin
    if (
        usuario_actual.rol != RolUsuario.ADMINISTRADOR
        and usuario_actual.id != favorito.id_usuario
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para marcar favoritos para otro usuario",
        )

    # Verificar que el usuario existe
    usuario = session.get(Usuario, favorito.id_usuario)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {favorito.id_usuario} no encontrado",
        )

    # Verificar que la canción existe
    cancion = session.get(Cancion, favorito.id_cancion)
    if not cancion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Canción con ID {favorito.id_cancion} no encontrada",
        )

    # Verificar si ya existe el favorito
    statement = select(Favorito).where(
        Favorito.id_usuario == favorito.id_usuario,
        Favorito.id_cancion == favorito.id_cancion,
    )
    favorito_existente = session.exec(statement).first()

    if favorito_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta canción ya está marcada como favorita para este usuario",
        )

    # Crear el favorito
    db_favorito = Favorito.model_validate(favorito)
    session.add(db_favorito)
    session.commit()
    session.refresh(db_favorito)
    return db_favorito


@router.get(
    "/{favorito_id}",
    response_model=FavoritoConDetalles,
    summary="Obtener un favorito por ID",
)
def obtener_favorito(
    favorito_id: int,
    session: Session = Depends(get_session),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    """
    Obtiene los datos de un favorito específico por su ID, incluyendo detalles del usuario y canción.

    **Los usuarios pueden ver sus propios favoritos. Los administradores pueden ver cualquier favorito.**

    - **favorito_id**: ID del favorito a buscar
    """
    favorito = session.get(Favorito, favorito_id)

    if not favorito:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Favorito con ID {favorito_id} no encontrado",
        )

    # Verificar permisos
    if (
        usuario_actual.rol != RolUsuario.ADMINISTRADOR
        and usuario_actual.id != favorito.id_usuario
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para ver este favorito",
        )

    return favorito


@router.delete(
    "/{favorito_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un favorito",
)
def eliminar_favorito(
    favorito_id: int,
    session: Session = Depends(get_session),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    """
    Elimina un favorito del sistema.

    **Los usuarios pueden eliminar sus propios favoritos. Los administradores pueden eliminar cualquier favorito.**

    - **favorito_id**: ID del favorito a eliminar
    """
    favorito = session.get(Favorito, favorito_id)

    if not favorito:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Favorito con ID {favorito_id} no encontrado",
        )

    # Verificar permisos
    if (
        usuario_actual.rol != RolUsuario.ADMINISTRADOR
        and usuario_actual.id != favorito.id_usuario
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para eliminar este favorito",
        )

    session.delete(favorito)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
