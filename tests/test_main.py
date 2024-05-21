import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db
from app.models import Base

DATABASE_URL = "sqlite:///./test.db"


engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def test_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def client():
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client


def test_create_coil(client, test_db):
    response = client.post("/api/coil/", json={"length": 10.0, "weight": 15.0})
    assert response.status_code == 201
    data = response.json()
    assert data == 1

def test_get_coils(client, test_db):
    response = client.get("/api/coil/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["length"] == 10.0
    assert data[0]["weight"] == 15.0

def test_delete_coil(client, test_db):
    response = client.delete("/api/coil/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["date_removed"] is not None

    response = client.get("/api/coil/")
    data = response.json()
    assert len(data) == 1
    assert data[0]["date_removed"] is not None
