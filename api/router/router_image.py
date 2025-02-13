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
    texts: list[str] = Query(
        ["texte1", "texte2"],
        alias="texts",
        description="Liste des textes à ajouter. Exemple : ['Bonjour', 'Monde']"
    ),
    text_x_positions: list[int] = Query(
        [1, 50],
        alias="text_x_positions",
        description="Liste des positions x (en %) pour les textes. Exemple : [5, 50]"
    ),
    text_y_positions: list[int] = Query(
        [96, 96],
        alias="text_y_positions",
        description="Liste des positions y (en %) pour les textes. Exemple : [5, 5]"
    ),
    text_fonts: list[FontType] = Query(
        ['arial', 'arial'],
        alias="text_fonts",
        description="Liste des polices utilisées pour les textes. Fonts disponibles : arial, avenir, helvetica, verdana, tnr, roboto."
    ),
    text_colors: list[str] = Query(
        ['000000', '000000'],
        alias="text_colors",
        description="Liste des couleurs des textes en format hexadécimal. Exemple : ['000000', 'FFFFFF']"
    ),
    text_sizes: list[int] = Query(
        [10, 10],
        alias="text_sizes",
        description="Liste des tailles des textes en points. Exemple : [10, 15]"
    ),
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

    # Traitement des paramètres de texte
    ts_clean = [t for t in texts if t is not None] if texts else []
    
    # Si nous avons des textes, nous devons nous assurer que tous les autres paramètres sont valides
    if ts_clean:
        # Vérifier et nettoyer les positions x et y
        txs_clean = text_x_positions[:len(ts_clean)] if text_x_positions else [1] * len(ts_clean)
        tys_clean = text_y_positions[:len(ts_clean)] if text_y_positions else [96] * len(ts_clean)
        
        # Valider les positions x et y
        if not all(0 <= x <= 100 for x in txs_clean):
            raise HTTPException(
                status_code=400,
                detail="Les positions x doivent être comprises entre 0 et 100"
            )
        if not all(0 <= y <= 100 for y in tys_clean):
            raise HTTPException(
                status_code=400,
                detail="Les positions y doivent être comprises entre 0 et 100"
            )
        
        # Vérifier et nettoyer les polices
        tfs_clean = text_fonts[:len(ts_clean)] if text_fonts else [FontType.arial] * len(ts_clean)
        
        # Vérifier et nettoyer les couleurs et tailles
        tcs_clean = text_colors[:len(ts_clean)] if text_colors else ['000000'] * len(ts_clean)
        tts_clean = text_sizes[:len(ts_clean)] if text_sizes else [10] * len(ts_clean)
        
        # Valider les tailles
        if not all(0 < size <= 100 for size in tts_clean):
            raise HTTPException(
                status_code=400,
                detail="Les tailles de texte doivent être comprises entre 1 et 100"
            )
        
        # Vérifier que toutes les listes ont la même longueur
        text_lists = [ts_clean, txs_clean, tys_clean, tfs_clean, tcs_clean, tts_clean]
        if not all(len(lst) == len(ts_clean) for lst in text_lists):
            raise HTTPException(
                status_code=400,
                detail="Toutes les listes de paramètres de texte doivent avoir la même longueur"
            )
            
        # Valider les couleurs hexadécimales
        if not all(len(color) == 6 and all(c in '0123456789ABCDEFabcdef' for c in color) for color in tcs_clean):
            raise HTTPException(
                status_code=400,
                detail="Les couleurs doivent être au format hexadécimal valide (6 caractères)"
            )
    else:
        # Si pas de textes, initialiser toutes les listes comme vides
        txs_clean = []
        tys_clean = []
        tfs_clean = []
        tcs_clean = []
        tts_clean = []

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

