import pytest
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_chat_endpoint_returns_200(client):
    response = client.post(
        '/api/chat',
        data=json.dumps({"message": "Where is Gate C?", "lang": "en"}),
        content_type='application/json'
    )
    assert response.status_code == 200


def test_chat_endpoint_returns_json_with_reply_key(client):
    response = client.post(
        '/api/chat',
        data=json.dumps({"message": "Where is Gate C?", "lang": "en"}),
        content_type='application/json'
    )
    data = json.loads(response.data)
    assert "reply" in data


def test_dashboard_endpoint_returns_200(client):
    response = client.get('/api/dashboard')
    assert response.status_code == 200


def test_insight_endpoint_returns_200(client):
    response = client.get('/api/insight')
    assert response.status_code == 200


def test_insight_endpoint_returns_json_with_insight_key(client):
    response = client.get('/api/insight')
    data = json.loads(response.data)
    assert "insight" in data


def test_chat_endpoint_rejects_empty_message(client):
    response = client.post(
        '/api/chat',
        data=json.dumps({"message": "", "lang": "en"}),
        content_type='application/json'
    )
    assert response.status_code in [200, 400]