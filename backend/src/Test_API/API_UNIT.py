import sys
import os
import pytest
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flask import session
from unittest.mock import patch
from api import api  # Importera Flask-appen från `api.py`
import DB

# Fixture för Flask testklient
@pytest.fixture
def client():
    with api.test_client() as client:
        with api.app_context():
            yield client

# ------------------- Test för login -------------------
def test_login_success(client):
    with patch('DB.check_login', return_value=True):
        response = client.post('/login', json={"username": "test_user", "password": "correct_password"})
        data = response.get_json()

        assert response.status_code == 200
        assert data['success'] is True

        with client.session_transaction() as sess:
            assert sess['user_id'] == "test_user"

def test_login_failure(client):
    with patch('DB.check_login', return_value=False):
        response = client.post('/login', json={"username": "wrong_user", "password": "wrong_password"})
        data = response.get_json()

        assert response.status_code == 401
        assert data['success'] is False

def test_login_missing_fields(client):
    response = client.post('/login', json={})
    data = response.get_json()

    assert response.status_code == 400
    assert data['success'] is False


# ------------------- Test för setup -------------------
