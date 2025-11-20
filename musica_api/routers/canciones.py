"""
Router para gestionar Canciones.
Endpoints para CRUD de canciones y búsqueda.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, Response
from sqlmodel import Session, select, col

from musica_api.database import get_session
from musica_api.models import Cancion, Usuario
from musica_api.schemas import CancionCreate, CancionRead, CancionUpdate
from musica_api.auth import obtener_usuario_actual

router = APIRouter()


# ENDPOINTS CRUD: CANCIONES
@router.get("/", response_model=List[CancionRead], summary="Listar todas las canciones")
def listar_canciones(
    session: Session = Depends(get_session),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
    skip: int = 0,
    limit: int = 100,
):
    """
    Obtiene una lista de todas las canciones en el catálogo.

    **Requiere autenticación (todos los usuarios)**

    - **skip**: Número de registros a saltar (para paginación)
    - **limit**: Número máximo de registros a retornar
    """
    statement = select(Cancion).offset(skip).limit(limit)
    canciones = session.exec(statement).all()
    return canciones


@router.post(
    "/",
    response_model=CancionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva canción",
)
def crear_cancion(
    cancion: CancionCreate,
    session: Session = Depends(get_session),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    """
    Crea una nueva canción en el catálogo.

    **Requiere autenticación (todos los usuarios)**

    - **titulo**: Título de la canción
    - **artista**: Nombre del artista o intérprete
    - **album**: Álbum al que pertenece (opcional)
    - **duracion**: Duración en segundos
    - **año**: Año de lanzamiento (opcional)
    - **genero**: Género musical (opcional)
    """
    db_cancion = Cancion.model_validate(cancion)
    session.add(db_cancion)
    session.commit()
    session.refresh(db_cancion)
    return db_cancion


@router.get("/buscar", response_model=List[CancionRead], summary="Buscar canciones")
def buscar_canciones(
    titulo: Optional[str] = Query(None, description="Buscar por título (parcial)"),
    artista: Optional[str] = Query(None, description="Buscar por artista (parcial)"),
    genero: Optional[str] = Query(None, description="Buscar por género (exacto)"),
    session: Session = Depends(get_session),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    """
    Busca canciones por título, artista o género.

    **Requiere autenticación (todos los usuarios)**

    - **titulo**: Búsqueda parcial en el título (case-insensitive)
    - **artista**: Búsqueda parcial en el artista (case-insensitive)
    - **genero**: Búsqueda exacta por género (case-insensitive)

    Si se proporcionan múltiples parámetros, se aplicarán todos (AND).
    """
    statement = select(Cancion)

    # Aplicar filtros según los parámetros proporcionados
    if titulo:
        statement = statement.where(col(Cancion.titulo).ilike(f"%{titulo}%"))

    if artista:
        statement = statement.where(col(Cancion.artista).ilike(f"%{artista}%"))

    if genero:
        statement = statement.where(col(Cancion.genero).ilike(genero))

    canciones = session.exec(statement).all()
    return canciones


@router.get(
    "/{cancion_id}", response_model=CancionRead, summary="Obtener una canción por ID"
)
def obtener_cancion(
    cancion_id: int,
    session: Session = Depends(get_session),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    """
    Obtiene los datos de una canción específica por su ID.

    **Requiere autenticación (todos los usuarios)**

    - **cancion_id**: ID de la canción a buscar
    """
    cancion = session.get(Cancion, cancion_id)

    if not cancion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Canción con ID {cancion_id} no encontrada",
        )

    return cancion


@router.put(
    "/{cancion_id}", response_model=CancionRead, summary="Actualizar una canción"
)
def actualizar_cancion(
    cancion_id: int,
    cancion_update: CancionUpdate,
    session: Session = Depends(get_session),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    """
    Actualiza los datos de una canción existente.

    **Requiere autenticación (todos los usuarios)**

    - **cancion_id**: ID de la canción a actualizar
    - Todos los campos son opcionales
    """
    # Buscar la canción
    cancion = session.get(Cancion, cancion_id)

    if not cancion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Canción con ID {cancion_id} no encontrada",
        )

    # Actualizar solo los campos proporcionados
    cancion_data = cancion_update.model_dump(exclude_unset=True)
    for key, value in cancion_data.items():
        setattr(cancion, key, value)

    session.add(cancion)
    session.commit()
    session.refresh(cancion)
    return cancion


@router.delete(
    "/{cancion_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una canción",
)
def eliminar_cancion(
    cancion_id: int,
    session: Session = Depends(get_session),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    """
    Elimina una canción del catálogo.

    **Requiere autenticación (todos los usuarios)**

    - **cancion_id**: ID de la canción a eliminar

    Nota: También se eliminarán todos los favoritos asociados a esta canción.
    """
    cancion = session.get(Cancion, cancion_id)

    if not cancion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Canción con ID {cancion_id} no encontrada",
        )

    session.delete(cancion)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
