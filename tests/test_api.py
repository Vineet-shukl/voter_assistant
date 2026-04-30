import json
from unittest.mock import patch, MagicMock
import pytest
from flask import Request

# Need to mock firebase_admin before importing main
with patch('firebase_admin.initialize_app'), \
     patch('firebase_admin.firestore.client'):
    from functions.main import chat, health, eligibility, timeline, states

# --- Helper to create mock Flask requests ---
def make_mock_request(method="GET", url="/", json_data=None, args=None, headers=None):
    from werkzeug.test import EnvironBuilder
    builder = EnvironBuilder(method=method, path=url, json=json_data, query_string=args, headers=headers)
    env = builder.get_environ()
    req = Request(env)
    return req

# --- Tests ---
def test_health_endpoint():
    req = make_mock_request(method="GET", url="/health")
    resp = health(req)
    assert resp.status_code == 200
    assert json.loads(resp.get_data()) == {"status": "ok"}

@patch("functions.main.generate_reply")
@patch("functions.main.get_db")
def test_chat_endpoint_with_mocked_gemini(mock_get_db, mock_generate):
    # Mock firestore rate limit
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db
    mock_generate.return_value = "Mocked AI reply about elections."
    
    req = make_mock_request(
        method="POST", 
        url="/chat", 
        json_data={"message": "How do I vote?", "context": {}},
        headers={"X-Forwarded-For": "192.168.1.1"}
    )
    
    # We must patch CORS to allow localhost or just skip it.
    # The actual implementation allows any request to return CORS headers.
    resp = chat(req)
    
    assert resp.status_code == 200
    data = json.loads(resp.get_data())
    assert data["reply"] == "Mocked AI reply about elections."

def test_eligibility_endpoint_validates_input():
    # Valid
    req1 = make_mock_request(method="GET", url="/eligibility", args={"age": "20", "citizen": "true", "state": "CA"})
    resp1 = eligibility(req1)
    assert resp1.status_code == 200
    assert json.loads(resp1.get_data())["eligible"] is True
    
    # Invalid state length
    req2 = make_mock_request(method="GET", url="/eligibility", args={"age": "20", "citizen": "true", "state": "CALI"})
    resp2 = eligibility(req2)
    assert resp2.status_code == 422

def test_timeline_endpoint_returns_json():
    req = make_mock_request(method="GET", url="/timeline", args={"state": "TX"})
    resp = timeline(req)
    assert resp.status_code == 200
    assert "registration_deadline" in json.loads(resp.get_data())

def test_timeline_endpoint_invalid_state():
    req = make_mock_request(method="GET", url="/timeline", args={"state": "XX"})
    resp = timeline(req)
    assert resp.status_code == 404
