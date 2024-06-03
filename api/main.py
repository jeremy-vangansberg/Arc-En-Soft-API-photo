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
    xs: List[Optional[int]] = Query([5], alias="xs", description="List of x coordinates"),
    ys: List[Optional[int]] = Query([5], alias="ys", description="List of y coordinates"),
    rs: List[Optional[int]] = Query([90], alias="rs", description="List of rotation angles"),
    ws: List[Optional[float]] = Query([10], alias="ws", description="List of widths"),
    cs: List[Optional[str]] = Query(['string'], alias="cs", description="List of filters"),
    dhs: List[Optional[int]] = Query([10], alias="dhs", description="List of top crop heights"),
    dbs: List[Optional[int]] = Query([5], alias="dbs", description="List of bottom crop heights"),
    ts: List[Optional[str]] = Query(['string'], alias="ts", description="List of texts"),
    tfs: List[Optional[str]] = Query(['string'], alias="tfs", description="List of font sizes"),
    tts: List[Optional[int]] = Query([0], alias="tts", description="List of text x coordinates"),
    txs: List[Optional[int]] = Query([0], alias="txs", description="List of text y coordinates"),
    tys: List[Optional[int]] = Query([0], alias="tys", description="List of text aligns"),
    tas: List[Optional[str]] = Query(['string'], alias="tas", description="List of text aligns"),
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
            tts,
            txs,
            tys,
            tas,
            os.getenv("FTP_HOST"), 
            os.getenv("FTP_USERNAME"), 
            os.getenv("FTP_PASSWORD")
        ]
    )
   return {"message": "Image processed successfully", "task_id": task.id}
