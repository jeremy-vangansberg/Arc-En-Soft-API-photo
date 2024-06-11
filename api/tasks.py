# tasks.py
from celery import shared_task
from utils import process_and_upload

@shared_task
def process_and_upload_task(template_url, image_url, result_file, xs, ys, rs, ws, cs, dhs, dbs, ts, tfs, tcs, tts, txs, tys, ftp_host, ftp_username, ftp_password, params):
    """
    A task to download data, process it, and upload it to a server.
    """
    process_and_upload(template_url, image_url, result_file, xs, ys, rs, ws, cs, dhs, dbs, ts, tfs, tcs, tts, txs, tys, ftp_host, ftp_username, ftp_password, params)
