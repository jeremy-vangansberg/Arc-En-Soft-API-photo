from fastapi import APIRouter
from celery.app.control import Control
from celery_worker import celery_app, REDIS_HOST, REDIS_USER, REDIS_PASSWORD
from fastapi import HTTPException
import redis
import logging

logger = logging.getLogger(__name__)

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
        # Connexion directe à Redis
        redis_client = redis.Redis(
            host=REDIS_HOST,
            port=6379,
            username=REDIS_USER,
            password=REDIS_PASSWORD,
            decode_responses=True
        )
        
        # Récupérer toutes les clés liées à Celery
        celery_keys = redis_client.keys('celery*')
        logger.info(f"Clés Redis trouvées: {celery_keys}")
        
        # Supprimer toutes les clés Celery
        if celery_keys:
            redis_client.delete(*celery_keys)
            logger.info(f"Suppression de {len(celery_keys)} clés Redis")
        
        # Essayer aussi la méthode standard de Celery
        try:
            celery_app.control.purge()
            logger.info("Purge Celery effectuée")
            
            # Révocation de toutes les tâches en cours
            celery_app.control.revoke(None, terminate=True)
            logger.info("Révocation des tâches en cours effectuée")
        except Exception as celery_error:
            logger.warning(f"Erreur lors de la purge Celery standard: {str(celery_error)}")
            
        return {"message": "File d'attente Redis/Celery réinitialisée avec succès"}
        
    except Exception as e:
        logger.error(f"Erreur lors de la réinitialisation de Redis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la réinitialisation de la file d'attente : {str(e)}"
        )

@router.get("/queue-status", description="Affiche l'état actuel des files d'attente Celery.")
async def get_queue_status():
    """
    Affiche l'état actuel des files d'attente Celery.
    """
    try:
        # Connexion directe à Redis
        redis_client = redis.Redis(
            host=REDIS_HOST,
            port=6379,
            username=REDIS_USER,
            password=REDIS_PASSWORD,
            decode_responses=True
        )
        
        # Récupérer toutes les clés liées à Celery
        celery_keys = redis_client.keys('celery*')
        
        # Récupérer les informations sur chaque clé
        queue_info = {}
        for key in celery_keys:
            key_type = redis_client.type(key)
            if key_type == 'list':
                queue_info[key] = {
                    'type': key_type,
                    'length': redis_client.llen(key),
                    'sample': redis_client.lrange(key, 0, 2)  # Échantillon des 3 premiers éléments
                }
            elif key_type == 'hash':
                queue_info[key] = {
                    'type': key_type,
                    'fields': redis_client.hkeys(key),
                    'sample': {k: redis_client.hget(key, k) for k in list(redis_client.hkeys(key))[:3]}
                }
            else:
                queue_info[key] = {
                    'type': key_type
                }
        
        return {
            "queue_count": len(celery_keys),
            "queues": queue_info
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'état des files d'attente: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération de l'état des files d'attente: {str(e)}"
        )
