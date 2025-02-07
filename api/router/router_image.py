from fastapi import APIRouter, Query, Request, HTTPException
from typing import Optional
from celery_worker import celery_app

from ftp_utils import ftp_security
from descriptions import description_create_image
from enum import Enum
import logging
import datetime


router = APIRouter(
    prefix="",
    tags=["image"]
)

# Configurer le logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
    ftp_id: Optional[int] = Query(1,
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
        None,
        description="Si défini, applique un filigrane (watermark) sur l'image."
    ),
    result_w: Optional[int] = Query(
        None,
        alias="result_w",
        description="Largeur en pixels de l'image finale, avec conservation du ratio. Exemple : 800."
    ),
    x1: Optional[int] = Query(
        0,
        alias="x1",
        description="Coordonnée x (en %) pour la première image. Exemple : 50."
    ),
    y1: Optional[int] = Query(
        0,
        alias="y1",
        description="Coordonnée y (en %) pour la première image. Exemple : 50."
    ),
    r1: Optional[int] = Query(
        None,
        alias="r1",
        description="Rotation (en degrés, sens horaire) pour la première image. Exemple : 90."
    ),
    w1: Optional[float] = Query(
        None,
        alias="w1",
        description="Largeur (en %) pour la première image. Exemple : 10.0."
    ),
    c1: FilterType = Query(
        None,
        alias="c1",
        description="Filtre appliqué à la première image. Exemple : 'nb' pour noir et blanc."
    ),
    db1: Optional[int] = Query(
        None,
        alias="db1",
        description="Pourcentage de découpe en bas pour la première image. Exemple : 5."
    ),
    dh1: Optional[int] = Query(
        None,
        alias="dh1",
        description="Pourcentage de découpe en haut pour la première image. Exemple : 5."
    ),
    x2: Optional[int] = Query(None, alias="x2"),
    y2: Optional[int] = Query(None, alias="y2"),
    r2: Optional[int] = Query(None, alias="r2"),
    w2: Optional[float] = Query(None, alias="w2"),
    c2: FilterType = Query(None, alias="c2"),
    db2: Optional[int] = Query(None, alias="db2"),
    dh2: Optional[int] = Query(None, alias="dh2"),
    x3: Optional[int] = Query(None, alias="x3"),
    y3: Optional[int] = Query(None, alias="y3"),
    r3: Optional[int] = Query(None, alias="r3"),
    w3: Optional[float] = Query(None, alias="w3"),
    c3: FilterType = Query(None, alias="c3"),
    db3: Optional[int] = Query(None, alias="db3"),
    dh3: Optional[int] = Query(None, alias="dh3"),
    x4: Optional[int] = Query(None, alias="x4"),
    y4: Optional[int] = Query(None, alias="y4"),
    r4: Optional[int] = Query(None, alias="r4"),
    w4: Optional[float] = Query(None, alias="w4"),
    c4: FilterType = Query(None, alias="c4"),
    db4: Optional[int] = Query(None, alias="db4"),
    dh4: Optional[int] = Query(None, alias="dh4"),
    x5: Optional[int] = Query(None, alias="x5"),
    y5: Optional[int] = Query(None, alias="y5"),
    r5: Optional[int] = Query(None, alias="r5"),
    w5: Optional[float] = Query(None, alias="w5"),
    c5: FilterType = Query(None, alias="c5"),
    db5: Optional[int] = Query(None, alias="db5"),
    dh5: Optional[int] = Query(None, alias="dh5"),
    x6: Optional[int] = Query(None, alias="x6"),
    y6: Optional[int] = Query(None, alias="y6"),
    r6: Optional[int] = Query(None, alias="r6"),
    w6: Optional[float] = Query(None, alias="w6"),
    c6: FilterType = Query(None, alias="c6"),
    db6: Optional[int] = Query(None, alias="db6"),
    dh6: Optional[int] = Query(None, alias="dh6"),
    x7: Optional[int] = Query(None, alias="x7"),
    y7: Optional[int] = Query(None, alias="y7"),
    r7: Optional[int] = Query(None, alias="r7"),
    w7: Optional[float] = Query(None, alias="w7"),
    c7: FilterType = Query(None, alias="c7"),
    db7: Optional[int] = Query(None, alias="db7"),
    dh7: Optional[int] = Query(None, alias="dh7"),
    x8: Optional[int] = Query(None, alias="x8"),
    y8: Optional[int] = Query(None, alias="y8"),
    r8: Optional[int] = Query(None, alias="r8"),
    w8: Optional[float] = Query(None, alias="w8"),
    c8: FilterType = Query(None, alias="c8"),
    db8: Optional[int] = Query(None, alias="db8"),
    dh8: Optional[int] = Query(None, alias="dh8"),
    x9: Optional[int] = Query(None, alias="x9"),
    y9: Optional[int] = Query(None, alias="y9"),
    r9: Optional[int] = Query(None, alias="r9"),
    w9: Optional[float] = Query(None, alias="w9"),
    c9: FilterType = Query(None, alias="c9"),
    db9: Optional[int] = Query(None, alias="db9"),
    dh9: Optional[int] = Query(None, alias="dh9"),
    x10: Optional[int] = Query(None, alias="x10"),
    y10: Optional[int] = Query(None, alias="y10"),
    r10: Optional[int] = Query(None, alias="r10"),
    w10: Optional[float] = Query(None, alias="w10"),
    c10: FilterType = Query(None, alias="c10"),
    db10: Optional[int] = Query(None, alias="db10"),
    dh10: Optional[int] = Query(None, alias="dh10"),
    t1: Optional[str] = Query(None, alias="t1", description="Texte 1 à ajouter. Exemple : 'Bonjour'."),
    tx1: Optional[int] = Query(1, alias="tx1", description="Position x (en %) pour le texte 1. Exemple : 5."),
    ty1: Optional[int] = Query(96, alias="ty1", description="Position y (en %) pour le texte 1. Exemple : 5."),
    tf1: FontType = Query(None, alias="tf1", description="Police utilisée pour le texte 1. fonts disponible : arial, avenir, helvetica, verdana, tnr, roboto."),
    tc1: Optional[str] = Query('000000', alias="tc1", description="Couleur du texte 1 en format hexadécimal. Exemple : '000000'."),
    tt1: Optional[int] = Query(10, alias="tt1", description="Taille du texte 1 en points. Exemple : 10."),
    t2: Optional[str] = Query(None, alias="t2", description="Texte 2 à ajouter. Exemple : 'Bonjour le monde'."),
    tf2: FontType = Query(None, alias="tf2", description="Police utilisée pour le texte 2. fonts disponible : arial, avenir, helvetica, verdana, tnr, roboto."),
    tc2: Optional[str] = Query('000000', alias="tc2", description="Couleur du texte 2 en format hexadécimal. Exemple : 'FFFFFF'."),
    tt2: Optional[int] = Query(10, alias="tt2", description="Taille du texte 2 en points. Exemple : 15."),
    tx2: Optional[int] = Query(50, alias="tx2", description="Position x (en %) pour le texte 2. Exemple : 50."),
    ty2: Optional[int] = Query(96, alias="ty2", description="Position y (en %) pour le texte 2. Exemple : 5.")
):
    logger.info(f"Starting image processing request.{datetime.datetime.now()}")
    logger.info("Aggregating parameters into lists.")

    # Créer les listes brutes
    xs = [x1, x2, x3, x4, x5, x6, x7, x8, x9, x10]
    ys = [y1, y2, y3, y4, y5, y6, y7, y8, y9, y10]
    rs = [r1, r2, r3, r4, r5, r6, r7, r8, r9, r10]
    ws = [w1, w2, w3, w4, w5, w6, w7, w8, w9, w10]
    cs = [c1, c2, c3, c4, c5, c6, c7, c8, c9, c10]
    dhs = [dh1, dh2, dh3, dh4, dh5, dh6, dh7, dh8, dh9, dh10]
    dbs = [db1, db2, db3, db4, db5, db6, db7, db8, db9, db10]
    ts = [t1, t2]
    tfs = [tf1, tf2]
    tcs = [tc1, tc2]
    tts = [tt1, tt2]
    txs = [tx1, tx2]
    tys = [ty1, ty2]

    # Trouver les indices valides basés sur xs (position x requise)
    valid_indices = [i for i, x in enumerate(xs) if x is not None]
    if not valid_indices:
        raise HTTPException(
            status_code=400,
            detail="Au moins une position x (x1, x2, etc.) doit être spécifiée"
        )

    # Nettoyer les listes pour ne garder que les éléments avec un x valide
    xs_clean = [xs[i] for i in valid_indices]
    ys_clean = [ys[i] for i in valid_indices]
    rs_clean = [rs[i] for i in valid_indices]
    ws_clean = [ws[i] for i in valid_indices]
    cs_clean = [cs[i] for i in valid_indices]
    dhs_clean = [dhs[i] for i in valid_indices]
    dbs_clean = [dbs[i] for i in valid_indices]

    # Nettoyer les listes de texte (garder uniquement ceux avec du texte)
    valid_text_indices = [i for i, t in enumerate(ts) if t is not None]
    ts_clean = [ts[i] for i in valid_text_indices]
    tfs_clean = [tfs[i] for i in valid_text_indices]
    tcs_clean = [tcs[i] for i in valid_text_indices]
    tts_clean = [tts[i] for i in valid_text_indices]
    txs_clean = [txs[i] for i in valid_text_indices]
    tys_clean = [tys[i] for i in valid_text_indices]

    logger.info(f"Nombre d'images à traiter : {len(xs_clean)}")
    logger.info(f"Nombre de textes à ajouter : {len(ts_clean)}")

    # Paramètres de la requête
    params = {
        "template_url": template_url,
        "image_url": image_url,
        "result_file": result_file,
        "result_w": result_w,
        "xs": xs_clean,
        "ys": ys_clean,
        "rs": rs_clean,
        "ws": ws_clean,
        "cs": cs_clean,
        "dhs": dhs_clean,
        "dbs": dbs_clean,
        "ts": ts_clean,
        "tfs": tfs_clean,
        "tcs": tcs_clean,
        "tts": tts_clean,
        "txs": txs_clean,
        "tys": tys_clean
    }

    logger.info(f"Fetching FTP credentials for FTP ID: {ftp_id}.")
    FTP_HOST, FTP_URSERNAME, FTP_PASSWORD = ftp_security(ftp_id)

    logger.info("Sending task to Celery worker.")

    # Appeler la tâche Celery avec les listes nettoyées
    task = celery_app.send_task(
        "tasks.process_and_upload_task",
        args=[
            template_url,
            image_url,
            result_file,
            result_w,
            xs_clean,
            ys_clean,
            rs_clean,
            ws_clean,
            cs_clean,
            dhs_clean,
            dbs_clean,
            ts_clean,
            tfs_clean,
            tcs_clean,
            tts_clean,
            txs_clean,
            tys_clean,
            FTP_HOST, 
            FTP_URSERNAME, 
            FTP_PASSWORD,
            dpi,
            params,
            watermark_text
        ]
    )

    logger.info(f"Image processing task started with ID: {task.id}.")
    return {"message": "Image processing started", "task_id": task.id}

