"""
Router para gestionar Usuarios.
Endpoints para CRUD de usuarios y gestión de favoritos.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlmodel import Session, select

from musica_api.database import get_session
from musica_api.models import Usuario, Favorito, Cancion
from musica_api.schemas import (
    UsuarioCreate,
    UsuarioRead,
    UsuarioUpdate,
    FavoritoRead,
    CancionRead
)

router = APIRouter()


# ENDPOINTS CRUD: USUARIOS

@router.get("/", response_model=List[UsuarioRead], summary="Listar todos los usuarios")
def listar_usuarios(
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100
):
    """
    Obtiene una lista de todos los usuarios registrados.
    
    - **skip**: Número de registros a saltar (para paginación)
    - **limit**: Número máximo de registros a retornar
    """
    statement = select(Usuario).offset(skip).limit(limit)
    usuarios = session.exec(statement).all()
    return usuarios


@router.post("/", response_model=UsuarioRead, status_code=status.HTTP_201_CREATED, summary="Crear un nuevo usuario")
def crear_usuario(
    usuario: UsuarioCreate,
    session: Session = Depends(get_session)
):
    """
    Crea un nuevo usuario en el sistema.
    
    - **nombre**: Nombre completo del usuario (mínimo 2 caracteres)
    - **correo**: Correo electrónico único del usuario
    """
    # Verificar si el correo ya existe
    statement = select(Usuario).where(Usuario.correo == usuario.correo)
    usuario_existente = session.exec(statement).first()
    
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El correo '{usuario.correo}' ya está registrado"
        )
    
    # Crear el nuevo usuario
    db_usuario = Usuario.model_validate(usuario)
    session.add(db_usuario)
    session.commit()
    session.refresh(db_usuario)
    return db_usuario


@router.get("/{usuario_id}", response_model=UsuarioRead, summary="Obtener un usuario por ID")
def obtener_usuario(
    usuario_id: int,
    session: Session = Depends(get_session)
):
    """
    Obtiene los datos de un usuario específico por su ID.
    
    - **usuario_id**: ID del usuario a buscar
    """
    usuario = session.get(Usuario, usuario_id)
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {usuario_id} no encontrado"
        )
    
    return usuario


@router.put("/{usuario_id}", response_model=UsuarioRead, summary="Actualizar un usuario")
def actualizar_usuario(
    usuario_id: int,
    usuario_update: UsuarioUpdate,
    session: Session = Depends(get_session)
):
    """
    Actualiza los datos de un usuario existente.
    
    - **usuario_id**: ID del usuario a actualizar
    - Campos opcionales: nombre, correo
    """
    # Buscar el usuario
    usuario = session.get(Usuario, usuario_id)
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {usuario_id} no encontrado"
        )
    
    # Si se intenta actualizar el correo, verificar que no exista
    if usuario_update.correo and usuario_update.correo != usuario.correo:
        statement = select(Usuario).where(Usuario.correo == usuario_update.correo)
        correo_existente = session.exec(statement).first()
        
        if correo_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El correo '{usuario_update.correo}' ya está en uso"
            )
    

    usuario_data = usuario_update.model_dump(exclude_unset=True)
    for key, value in usuario_data.items():
        setattr(usuario, key, value)
    
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar un usuario")
def eliminar_usuario(
    usuario_id: int,
    session: Session = Depends(get_session)
):
    """
    Elimina un usuario del sistema.
    
    - **usuario_id**: ID del usuario a eliminar
    
    Nota: También se eliminarán todos sus favoritos asociados.
    """
    usuario = session.get(Usuario, usuario_id)
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {usuario_id} no encontrado"
        )
    
    session.delete(usuario)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ENDPOINTS: FAVORITOS DE USUARIO

@router.get("/{usuario_id}/favoritos", response_model=List[CancionRead], summary="Listar favoritos de un usuario")
def listar_favoritos_usuario(
    usuario_id: int,
    session: Session = Depends(get_session)
):
    """
    Obtiene todas las canciones marcadas como favoritas por un usuario.
    
    - **usuario_id**: ID del usuario
    """
    # Verificar que el usuario existe
    usuario = session.get(Usuario, usuario_id)
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {usuario_id} no encontrado"
        )
    
    # Obtener las canciones favoritas
    statement = (
        select(Cancion)
        .join(Favorito)
        .where(Favorito.id_usuario == usuario_id)
    )
    canciones = session.exec(statement).all()
    return canciones


@router.post("/{usuario_id}/favoritos/{cancion_id}", response_model=FavoritoRead, status_code=status.HTTP_201_CREATED, summary="Marcar canción como favorita")
def marcar_favorito(
    usuario_id: int,
    cancion_id: int,
    session: Session = Depends(get_session)
):
    """
    Marca una canción como favorita para un usuario específico.
    
    - **usuario_id**: ID del usuario
    - **cancion_id**: ID de la canción a marcar como favorita
    """
    # Verificar que el usuario existe
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {usuario_id} no encontrado"
        )
    
    # Verificar que la canción existe
    cancion = session.get(Cancion, cancion_id)
    if not cancion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Canción con ID {cancion_id} no encontrada"
        )
    
    # Verificar si ya existe el favorito
    statement = select(Favorito).where(
        Favorito.id_usuario == usuario_id,
        Favorito.id_cancion == cancion_id
    )
    favorito_existente = session.exec(statement).first()
    
    if favorito_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta canción ya está marcada como favorita"
        )
    
    # Crear el favorito
    favorito = Favorito(id_usuario=usuario_id, id_cancion=cancion_id)
    session.add(favorito)
    session.commit()
    session.refresh(favorito)
    return favorito


@router.delete("/{usuario_id}/favoritos/{cancion_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar favorito específico")
def eliminar_favorito_especifico(
    usuario_id: int,
    cancion_id: int,
    session: Session = Depends(get_session)
):
    """
    Elimina una canción de los favoritos de un usuario.
    
    - **usuario_id**: ID del usuario
    - **cancion_id**: ID de la canción a eliminar de favoritos
    """
    # Buscar el favorito
    statement = select(Favorito).where(
        Favorito.id_usuario == usuario_id,
        Favorito.id_cancion == cancion_id
    )
    favorito = session.exec(statement).first()
    
    if not favorito:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorito no encontrado"
        )
    
    session.delete(favorito)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)