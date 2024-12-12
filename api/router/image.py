import logging
from fastapi import APIRouter, Query, Request
from typing import Optional
from celery_worker import celery_app
from ftp_utils import ftp_security
from descriptions import description_create_image
from enum import Enum

# Configurer le logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="",
    tags=["image"]
)


class FontType(str, Enum):
    arial = "arial"
    avenir = "avenir"
    helvetica = "helvetica"
    roboto = "roboto"
    tnr = "tnr"
    verdana = "verdana"


class FilterType(str, Enum):
    nb = "nb"
    cartoon = "cartoon"


@router.get("/create_image/", description=description_create_image)
def create_image(
    request: Request,
    ftp__id: Optional[int] = Query(1,
        description="ID du serveur FTP de destination."
    ),
    template_url: str = Query(
        'https://edit.org/img/blog/ate-preschool-yearbook-templates-free-editable.webp',
        alias="template_url",
        description="URL de l'image modèle utilisée comme fond. Exemple : 'https://example.com/template.jpg'."
    ),
    image_url: str = Query(
        'https://www.photosscolaire.com/wp-content/uploads/2023/05/03-0285-0086-scaled.jpg',
        alias="image_url",
        description="URL de l'image principale à ajouter. Exemple : 'https://example.com/image.jpg'."
    ),
    result_file: Optional[str] = Query(
        'test.jpg',
        alias="result_file",
        description="chemin relatif ou absolue pour enregistrer le résultat. Exemple : 'result.jpg' ou /folder/result.jpg."
    ),
    dpi: Optional[int] = Query(
        300,
        alias="dpi",
        description="Résolution de l'image finale en DPI. Exemple : 300."
    ),
    watermark_text: Optional[str] = Query(
        "watermark",
        description="Si défini, applique un filigrane (watermark) sur l'image."
    ),
    result_w: Optional[int] = Query(
        None,
        alias="result_w",
        description="Largeur en pixels de l'image finale, avec conservation du ratio. Exemple : 800."
    ),
    x1: Optional[int] = Query(0, alias="x1"),
    y1: Optional[int] = Query(0, alias="y1"),
    r1: Optional[int] = Query(None, alias="r1"),
    w1: Optional[float] = Query(None, alias="w1"),
    c1: FilterType = Query(None, alias="c1"),
    db1: Optional[int] = Query(None, alias="db1"),
    dh1: Optional[int] = Query(None, alias="dh1"),
    x2: Optional[int] = Query(None, alias="x2"),
    y2: Optional[int] = Query(None, alias="y2"),
    r2: Optional[int] = Query(None, alias="r2"),
    w2: Optional[float] = Query(None, alias="w2"),
    c2: FilterType = Query(None, alias="c2"),
    db2: Optional[int] = Query(None, alias="db2"),
    dh2: Optional[int] = Query(None, alias="dh2"),
    t1: Optional[str] = Query(None, alias="t1"),
    tx1: Optional[int] = Query(1, alias="tx1"),
    ty1: Optional[int] = Query(96, alias="ty1"),
    tf1: FontType = Query(None, alias="tf1"),
    tc1: Optional[str] = Query('000000', alias="tc1"),
    tt1: Optional[int] = Query(10, alias="tt1"),
    t2: Optional[str] = Query(None, alias="t2"),
    tf2: FontType = Query(None, alias="tf2"),
    tc2: Optional[str] = Query('000000', alias="tc2"),
    tt2: Optional[int] = Query(10, alias="tt2"),
    tx2: Optional[int] = Query(50, alias="tx2"),
    ty2: Optional[int] = Query(96, alias="ty2")
):
    logger.info("Starting image processing request.")

    # Agréger les paramètres en listes
    logger.debug("Aggregating parameters into lists.")
    xs = [x1, x2]
    ys = [y1, y2]
    rs = [r1, r2]
    ws = [w1, w2]
    cs = [c1, c2]
    dhs = [dh1, dh2]
    dbs = [db1, db2]
    ts = [t1, t2]

    # Filtrer les valeurs None
    logger.debug("Filtering None values from lists.")
    xs = [x for x in xs if x is not None]
    ys = [y for y in ys if y is not None]

    # Récupération des informations FTP
    logger.info(f"Fetching FTP credentials for FTP ID: {ftp__id}.")
    FTP_HOST, FTP_USERNAME, FTP_PASSWORD = ftp_security(ftp__id)

    # Préparation des paramètres
    logger.debug("Preparing parameters for Celery task.")
    params = {
        "template_url": template_url,
        "image_url": image_url,
        "result_file": result_file,
        "result_w": result_w,
        "xs": xs,
        "ys": ys
    }

    # Lancer la tâche Celery
    logger.info("Sending task to Celery worker.")
    task = celery_app.send_task(
        "tasks.process_and_upload_task",
        args=[
            template_url,
            image_url,
            result_file,
            result_w,
            xs,
            ys,
            FTP_HOST,
            FTP_USERNAME,
            FTP_PASSWORD,
            dpi,
            params,
            watermark_text
        ]
    )

    logger.info(f"Image processing task started with ID: {task.id}.")
    return {"message": "Image processing started", "task_id": task.id}
