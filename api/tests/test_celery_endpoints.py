import pytest
from fastapi import HTTPException
from celery_worker import celery_app
from router.router_celery import router

def test_reset_queue_success(test_client, mock_celery_control, mock_celery_app):
    """Test la réinitialisation réussie de la file d'attente"""
    # Configuration des mocks
    mock_celery_app.purge.return_value = None
    mock_celery_control.revoke.return_value = None

    # Appel de l'endpoint
    response = test_client.get("/reset-queue")

    # Vérifications
    assert response.status_code == 200
    assert response.json() == {"message": "File d'attente Celery réinitialisée avec succès"}
    
    # Vérification des appels aux méthodes Celery
    mock_celery_app.purge.assert_called_once()
    mock_celery_control.revoke.assert_called_once_with(None, terminate=True)

def test_reset_queue_failure(test_client, mock_celery_control, mock_celery_app):
    """Test l'échec de la réinitialisation de la file d'attente"""
    # Simulation d'une erreur
    mock_celery_app.purge.side_effect = Exception("Erreur de connexion")

    # Appel de l'endpoint
    response = test_client.get("/reset-queue")

    # Vérifications
    assert response.status_code == 500
    assert "Erreur lors de la réinitialisation de la file d'attente" in response.json()["detail"]

def test_reset_queue_partial_failure(test_client, mock_celery_control, mock_celery_app):
    """Test une réinitialisation partielle (purge réussie mais révocation échouée)"""
    # Configuration des mocks
    mock_celery_app.purge.return_value = None
    mock_celery_control.revoke.side_effect = Exception("Erreur de révocation")

    # Appel de l'endpoint
    response = test_client.get("/reset-queue")

    # Vérifications
    assert response.status_code == 500
    assert "Erreur lors de la réinitialisation de la file d'attente" in response.json()["detail"]
    mock_celery_app.purge.assert_called_once() 