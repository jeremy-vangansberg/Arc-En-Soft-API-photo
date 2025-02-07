from celery import Celery
import os
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    force=True
)

REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
REDIS_USER = os.getenv('REDIS_USER')
REDIS_HOST = os.getenv('REDIS_HOST')

celery_app = Celery(
    "worker",
    broker=f"redis://{REDIS_USER}:{REDIS_PASSWORD}@{REDIS_HOST}:6379",
    include=["tasks"]  # Assurez-vous de mettre à jour le chemin vers vos tâches Celery
)

# Configuration de Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],  # Accepte le contenu JSON
    result_serializer='json',
    timezone='Europe/Paris',
    enable_utc=True,
    worker_log_format='%(asctime)s - %(levelname)s - %(message)s',
    worker_task_log_format='%(asctime)s - %(levelname)s - %(task_name)s - %(message)s',
    task_track_started=True,
    task_time_limit=3600,
)
