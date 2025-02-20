import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from main import app

@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.fixture
def mock_celery_app():
    with patch('celery_worker.celery_app') as mock:
        yield mock

def test_reset_queue_success(test_client, mock_celery_app):
    """Test la réinitialisation réussie de la file d'attente"""
    response = test_client.get("/reset-queue")
    assert response.status_code == 200
    assert response.json() == {"message": "File d'attente Celery réinitialisée avec succès"}
    assert mock_celery_app.control.purge.called
    assert mock_celery_app.control.revoke.called

def test_reset_queue_failure(test_client, mock_celery_app):
    """Test l'échec de la réinitialisation"""
    mock_celery_app.control.purge.side_effect = Exception("Erreur test")
    
    response = test_client.get("/reset-queue")
    assert response.status_code == 500
    assert "erreur" in response.json()["detail"].lower() 