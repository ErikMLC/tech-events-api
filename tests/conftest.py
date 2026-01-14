from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient

from app.config import settings
from app.main import app


# Cliente de prueba para hacer requests a la API
@pytest.fixture(scope="module")
def client():
    """
    Fixture que proporciona un cliente de prueba para FastAPI.
    """
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="module")
async def test_db():
    """
    Fixture que proporciona una conexión a la base de datos de prueba.
    """
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[f"{settings.database_name}_test"]

    yield db

    # Limpiar después de los tests
    await client.drop_database(f"{settings.database_name}_test")
    client.close()


@pytest.fixture
def sample_event():
    """
    Fixture que proporciona datos de ejemplo para un evento.
    Genera una fecha en el futuro para evitar errores de validación.
    """
    future_date = datetime.now() + timedelta(days=30)

    return {
        "title": "Test Conference 2025",
        "description": "A test conference for developers",
        "date": future_date.isoformat(),  # Fecha en el futuro
        "location": "Test City",
        "organizer": "test@conference.com",
        "tags": ["test", "python"],
        "capacity": 100,
    }
