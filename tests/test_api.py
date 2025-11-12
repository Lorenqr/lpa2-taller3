"""
Tests para la API de Música.
Pruebas unitarias y de integración usando pytest.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from main import app
from app.database import get_session
from app.models import Usuario, Cancion, Favorito


# =============================================================================
# CONFIGURACIÓN DE FIXTURES
# =============================================================================

# Fixture para crear una base de datos en memoria para testing
@pytest.fixture(name="session")
def session_fixture():
    """
    Crea una sesión de base de datos en memoria para cada test.
    Se limpia automáticamente después de cada test.
    """
    # TODO: Crear engine en memoria (SQLite)
    
    # TODO: Crear todas las tablas
    
    # TODO: Crear sesión

    pass


# Fixture para cliente de pruebas
@pytest.fixture(name="client")
def client_fixture(session: Session):
    """
    Crea un cliente de pruebas de FastAPI con la sesión de test.
    """
    # TODO: Override de la dependencia get_session
    
    pass


# TODO: Fixture para crear usuarios de prueba
@pytest.fixture(name="usuario_test")
def usuario_test_fixture(session: Session):
    """
    Crea un usuario de prueba en la base de datos.
    """
  
    pass


# TODO: Fixture para crear canciones de prueba
@pytest.fixture(name="musica_test")
def cancion_test_fixture(session: Session):
    """
    Crea una cancion de prueba en la base de datos.
    """
    # cancion = Cancion(
    #     titulo="canción Test",
    #     director="Director Test",
    #     genero="Drama",
    #     duracion=120,
    #     año=2020,
    #     clasificacion="PG-13",
    #     sinopsis="Una canción de prueba"
    # )
    # session.add(cancion)
    # session.commit()
    # session.refresh(cancion)
    # return cancion
    pass


# =============================================================================
# TESTS DE USUARIOS
# =============================================================================

class TestUsuarios:
    """Tests para los endpoints de usuarios."""
    
    # TODO: Test para listar usuarios
    def test_listar_usuarios(self, client: TestClient):
        """Test para GET /api/usuarios"""

        pass
    
    # TODO: Test para crear usuario
    def test_crear_usuario(self, client: TestClient):
        """Test para POST /api/usuarios"""

        pass
    
    # TODO: Test para crear usuario con correo duplicado
    def test_crear_usuario_correo_duplicado(self, client: TestClient, usuario_test: Usuario):
        """Test para verificar que no se permiten correos duplicados"""

        pass
    
    # TODO: Test para obtener usuario por ID
    def test_obtener_usuario(self, client: TestClient, usuario_test: Usuario):
        """Test para GET /api/usuarios/{id}"""

        pass
    
    # TODO: Test para obtener usuario inexistente
    def test_obtener_usuario_no_existe(self, client: TestClient):
        """Test para verificar error 404 con usuario inexistente"""

        pass
    
    # TODO: Test para actualizar usuario
    def test_actualizar_usuario(self, client: TestClient, usuario_test: Usuario):
        """Test para PUT /api/usuarios/{id}"""

        pass
    
    # TODO: Test para eliminar usuario
    def test_eliminar_usuario(self, client: TestClient, usuario_test: Usuario):
        """Test para DELETE /api/usuarios/{id}"""

        pass


# =============================================================================
# TESTS DE canciónS
# =============================================================================

class TestCancions:
    """Tests para los endpoints de cancións."""
    
    # TODO: Test para listar cancións
    def test_listar_cancions(self, client: TestClient):
        """Test para GET /api/cancions"""

        pass
    
    # TODO: Test para crear canción
    def test_crear_cancion(self, client: TestClient):
        """Test para POST /api/cancions"""

        pass
    
    # TODO: Test para obtener canción por ID
    def test_obtener_cancion(self, client: TestClient, cancion_test: Cancion):
        """Test para GET /api/cancions/{id}"""

        pass
    
    # TODO: Test para actualizar canción
    def test_actualizar_cancion(self, client: TestClient, cancion_test: Cancion):
        """Test para PUT /api/cancions/{id}"""

        pass
    
    # TODO: Test para eliminar canción
    def test_eliminar_cancion(self, client: TestClient, cancion_test: Cancion):
        """Test para DELETE /api/cancions/{id}"""

        pass
    
    # TODO: Test para buscar cancións
    def test_buscar_cancions(self, client: TestClient, cancion_test: Cancion):
        """Test para GET /api/cancions/buscar"""

        pass
    
    # TODO: Test para buscar cancións con múltiples filtros
    def test_buscar_cancions_multiples_filtros(self, client: TestClient):
        """Test para búsqueda con múltiples parámetros"""

        pass


# =============================================================================
# TESTS DE FAVORITOS
# =============================================================================

class TestFavoritos:
    """Tests para los endpoints de favoritos."""
    
    # TODO: Test para listar favoritos
    def test_listar_favoritos(self, client: TestClient):
        """Test para GET /api/favoritos"""

        pass
    
    # TODO: Test para crear favorito
    def test_crear_favorito(
        self, 
        client: TestClient, 
        usuario_test: Usuario, 
        cancion_test: Cancion
    ):
        """Test para POST /api/favoritos"""

        pass
    
    # TODO: Test para crear favorito duplicado
    def test_crear_favorito_duplicado(
        self, 
        client: TestClient, 
        usuario_test: Usuario, 
        cancion_test: Cancion
    ):
        """Test para verificar que no se permiten favoritos duplicados"""

        pass
    
    # TODO: Test para eliminar favorito
    def test_eliminar_favorito(
        self, 
        client: TestClient, 
        session: Session,
        usuario_test: Usuario, 
        cancion_test: Cancion
    ):
        """Test para DELETE /api/favoritos/{id}"""

        pass
    
    # TODO: Test para marcar favorito desde usuario
    def test_marcar_favorito_usuario(
        self, 
        client: TestClient, 
        usuario_test: Usuario, 
        cancion_test: Cancion
    ):
        """Test para POST /api/usuarios/{id}/favoritos/{id_cancion}"""

        pass
    
    # TODO: Test para listar favoritos de usuario
    def test_listar_favoritos_usuario(
        self, 
        client: TestClient, 
        session: Session,
        usuario_test: Usuario, 
        cancion_test: Cancion
    ):
        """Test para GET /api/usuarios/{id}/favoritos"""

        pass


# =============================================================================
# TESTS DE INTEGRACIÓN
# =============================================================================

class TestIntegracion:
    """Tests de integración que prueban flujos completos."""
    
    # TODO: Test de flujo completo: crear usuario, canción y marcar favorito
    def test_flujo_completo(self, client: TestClient):
        """Test que verifica el flujo completo de la aplicación"""
        # 1. Crear usuario

        # 2. Crear canción

        # 3. Marcar como favorito

        # 4. Verificar que aparece en favoritos del usuario

        pass


# =============================================================================
# TESTS DE VALIDACIÓN
# =============================================================================

class TestValidacion:
    """Tests para validaciones de datos."""
    
    # TODO: Test para validar email inválido
    def test_email_invalido(self, client: TestClient):
        """Test para verificar validación de email"""

        pass
    
    # TODO: Test para validar año de canción
    def test_año_cancion_invalido(self, client: TestClient):
        """Test para verificar validación de año"""

        pass
    
    # TODO: Test para validar campos requeridos
    def test_campos_requeridos(self, client: TestClient):
        """Test para verificar que los campos requeridos son obligatorios"""

        pass


