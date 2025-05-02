from fastapi.testclient import TestClient
from forward_context.main import app

client = TestClient(app)

def test_search_endpoint():
    payload = {
        "query": "unemployment rate in the USA in 2023"
    }
    response = client.post("/forward-context", json=payload)

    assert response.status_code == 200
    assert "result" in response.json()

