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
    none = "none"


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
    image_url: list[str] = Query(
        [
            'https://www.photosscolaire.com/wp-content/uploads/2023/05/03-0285-0086-scaled.jpg',
            'https://www.photosscolaire.com/wp-content/uploads/2023/05/03-0285-0087-scaled.jpg'
        ],
        alias="image_url",
        description="Liste des URLs des images à ajouter. Exemple : ['https://example.com/image1.jpg', 'https://example.com/image2.jpg']"
    ),
    image_x: list[int] = Query(
        [20, 60],
        alias="image_x",
        description="Liste des coordonnées x (en %) pour chaque image. Exemple : [10, 50]"
    ),
    image_y: list[int] = Query(
        [30, 30],
        alias="image_y",
        description="Liste des coordonnées y (en %) pour chaque image. Exemple : [10, 50]"
    ),
    image_rotation: list[Optional[int]] = Query(
        [0, 0],
        alias="image_rotation",
        description="Liste des angles de rotation (en degrés) pour chaque image. Exemple : [90, 180]"
    ),
    image_width: list[Optional[float]] = Query(
        [30.0, 30.0],
        alias="image_width",
        description="Liste des largeurs (en %) pour chaque image. Exemple : [10.0, 20.0]"
    ),
    image_filter: list[Optional[FilterType]] = Query(
        [FilterType.none, FilterType.nb],
        alias="image_filter",
        description="Liste des filtres à appliquer pour chaque image. Exemple : ['nb', 'cartoon']"
    ),
    image_crop_top: list[Optional[int]] = Query(
        [5, 10],
        alias="image_crop_top",
        description="Liste des pourcentages de découpe en haut pour chaque image. Exemple : [5, 10]"
    ),
    image_crop_bottom: list[Optional[int]] = Query(
        [5, 10],
        alias="image_crop_bottom",
        description="Liste des pourcentages de découpe en bas pour chaque image. Exemple : [5, 10]"
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
    text: list[str] = Query(
        ["Bonjour", "Monde"],
        alias="text",
        description="Liste des textes à ajouter. Exemple : ['Bonjour', 'Monde']"
    ),
    text_x: list[int] = Query(
        [20, 60],
        alias="text_x",
        description="Liste des coordonnées x (en %) pour chaque texte. Exemple : [10, 50]"
    ),
    text_y: list[int] = Query(
        [70, 70],
        alias="text_y",
        description="Liste des coordonnées y (en %) pour chaque texte. Exemple : [10, 50]"
    ),
    text_font: list[Optional[str]] = Query(
        ["arial", "tnr"],
        alias="text_font",
        description="Liste des polices pour chaque texte. Exemple : ['arial', 'tnr']"
    ),
    text_color: list[Optional[str]] = Query(
        ["000000", "FF0000"],
        alias="text_color",
        description="Liste des couleurs (format hex) sans #. Exemple : ['000000', 'FF0000']"
    ),
    text_size: list[Optional[int]] = Query(
        [24, 36],
        alias="text_size",
        description="Liste des tailles des textes en points. Exemple : [10, 15]"
    ),
):
    logger.info(f"Starting image processing request.{datetime.datetime.now()}")
    logger.info("Aggregating parameters into lists.")

    # Vérifier qu'il y a au moins une image à traiter
    if not image_url:
        raise HTTPException(
            status_code=400,
            detail="Au moins une URL d'image doit être spécifiée"
        )

    # Vérifier que toutes les listes d'images ont la même longueur
    image_lists = [
        image_url, image_x, image_y, image_rotation, 
        image_width, image_filter, image_crop_top, image_crop_bottom
    ]
    if not all(len(lst) == len(image_url) for lst in image_lists):
        raise HTTPException(
            status_code=400,
            detail="Toutes les listes de paramètres d'image doivent avoir la même longueur"
        )

    # Valider les positions x et y
    if not all(0 <= x <= 100 for x in image_x):
        raise HTTPException(
            status_code=400,
            detail="Les positions x doivent être comprises entre 0 et 100"
        )
    if not all(0 <= y <= 100 for y in image_y):
        raise HTTPException(
            status_code=400,
            detail="Les positions y doivent être comprises entre 0 et 100"
        )

    # Traitement des paramètres de texte
    ts_clean = [t for t in text if t is not None] if text else []
    
    # Si nous avons des textes, nous devons nous assurer que tous les autres paramètres sont valides
    if ts_clean:
        # Vérifier et nettoyer les positions x et y
        txs_clean = text_x[:len(ts_clean)] if text_x else [1] * len(ts_clean)
        tys_clean = text_y[:len(ts_clean)] if text_y else [96] * len(ts_clean)
        
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
        tfs_clean = text_font[:len(ts_clean)] if text_font else [FontType.arial] * len(ts_clean)
        
        # Vérifier et nettoyer les couleurs et tailles
        tcs_clean = text_color[:len(ts_clean)] if text_color else ['000000'] * len(ts_clean)
        tts_clean = text_size[:len(ts_clean)] if text_size else [10] * len(ts_clean)
        
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

    logger.info(f"Nombre d'images à traiter : {len(image_url)}")
    logger.info(f"Nombre de textes à ajouter : {len(ts_clean)}")

    # Paramètres de la requête
    params = {
        "template_url": template_url,
        "image_url": image_url,
        "result_file": result_file,
        "result_w": result_w,
        "image_x": image_x,
        "image_y": image_y,
        "image_rotation": image_rotation,
        "image_width": image_width,
        "image_filter": image_filter,
        "image_crop_top": image_crop_top,
        "image_crop_bottom": image_crop_bottom,
        "text": ts_clean,
        "text_font": tfs_clean,
        "text_color": tcs_clean,
        "text_size": tts_clean,
        "text_x": txs_clean,
        "text_y": tys_clean
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
            image_x,
            image_y,
            image_rotation,
            image_width,
            image_filter,
            image_crop_top,
            image_crop_bottom,
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

