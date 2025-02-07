import logging
import datetime
from fastapi import APIRouter, Query, Request
from typing import Optional
from celery_worker import celery_app
from ftp_utils import ftp_security
from descriptions import description_intercalaire

# Configuration du logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

router = APIRouter(
    prefix="",
    tags=["intercalaire"]
)

@router.get("/intercalaire", description=description_intercalaire)
def create_intercalaire(
    request: Request,
    result_file: Optional[str] = Query(
        'exemple/test.jpg',
        alias="result_file",
        description="Chemin relatif ou absolu pour enregistrer le résultat. Exemple : 'intercalaire.jpg'."
    ),
    ftp__id: Optional[int] = Query(1, description="ID du serveur FTP où l'image sera téléversée. Exemple : 1."),
    background_color: str = Query(
        'FFFFFF', alias="background_color", description="Couleur de l'arrière-plan au format hexadécimal."
    ),
    width: int = Query(800, alias="width", description="Largeur de l'image en pixels."),
    height: int = Query(600, alias="height", description="Hauteur de l'image en pixels."),
    # Paramètres des textes
    t1: Optional[str] = Query(None, alias="t1", description="Texte 1."),
    t2: Optional[str] = Query(None, alias="t2", description="Texte 2."),
    tx1: Optional[int] = Query(None, alias="tx1", description="Position horizontale pour le texte 1."),
    ty1: Optional[int] = Query(None, alias="ty1", description="Position verticale pour le texte 1."),
    tf1: Optional[str] = Query('arial', alias="tf1", description="Police pour le texte 1."),
    tc1: Optional[str] = Query('000000', alias="tc1", description="Couleur pour le texte 1."),
    tt1: Optional[int] = Query(20, alias="tt1", description="Taille de la police pour le texte 1."),
    tx2: Optional[int] = Query(None, alias="tx2", description="Position horizontale pour le texte 2."),
    ty2: Optional[int] = Query(None, alias="ty2", description="Position verticale pour le texte 2."),
    tf2: Optional[str] = Query('arial', alias="tf2", description="Police pour le texte 2."),
    tc2: Optional[str] = Query('000000', alias="tc2", description="Couleur pour le texte 2."),
    tt2: Optional[int] = Query(20, alias="tt2", description="Taille de la police pour le texte 2."),
    # Paramètres des images additionnelles
    x1: Optional[int] = Query(None, alias="x1", description="Position horizontale pour l'image 1."),
    y1: Optional[int] = Query(None, alias="y1", description="Position verticale pour l'image 1."),
    r1: Optional[int] = Query(None, alias="r1", description="Rotation pour l'image 1."),
    w1: Optional[int] = Query(None, alias="w1", description="Largeur pour l'image 1."),
    c1: Optional[str] = Query(None, alias="c1", description="Filtre pour l'image 1."),
    dh1: Optional[int] = Query(None, alias="dh1", description="Découpe en haut pour l'image 1."),
    db1: Optional[int] = Query(None, alias="db1", description="Découpe en bas pour l'image 1."),
):
    logger.info(f"Starting intercalaire generation request at {datetime.datetime.now()}")
    
    # Agréger les paramètres en listes
    logger.info("Aggregating parameters into lists.")
    xs = [x1]
    ys = [y1]
    rs = [r1]
    ws = [w1]
    cs = [c1]
    dhs = [dh1]
    dbs = [db1]
    ts = [t1, t2]
    tfs = [tf1, tf2]
    tcs = [tc1, tc2]
    tts = [tt1, tt2]
    txs = [tx1, tx2]
    tys = [ty1, ty2]

    # Filtrer les valeurs None
    logger.info("Filtering None values from parameter lists.")
    xs = [x for x in xs if x is not None]
    ys = [y for y in ys if y is not None]
    rs = [r for r in rs if r is not None]
    ws = [w for w in ws if w is not None]
    cs = [c for c in cs if c is not None]
    dhs = [dh for dh in dhs if dh is not None]
    dbs = [db for db in dbs if db is not None]
    ts = [t for t in ts if t is not None]
    tfs = [tf for tf in tfs if tf is not None]
    tcs = [tc for tc in tcs if tc is not None]
    tts = [tt for tt in tts if tt is not None]
    txs = [tx for tx in txs if tx is not None]
    tys = [ty for ty in tys if ty is not None]

    # Récupération des informations FTP
    logger.info(f"Fetching FTP credentials for FTP ID: {ftp__id}")
    FTP_HOST, FTP_USERNAME, FTP_PASSWORD = ftp_security(ftp__id)

    # Construction des paramètres
    logger.info("Building task parameters.")
    params = {
        "result_file": result_file,
        "background_color": background_color,
        "width": width,
        "height": height,
        "xs": xs,
        "ys": ys,
        "rs": rs,
        "ws": ws,
        "cs": cs,
        "dhs": dhs,
        "dbs": dbs,
        "ts": ts,
        "tfs": tfs,
        "tcs": tcs,
        "tts": tts,
        "txs": txs,
        "tys": tys
    }

    # Envoi de la tâche Celery
    logger.info("Sending task to Celery worker.")
    task = celery_app.send_task(
        "tasks.process_intercalaire_task",
        args=[
            result_file,
            background_color,
            width,
            height,
            params,
            FTP_HOST,
            FTP_USERNAME,
            FTP_PASSWORD
        ]
    )

    logger.info(f"Intercalaire processing task started with ID: {task.id}.")

    return {"message": "Intercalaire processing started", "task_id": task.id}
