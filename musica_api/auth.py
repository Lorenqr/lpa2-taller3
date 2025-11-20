"""
Utilidades de autenticación y seguridad.
Maneja JWT, hashing de contraseñas y verificación de permisos.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select

from musica_api.models import Usuario, RolUsuario
from musica_api.schemas import TokenData
from musica_api.database import get_session
from musica_api.config import settings


# Configuración de JWT
SECRET_KEY = settings.jwt_secret_key
ALGORITHM = settings.jwt_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.jwt_expiration_minutes


# Configuración de hashing de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# OAuth2 scheme para obtener el token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# Funciones de hashing


def verificar_contraseña(contraseña_plana: str, contraseña_hash: str) -> bool:
    """Verifica si una contraseña plana coincide con su hash."""
    return pwd_context.verify(contraseña_plana, contraseña_hash)


def hashear_contraseña(contraseña: str) -> str:
    """Genera un hash de la contraseña."""
    return pwd_context.hash(contraseña)


# Funciones de JWT


def crear_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un token JWT con los datos proporcionados.

    Args:
        data: Diccionario con los datos a incluir en el token
        expires_delta: Tiempo de expiración del token

    Returns:
        Token JWT codificado
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def verificar_token(token: str) -> TokenData:
    """
    Verifica y decodifica un token JWT.

    Args:
        token: Token JWT a verificar

    Returns:
        TokenData con los datos del token

    Raises:
        HTTPException: Si el token es inválido
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        correo: str = payload.get("sub")
        rol: str = payload.get("rol")

        if correo is None:
            raise credentials_exception

        token_data = TokenData(correo=correo, rol=rol)
        return token_data

    except JWTError:
        raise credentials_exception


# Dependencias de autenticación


async def obtener_usuario_actual(
    token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)
) -> Usuario:
    """
    Obtiene el usuario actual basado en el token JWT.

    Args:
        token: Token JWT del usuario
        session: Sesión de base de datos

    Returns:
        Usuario autenticado

    Raises:
        HTTPException: Si el token es inválido o el usuario no existe
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = verificar_token(token)

    statement = select(Usuario).where(Usuario.correo == token_data.correo)
    usuario = session.exec(statement).first()

    if usuario is None:
        raise credentials_exception

    if not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Usuario inactivo"
        )

    return usuario


async def obtener_usuario_activo(
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
) -> Usuario:
    """
    Verifica que el usuario esté activo.

    Args:
        usuario_actual: Usuario autenticado

    Returns:
        Usuario activo

    Raises:
        HTTPException: Si el usuario está inactivo
    """
    if not usuario_actual.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Usuario inactivo"
        )
    return usuario_actual


# Dependencias de autorización por rol


async def verificar_administrador(
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
) -> Usuario:
    """
    Verifica que el usuario actual sea administrador.

    Args:
        usuario_actual: Usuario autenticado

    Returns:
        Usuario administrador

    Raises:
        HTTPException: Si el usuario no es administrador
    """
    if usuario_actual.rol != RolUsuario.ADMINISTRADOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos de administrador",
        )
    return usuario_actual


async def verificar_usuario_o_admin(
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
) -> Usuario:
    """
    Verifica que el usuario actual sea usuario regular o administrador.

    Args:
        usuario_actual: Usuario autenticado

    Returns:
        Usuario autenticado
    """
    if usuario_actual.rol not in [RolUsuario.USUARIO, RolUsuario.ADMINISTRADOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para esta acción",
        )
    return usuario_actual


# Función de autenticación


def autenticar_usuario(
    correo: str, contraseña: str, session: Session
) -> Optional[Usuario]:
    """
    Autentica un usuario verificando sus credenciales.

    Args:
        correo: Correo electrónico del usuario
        contraseña: Contraseña del usuario
        session: Sesión de base de datos

    Returns:
        Usuario si las credenciales son válidas, None en caso contrario
    """
    statement = select(Usuario).where(Usuario.correo == correo)
    usuario = session.exec(statement).first()

    if not usuario:
        return None

    if not verificar_contraseña(contraseña, usuario.contraseña_hash):
        return None

    return usuario
