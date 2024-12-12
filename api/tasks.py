# tasks.py
from celery import shared_task
from utils import process_and_upload, process_intercalaire

@shared_task
def process_and_upload_task(template_url, image_url, result_file, result_w, xs, ys, rs, ws, cs, dhs, dbs, ts, tfs, tcs, tts, txs, tys, ftp_host, ftp_username, ftp_password, dpi, params, watermark_text):
    """
    A task to download data, process it, and upload it to a server.
    """
    process_and_upload(template_url, image_url, result_file, result_w, xs, ys, rs, ws, cs, dhs, dbs, ts, tfs, tcs, tts, txs, tys, ftp_host, ftp_username, ftp_password, dpi, params, watermark_text)

@shared_task
def process_intercalaire_task(result_file, background_color, width, height, text_blocks, ftp_host, ftp_username, ftp_password):
    return process_intercalaire(result_file, background_color, width, height, text_blocks, ftp_host, ftp_username, ftp_password)
