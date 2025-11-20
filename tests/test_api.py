"""
Tests para la API de Música.
Pruebas unitarias y de integración usando pytest.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from main import app
from musica_api.database import get_session
from musica_api.models import Usuario, Cancion, Favorito


# =============================================================================
# CONFIGURACIÓN DE FIXTURES
# =============================================================================

@pytest.fixture(name="session")
def session_fixture():
    """
    Crea una sesión de base de datos en memoria para cada test.
    Se limpia automáticamente después de cada test.
    """
    # Crear engine en memoria (SQLite)
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    
    # Crear todas las tablas
    SQLModel.metadata.create_all(engine)
    
    # Crear sesión
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """
    Crea un cliente de pruebas de FastAPI con la sesión de test.
    """
    # Override de la dependencia get_session
    def get_session_override():
        return session
    
    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="usuario_test")
def usuario_test_fixture(session: Session):
    """
    Crea un usuario de prueba en la base de datos.
    """
    usuario = Usuario(
        nombre="Usuario Test",
        correo="usuario.test@example.com"
    )
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario


@pytest.fixture(name="cancion_test")
def cancion_test_fixture(session: Session):
    """
    Crea una cancion de prueba en la base de datos.
    """
    cancion = Cancion(
        titulo="Canción Test",
        artista="Artista Test",
        album="Album Test",
        duracion=180,
        año=2020,
        genero="Rock"
    )
    session.add(cancion)
    session.commit()
    session.refresh(cancion)
    return cancion


# =============================================================================
# TESTS DE USUARIOS
# =============================================================================

class TestUsuarios:
    """Tests para los endpoints de usuarios."""
    
    def test_listar_usuarios(self, client: TestClient):
        """Test para GET /api/usuarios"""
        response = client.get("/api/usuarios")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_crear_usuario(self, client: TestClient):
        """Test para POST /api/usuarios"""
        response = client.post("/api/usuarios", json={
            "nombre": "Nuevo Usuario",
            "correo": "nuevo@example.com"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["nombre"] == "Nuevo Usuario"
        assert data["correo"] == "nuevo@example.com"
        assert "id" in data
    
    def test_crear_usuario_correo_duplicado(self, client: TestClient, usuario_test: Usuario):
        """Test para verificar que no se permiten correos duplicados"""
        response = client.post("/api/usuarios", json={
            "nombre": "Otro Usuario",
            "correo": usuario_test.correo
        })
        assert response.status_code == 400
        assert "ya está registrado" in response.json()["detail"].lower()
    
    def test_obtener_usuario(self, client: TestClient, usuario_test: Usuario):
        """Test para GET /api/usuarios/{id}"""
        response = client.get(f"/api/usuarios/{usuario_test.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == usuario_test.id
        assert data["nombre"] == usuario_test.nombre
        assert data["correo"] == usuario_test.correo
    
    def test_obtener_usuario_no_existe(self, client: TestClient):
        """Test para verificar error 404 con usuario inexistente"""
        response = client.get("/api/usuarios/99999")
        assert response.status_code == 404
        assert "no encontrado" in response.json()["detail"].lower()
    
    def test_actualizar_usuario(self, client: TestClient, usuario_test: Usuario):
        """Test para PUT /api/usuarios/{id}"""
        response = client.put(f"/api/usuarios/{usuario_test.id}", json={
            "nombre": "Usuario Actualizado"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["nombre"] == "Usuario Actualizado"
        assert data["correo"] == usuario_test.correo
    
    def test_eliminar_usuario(self, client: TestClient, usuario_test: Usuario):
        """Test para DELETE /api/usuarios/{id}"""
        response = client.delete(f"/api/usuarios/{usuario_test.id}")
        assert response.status_code == 204
        
        # Verificar que el usuario ya no existe
        response = client.get(f"/api/usuarios/{usuario_test.id}")
        assert response.status_code == 404


# =============================================================================
# TESTS DE CANCIONES
# =============================================================================

class TestCanciones:
    """Tests para los endpoints de canciones."""
    
    def test_listar_canciones(self, client: TestClient):
        """Test para GET /api/canciones"""
        response = client.get("/api/canciones")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_crear_cancion(self, client: TestClient):
        """Test para POST /api/canciones"""
        response = client.post("/api/canciones", json={
            "titulo": "Nueva Canción",
            "artista": "Artista Nuevo",
            "album": "Album Nuevo",
            "duracion": 240,
            "año": 2023,
            "genero": "Pop"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["titulo"] == "Nueva Canción"
        assert data["artista"] == "Artista Nuevo"
        assert "id" in data
    
    def test_obtener_cancion(self, client: TestClient, cancion_test: Cancion):
        """Test para GET /api/canciones/{id}"""
        response = client.get(f"/api/canciones/{cancion_test.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == cancion_test.id
        assert data["titulo"] == cancion_test.titulo
    
    def test_actualizar_cancion(self, client: TestClient, cancion_test: Cancion):
        """Test para PUT /api/canciones/{id}"""
        response = client.put(f"/api/canciones/{cancion_test.id}", json={
            "titulo": "Canción Actualizada",
            "artista": "Artista Actualizado"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["titulo"] == "Canción Actualizada"
    
    def test_eliminar_cancion(self, client: TestClient, cancion_test: Cancion):
        """Test para DELETE /api/canciones/{id}"""
        response = client.delete(f"/api/canciones/{cancion_test.id}")
        assert response.status_code == 204
        
        # Verificar que la canción ya no existe
        response = client.get(f"/api/canciones/{cancion_test.id}")
        assert response.status_code == 404
    
    def test_buscar_canciones(self, client: TestClient, cancion_test: Cancion):
        """Test para GET /api/canciones/buscar"""
        response = client.get(f"/api/canciones/buscar?titulo={cancion_test.titulo}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert data[0]["titulo"] == cancion_test.titulo
    
    def test_buscar_canciones_multiples_filtros(self, client: TestClient):
        """Test para búsqueda con múltiples parámetros"""
        # Crear una canción específica
        client.post("/api/canciones", json={
            "titulo": "Búsqueda Test",
            "artista": "Artista Búsqueda",
            "album": "Album Test",
            "duracion": 200,
            "año": 2022,
            "genero": "Jazz"
        })
        
        response = client.get("/api/canciones/buscar?artista=Artista Búsqueda&genero=Jazz")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0


# =============================================================================
# TESTS DE FAVORITOS
# =============================================================================

class TestFavoritos:
    """Tests para los endpoints de favoritos."""
    
    def test_listar_favoritos(self, client: TestClient):
        """Test para GET /api/favoritos"""
        response = client.get("/api/favoritos")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_crear_favorito(
        self, 
        client: TestClient, 
        usuario_test: Usuario, 
        cancion_test: Cancion
    ):
        """Test para POST /api/favoritos"""
        response = client.post("/api/favoritos", json={
            "id_usuario": usuario_test.id,
            "id_cancion": cancion_test.id
        })
        assert response.status_code == 201
        data = response.json()
        assert data["id_usuario"] == usuario_test.id
        assert data["id_cancion"] == cancion_test.id
    
    def test_crear_favorito_duplicado(
        self, 
        client: TestClient, 
        usuario_test: Usuario, 
        cancion_test: Cancion
    ):
        """Test para verificar que no se permiten favoritos duplicados"""
        # Crear el primer favorito
        client.post("/api/favoritos", json={
            "id_usuario": usuario_test.id,
            "id_cancion": cancion_test.id
        })
        
        # Intentar crear el mismo favorito de nuevo
        response = client.post("/api/favoritos", json={
            "id_usuario": usuario_test.id,
            "id_cancion": cancion_test.id
        })
        assert response.status_code == 400
    
    def test_eliminar_favorito(
        self, 
        client: TestClient, 
        session: Session,
        usuario_test: Usuario, 
        cancion_test: Cancion
    ):
        """Test para DELETE /api/favoritos/{id}"""
        # Crear un favorito
        favorito = Favorito(
            id_usuario=usuario_test.id,
            id_cancion=cancion_test.id
        )
        session.add(favorito)
        session.commit()
        session.refresh(favorito)
        
        # Eliminar el favorito
        response = client.delete(f"/api/favoritos/{favorito.id}")
        assert response.status_code == 204
    
    def test_marcar_favorito_usuario(
        self, 
        client: TestClient, 
        usuario_test: Usuario, 
        cancion_test: Cancion
    ):
        """Test para POST /api/usuarios/{id}/favoritos/{id_cancion}"""
        response = client.post(f"/api/usuarios/{usuario_test.id}/favoritos/{cancion_test.id}")
        assert response.status_code == 201
        data = response.json()
        assert data["id_usuario"] == usuario_test.id
        assert data["id_cancion"] == cancion_test.id
    
    def test_listar_favoritos_usuario(
        self, 
        client: TestClient, 
        session: Session,
        usuario_test: Usuario, 
        cancion_test: Cancion
    ):
        """Test para GET /api/usuarios/{id}/favoritos"""
        # Crear un favorito
        favorito = Favorito(
            id_usuario=usuario_test.id,
            id_cancion=cancion_test.id
        )
        session.add(favorito)
        session.commit()
        
        # Listar favoritos del usuario
        response = client.get(f"/api/usuarios/{usuario_test.id}/favoritos")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0


# =============================================================================
# TESTS DE INTEGRACIÓN
# =============================================================================

class TestIntegracion:
    """Tests de integración que prueban flujos completos."""
    
    def test_flujo_completo(self, client: TestClient):
        """Test que verifica el flujo completo de la aplicación"""
        # 1. Crear usuario
        response_usuario = client.post("/api/usuarios", json={
            "nombre": "Usuario Flujo",
            "correo": "flujo@example.com"
        })
        assert response_usuario.status_code == 201
        usuario_id = response_usuario.json()["id"]

        # 2. Crear canción
        response_cancion = client.post("/api/canciones", json={
            "titulo": "Canción Flujo",
            "artista": "Artista Flujo",
            "duracion": 200,
            "año": 2023,
            "genero": "Rock"
        })
        assert response_cancion.status_code == 201
        cancion_id = response_cancion.json()["id"]

        # 3. Marcar como favorito
        response_favorito = client.post(f"/api/usuarios/{usuario_id}/favoritos/{cancion_id}")
        assert response_favorito.status_code == 201

        # 4. Verificar que aparece en favoritos del usuario
        response_lista = client.get(f"/api/usuarios/{usuario_id}/favoritos")
        assert response_lista.status_code == 200
        favoritos = response_lista.json()
        assert len(favoritos) > 0
        assert favoritos[0]["titulo"] == "Canción Flujo"


# =============================================================================
# TESTS DE VALIDACIÓN
# =============================================================================

class TestValidacion:
    """Tests para validaciones de datos."""
    
    def test_email_invalido(self, client: TestClient):
        """Test para verificar validación de email"""
        response = client.post("/api/usuarios", json={
            "nombre": "Usuario Test",
            "correo": "correo-invalido"
        })
        assert response.status_code == 422
    
    def test_año_cancion_invalido(self, client: TestClient):
        """Test para verificar validación de año"""
        response = client.post("/api/canciones", json={
            "titulo": "Canción Test",
            "artista": "Artista Test",
            "duracion": 180,
            "año": 3000,  # Año en el futuro lejano
            "genero": "Rock"
        })
        assert response.status_code == 422
    
    def test_campos_requeridos(self, client: TestClient):
        """Test para verificar que los campos requeridos son obligatorios"""
        # Intentar crear usuario sin correo
        response = client.post("/api/usuarios", json={
            "nombre": "Usuario Sin Correo"
        })
        assert response.status_code == 422
        
        # Intentar crear canción sin titulo
        response = client.post("/api/canciones", json={
            "artista": "Artista Test",
            "duracion": 180
        })
        assert response.status_code == 422
