def test_healthcheck(client):
    response = client.get("/health")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["status"] == "healthy"


def test_env_vars():
    import os

    assert os.getenv("POSTGRES_USER") == "testuser"
    assert os.getenv("POSTGRES_PASSWORD") == "testpassword"
