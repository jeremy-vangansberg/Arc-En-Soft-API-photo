from fastapi import FastAPI, HTTPException, Query
import requests
from io import BytesIO
from typing import Optional, List
from fastapi.responses import StreamingResponse
from PIL import Image, ImageOps, ImageDraw, ImageFont
import httpx
import os
from celery_worker import celery_app

app = FastAPI()

@app.get("/create_image/")
def create_image(
    template_url: str = Query('https://edit.org/img/blog/ate-preschool-yearbook-templates-free-editable.webp', alias="template_url", description="URL of the template image"),
    image_url: str = Query('https://www.photosscolaire.com/wp-content/uploads/2023/05/03-0285-0086-scaled.jpg', alias="image_url", description="URL of the image to be added"),
    result_file: Optional[str] = Query('test.png', alias="result_file", description="Name of the file to save the result. exemple: test.png"),
    xs: List[Optional[int]] = Query([5], alias="xs", description="Coordonnées x en %"),
    ys: List[Optional[int]] = Query([5], alias="ys", description="Coordonnées x en %"),
    rs: List[Optional[int]] = Query([90], alias="rs", description="Rotation en angle. (clockwise) ex: 90 ou -90"),
    ws: List[Optional[float]] = Query([10], alias="ws", description="Largeur en %"),
    cs: List[Optional[str]] = Query(['string'], alias="cs", description="Filtre à appliquer. ex: NB"),
    dhs: List[Optional[int]] = Query([10], alias="dhs", description="% de hauteur à couper en haut"),
    dbs: List[Optional[int]] = Query([5], alias="dbs", description="% de hauteur à couper en bas"),
    ts: List[Optional[str]] = Query(['test'], alias="ts", description="Text à écrire"),
    tfs: List[Optional[str]] = Query(['arial'], alias="tfs", description="Font. ex: arial, tnr"),
    tcs: List[Optional[str]] = Query(['black'], alias="tcs", description="Couleur du texte. ex: black, white"),
    tts: List[Optional[int]] = Query([10], alias="tts", description="Taille de la police"),
    txs: List[Optional[int]] = Query([3], alias="txs", description="absolute position x"),
    tys: List[Optional[int]] = Query([3], alias="tys", description="absolute position y")
):
   
   task = celery_app.send_task(
        "tasks.process_and_upload_task", 
        args=[
            template_url,
            image_url,
            result_file,
            xs,
            ys,
            rs,
            ws,
            cs,
            dhs,
            dbs,
            ts,
            tfs,
            tcs,
            tts,
            txs,
            tys,
            os.getenv("FTP_HOST"), 
            os.getenv("FTP_USERNAME"), 
            os.getenv("FTP_PASSWORD")
        ]
    )
   return {"message": "Image processed successfully", "task_id": task.id}
