from fastapi.testclient import TestClient
from main import app
import pytest


@pytest.fixture
def client():
    yield TestClient(app)


def test_root(client: TestClient) -> None:
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json() == "Hello World"

