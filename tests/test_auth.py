from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_crear_y_login_usuario():
    # Crear usuario
    payload = {"nombre": "testuser", "correo": "testuser@example.com", "contrasena": "mipass123"}
    r = client.post("/api/usuarios", json=payload)
    assert r.status_code in (200, 201)
    data = r.json()
    assert "correo" in data
    assert data["correo"] == "testuser@example.com"
    # Login
    r2 = client.post("/api/login/token", data={"username": "testuser@example.com", "password": "mipass123"})
    assert r2.status_code == 200
    token = r2.json().get("access_token")
    assert token