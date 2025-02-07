from fastapi import APIRouter
from celery.app.control import Control
from celery_worker import celery_app
from fastapi import HTTPException

router = APIRouter(
    prefix="",
    tags=["celery"]
)

@router.get("/reset-queue", description="Réinitialise la file d'attente Celery en purgeant toutes les tâches en attente.")
async def reset_celery_queue():
    """
    Réinitialise la file d'attente Celery en purgeant toutes les tâches en attente.
    """
    try:
        # Création d'une instance Control pour interagir avec Celery
        control = Control(celery_app)
        
        # Purge toutes les files d'attente
        celery_app.control.purge()
        
        # Optionnel : Révocation de toutes les tâches en cours
        control.revoke(None, terminate=True)
        
        return {"message": "File d'attente Celery réinitialisée avec succès"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la réinitialisation de la file d'attente : {str(e)}"
        )
