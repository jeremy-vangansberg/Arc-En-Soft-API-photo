# tasks.py
from celery import shared_task
from utils import process_and_upload, process_intercalaire
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def process_and_upload_task(self, template_url, image_url, result_file, result_w, xs, ys, rs, ws, cs, dhs, dbs, ts, tfs, tcs, tts, txs, tys, ftp_host, ftp_username, ftp_password, dpi, params, watermark_text):
    """
    A task to download data, process it, and upload it to a server.
    """
    logger.info(f"xs: {xs}, ys: {ys}, ws: {ws}, ts: {ts}, rs: {rs}")  # Debugging

    try:
        return process_and_upload(template_url, image_url, result_file, result_w, xs, ys, rs, ws, cs, dhs, dbs, ts, tfs, tcs, tts, txs, tys, ftp_host, ftp_username, ftp_password, dpi, params, watermark_text)
    except Exception as exc:
        logger.error(f"Erreur dans process_and_upload_task: {str(exc)}")
        if self.request.retries < self.max_retries:
            # Attendre de plus en plus longtemps entre les tentatives
            countdown = 2 ** self.request.retries  # exponential backoff
            raise self.retry(exc=exc, countdown=countdown)
        else:
            # Si toutes les tentatives ont échoué, lever l'erreur finale
            logger.error("Nombre maximum de tentatives atteint. Abandon de la tâche.")
            raise

@shared_task(bind=True, max_retries=3)
def process_intercalaire_task(self, result_file, background_color, width, height, text_blocks, ftp_host, ftp_username, ftp_password):
    try:
        return process_intercalaire(result_file, background_color, width, height, text_blocks, ftp_host, ftp_username, ftp_password)
    except Exception as exc:
        logger.error(f"Erreur dans process_intercalaire_task: {str(exc)}")
        if self.request.retries < self.max_retries:
            countdown = 2 ** self.request.retries
            raise self.retry(exc=exc, countdown=countdown)
        else:
            logger.error("Nombre maximum de tentatives atteint. Abandon de la tâche.")
            raise
