from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root_path_not_found():
    response = client.get("/")
    assert response.status_code == 404

def test_shorten_url():
    response = client.post("/shorten", params={"long_url": "https://www.google.com"})
    assert response.status_code == 200
    json_response = response.json()
    assert "short_url" in json_response
    assert len(json_response["short_url"]) > 10 