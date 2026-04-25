from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@patch("app.main.generate_reply")
def test_chat_endpoint_with_mocked_gemini(mock_generate):
    mock_generate.return_value = "Mocked AI reply about elections."
    
    response = client.post("/chat", json={"message": "How do I vote?", "context": {}})
    assert response.status_code == 200
    assert response.json()["reply"] == "Mocked AI reply about elections."

def test_eligibility_endpoint_validates_input():
    # Valid
    response = client.get("/eligibility?age=20&citizen=true&state=CA")
    assert response.status_code == 200
    assert response.json()["eligible"] is True
    
    # Invalid state length
    response = client.get("/eligibility?age=20&citizen=true&state=CALI")
    assert response.status_code == 422

def test_timeline_endpoint_returns_json():
    response = client.get("/timeline?state=TX")
    assert response.status_code == 200
    assert "registration_deadline" in response.json()

def test_timeline_endpoint_invalid_state():
    response = client.get("/timeline?state=XX")
    assert response.status_code == 404
