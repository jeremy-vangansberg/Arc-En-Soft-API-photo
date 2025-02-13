import os
import sys
import pytest
from fastapi.testclient import TestClient
from main import app
from celery_worker import celery_app
from unittest.mock import MagicMock, patch

# Configure le PYTHONPATH pour accéder aux modules du projet
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def test_client():
    """Fixture pour créer un client de test FastAPI"""
    return TestClient(app)

@pytest.fixture
def mock_celery_control():
    """Fixture pour mocker le contrôle Celery"""
    with patch('celery.app.control.Control') as mock_control:
        mock_instance = MagicMock()
        mock_control.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_celery_app():
    """Fixture pour mocker l'application Celery"""
    with patch.object(celery_app, 'control') as mock_app_control:
        yield mock_app_control 



