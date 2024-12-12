import logging
from fastapi import APIRouter, Query, Request
from typing import Optional
from celery_worker import celery_app
from ftp_utils import ftp_security
from descriptions import description_intercalaire

# Configurer le logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    ftp__id: Optional[int] = Query(
        1,
        description="ID du serveur FTP où l'image sera téléversée. Exemple : 1."
    ),
    background_color: str = Query(
        'FFFFFF',
        alias="background_color",
        description="Couleur de l'arrière-plan au format hexadécimal. Exemple : 'FFFFFF' pour blanc."
    ),
    width: int = Query(
        800,
        alias="width",
        description="Largeur de l'image en pixels. Exemple : 800."
    ),
    height: int = Query(
        600,
        alias="height",
        description="Hauteur de l'image en pixels. Exemple : 600."
    ),
    # Paramètres des textes
    t1: Optional[str] = Query(None, alias="t1", description="Texte 1. Exemple : 'Bonjour'."),
    t2: Optional[str] = Query(None, alias="t2", description="Texte 2. Exemple : 'Hello'."),
    tx1: Optional[int] = Query(None, alias="tx1", description="Position horizontale (en %) pour le texte 1."),
    ty1: Optional[int] = Query(None, alias="ty1", description="Position verticale (en %) pour le texte 1."),
    tf1: Optional[str] = Query('arial', alias="tf1", description="Police pour le texte 1."),
    tc1: Optional[str] = Query('000000', alias="tc1", description="Couleur pour le texte 1."),
    tt1: Optional[int] = Query(20, alias="tt1", description="Taille de la police pour le texte 1."),
    tx2: Optional[int] = Query(None, alias="tx2", description="Position horizontale (en %) pour le texte 2."),
    ty2: Optional[int] = Query(None, alias="ty2", description="Position verticale (en %) pour le texte 2."),
    tf2: Optional[str] = Query('arial', alias="tf2", description="Police pour le texte 2."),
    tc2: Optional[str] = Query('000000', alias="tc2", description="Couleur pour le texte 2."),
    tt2: Optional[int] = Query(20, alias="tt2", description="Taille de la police pour le texte 2."),
    # Paramètres des images additionnelles
    x1: Optional[int] = Query(None, alias="x1", description="Position horizontale (en %) pour l'image 1."),
    y1: Optional[int] = Query(None, alias="y1", description="Position verticale (en %) pour l'image 1."),
    r1: Optional[int] = Query(None, alias="r1", description="Rotation (en degrés) pour l'image 1."),
    w1: Optional[int] = Query(None, alias="w1", description="Largeur (en %) pour l'image 1."),
    c1: Optional[str] = Query(None, alias="c1", description="Filtre pour l'image 1."),
    dh1: Optional[int] = Query(None, alias="dh1", description="Découpe en haut (en %) pour l'image 1."),
    db1: Optional[int] = Query(None, alias="db1", description="Découpe en bas (en %) pour l'image 1."),
    x2: Optional[int] = Query(None, alias="x2", description="Position horizontale (en %) pour l'image 2."),
    y2: Optional[int] = Query(None, alias="y2", description="Position verticale (en %) pour l'image 2."),
    r2: Optional[int] = Query(None, alias="r2", description="Rotation (en degrés) pour l'image 2."),
    w2: Optional[int] = Query(None, alias="w2", description="Largeur (en %) pour l'image 2."),
    c2: Optional[str] = Query(None, alias="c2", description="Filtre pour l'image 2."),
    dh2: Optional[int] = Query(None, alias="dh2", description="Découpe en haut (en %) pour l'image 2."),
    db2: Optional[int] = Query(None, alias="db2", description="Découpe en bas (en %) pour l'image 2.")
):
    logger.info("Starting intercalaire creation request.")

    # Récupérer les paramètres sous forme de listes
    logger.debug("Aggregating parameters into lists.")
    xs = [x1, x2]
    ys = [y1, y2]
    rs = [r1, r2]
    ws = [w1, w2]
    cs = [c1, c2]
    dhs = [dh1, dh2]
    dbs = [db1, db2]
    ts = [t1, t2]
    tfs = [tf1, tf2]
    tcs = [tc1, tc2]
    tts = [tt1, tt2]
    txs = [tx1, tx2]
    tys = [ty1, ty2]

    # Filtrer les valeurs None
    logger.debug("Filtering None values from lists.")
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
    logger.info(f"Fetching FTP credentials for FTP ID: {ftp__id}.")
    FTP_HOST, FTP_USERNAME, FTP_PASSWORD = ftp_security(ftp__id)

    # Construction des paramètres
    logger.debug("Preparing parameters for Celery task.")
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

    # Appel de la tâche Celery
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
