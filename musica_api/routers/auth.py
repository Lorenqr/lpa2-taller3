"""
Router para autenticación y gestión de acceso.
Endpoints para login, registro y gestión de tokens.
"""

from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from musica_api.database import get_session
from musica_api.models import Usuario, RolUsuario
from musica_api.schemas import Token, LoginRequest, UsuarioRegister, UsuarioRead
from musica_api.auth import (
    autenticar_usuario,
    crear_access_token,
    hashear_contraseña,
    obtener_usuario_actual,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)


router = APIRouter()


@router.post("/login", response_model=Token, summary="Iniciar sesión")
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Session = Depends(get_session),
):
    """
    Autentica un usuario y retorna un token JWT.

    - **username**: Correo electrónico del usuario
    - **password**: Contraseña del usuario

    Retorna un token de acceso que debe incluirse en las peticiones posteriores.
    """
    usuario = autenticar_usuario(form_data.username, form_data.password, session)

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo. Contacte al administrador.",
        )

    # Crear el token JWT
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = crear_access_token(
        data={"sub": usuario.correo, "rol": usuario.rol},
        expires_delta=access_token_expires,
    )

    return Token(access_token=access_token, token_type="bearer", rol=usuario.rol)


@router.post("/login-json", response_model=Token, summary="Iniciar sesión (JSON)")
def login_json(login_data: LoginRequest, session: Session = Depends(get_session)):
    """
    Autentica un usuario usando JSON y retorna un token JWT.

    - **correo**: Correo electrónico del usuario
    - **contraseña**: Contraseña del usuario

    Alternativa al endpoint /login que acepta JSON en lugar de form data.
    """
    usuario = autenticar_usuario(login_data.correo, login_data.contraseña, session)

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo. Contacte al administrador.",
        )

    # Crear el token JWT
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = crear_access_token(
        data={"sub": usuario.correo, "rol": usuario.rol},
        expires_delta=access_token_expires,
    )

    return Token(access_token=access_token, token_type="bearer", rol=usuario.rol)


@router.post(
    "/register",
    response_model=UsuarioRead,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nuevo usuario",
)
def registrar_usuario(
    usuario_data: UsuarioRegister, session: Session = Depends(get_session)
):
    """
    Registra un nuevo usuario en el sistema con rol de usuario regular.

    - **nombre**: Nombre completo del usuario
    - **correo**: Correo electrónico único
    - **contraseña**: Contraseña (mínimo 6 caracteres)

    Los usuarios registrados mediante este endpoint siempre tendrán rol "usuario".
    """
    # Verificar si el correo ya existe
    statement = select(Usuario).where(Usuario.correo == usuario_data.correo)
    usuario_existente = session.exec(statement).first()

    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El correo '{usuario_data.correo}' ya está registrado",
        )

    # Crear el nuevo usuario con rol de usuario regular
    contraseña_hash = hashear_contraseña(usuario_data.contraseña)

    nuevo_usuario = Usuario(
        nombre=usuario_data.nombre,
        correo=usuario_data.correo,
        contraseña_hash=contraseña_hash,
        rol=RolUsuario.USUARIO,
        activo=True,
    )

    session.add(nuevo_usuario)
    session.commit()
    session.refresh(nuevo_usuario)

    return nuevo_usuario


@router.get("/me", response_model=UsuarioRead, summary="Obtener usuario actual")
def obtener_perfil(usuario_actual: Usuario = Depends(obtener_usuario_actual)):
    """
    Obtiene la información del usuario autenticado actualmente.

    Requiere token JWT válido en el header Authorization.
    """
    return usuario_actual


@router.get("/verify", summary="Verificar token")
def verificar_token_endpoint(usuario_actual: Usuario = Depends(obtener_usuario_actual)):
    """
    Verifica si el token JWT es válido y retorna información básica del usuario.

    Útil para verificar si la sesión sigue activa.
    """
    return {
        "valido": True,
        "usuario_id": usuario_actual.id,
        "correo": usuario_actual.correo,
        "rol": usuario_actual.rol,
        "activo": usuario_actual.activo,
    }
