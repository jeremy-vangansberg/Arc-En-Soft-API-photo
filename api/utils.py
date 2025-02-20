from datetime import datetime
import os
from ftplib import FTP
from typing import List, Dict
from PIL import Image
from photo_utils import (
    apply_watermark, 
    apply_resize_template, 
    add_text, 
    apply_filter, 
    apply_crop, 
    apply_rotation, 
    load_image,
    TextRenderStrategy
)
from ftp_utils import log_request_to_ftp, log_to_ftp, upload_file_ftp
from io import BytesIO
import logging



def clean_up_files(file_paths: list):
    """Supprime les fichiers temporaires spécifiés."""
    for path in file_paths:
        if path and os.path.exists(path):
            os.remove(path)

def process_intercalaire(result_file: str, background_color: str, width: int, height: int, text_blocks: List[Dict], ftp_host: str, ftp_username: str, ftp_password: str):
    """
    A function to create an image with multiple text blocks and upload it to a server.
    """
    try:
        # Create a new image with the specified background color
        background_color = "#" + background_color
        img = Image.new('RGB', (width, height), background_color)

        # Add each text block
        for block in text_blocks:
            img = add_text(
                img=img,
                text=block["text"],
                font_name=block.get("font_name", "arial"),
                font_size=block.get("font_size", 20),
                x=block["x"],
                y=block["y"],
                color=block.get("color", "black"),
                align=block.get("align", "left")
            )

        # Sauvegarder directement dans un BytesIO
        with BytesIO() as bio:
            img.save(bio, format='JPEG')
            bio.seek(0)
            
            # Upload the file to the FTP server
            with FTP(ftp_host, ftp_username, ftp_password) as ftp:
                directory_path, filename = os.path.split(result_file)
                ensure_ftp_path(ftp, directory_path)
                ftp.storbinary(f'STOR {result_file}', bio)

        return {"message": "Intercalaire created successfully"}

    except Exception as e:
        log_message = f"Error creating intercalaire: {str(e)}"
        log_to_ftp(
            ftp_host=ftp_host,
            ftp_username=ftp_password,
            ftp_password=ftp_password,
            log_message=log_message,
            log_folder="error_logs"
        )
        raise e

def ensure_ftp_path(ftp, path, create_dirs=True):
    """Assure que le chemin existe sur le serveur FTP."""
    logger = logging.getLogger(__name__)
    
    if not path:
        logger.debug("Chemin vide, pas de navigation nécessaire")
        return
        
    # Gestion des chemins absolus et relatifs
    if path.startswith('/'):
        logger.info("Chemin absolu détecté, retour à la racine")
        ftp.cwd('/')
        path = path[1:]
    
    # Navigation dans l'arborescence
    current_path = []
    for directory in path.split('/'):
        if directory:
            current_path.append(directory)
            try:
                logger.info(f"Tentative d'accès au dossier: {directory}")
                ftp.cwd(directory)
                logger.info(f"Navigation réussie vers: {directory}")
            except Exception as e:
                if create_dirs:
                    try:
                        logger.info(f"Dossier {directory} non trouvé, tentative de création")
                        ftp.mkd(directory)
                        logger.info(f"Dossier {directory} créé avec succès")
                        ftp.cwd(directory)
                        logger.info(f"Navigation vers le nouveau dossier {directory} réussie")
                    except Exception as create_error:
                        logger.error(f"Erreur lors de la création du dossier {directory}: {str(create_error)}")
                        if hasattr(create_error, 'args'):
                            logger.error(f"Détails de l'erreur: {create_error.args}")
                        raise
                else:
                    logger.error(f"Le dossier {directory} n'existe pas et create_dirs est False")
                    logger.error(f"Chemin complet tenté: /{'/'.join(current_path)}")
                    raise

def process_and_upload(template_url, image_url, result_file, result_w, xs, ys, rs, ws, cs, dhs, dbs, ts, tfs, tcs, tts, txs, tys, ftp_host, ftp_username, ftp_password, dpi, params, watermark_text):
    """
    Télécharge les données, applique les transformations et charge l'image sur un serveur.
    """
    logger = logging.getLogger(__name__)
    logger.info("=== DÉBUT DU PROCESSUS ===")

    try:
        # Log des paramètres
        logger.info(f"path du ftp: {result_file}")
        logger.info(f"URL du template: {template_url}")
        logger.info(f"URLs des images: {image_url}")
        logger.info(f"Paramètres images: xs={xs}, ys={ys}, ws={ws}, rs={rs}, cs={cs}")
        logger.info(f"Paramètres texte: texts={ts}, fonts={tfs}, colors={tcs}, sizes={tts}, positions_x={txs}, positions_y={tys}")
        
        # Charger le template
        try:
            template = load_image(template_url, is_template=True)
            logger.info(f"Template chargé avec succès. Dimensions: {template.size}")
        except ValueError as e:
            logger.error(f"Erreur lors du chargement du template: {str(e)}")
            raise ValueError(f"Impossible de charger le template. Erreur: {str(e)}")
        
        # Charger les images
        try:
            # S'assurer que image_url est une liste
            if not isinstance(image_url, list):
                image_url = [image_url]
            images = load_image(image_url)
            logger.info(f"Images source chargées avec succès. Nombre: {len(images)}")
        except ValueError as e:
            logger.error(f"Erreur lors du chargement des images: {str(e)}")
            raise ValueError(f"Impossible de charger une ou plusieurs images. Erreur: {str(e)}")

        # Vérifier que nous avons le bon nombre d'images
        if len(images) != len(xs):
            raise ValueError(f"Le nombre d'images ({len(images)}) ne correspond pas au nombre de positions ({len(xs)})")

        # Calculer le facteur d'échelle
        reference_width = 1000
        target_width = result_w if result_w else template.width
        scale_factor = target_width / reference_width
        logger.info(f"Facteur d'échelle calculé: {scale_factor} (target_width={target_width}, reference_width={reference_width})")

        # Valeurs par défaut
        default_rotation = 0
        default_width_percentage = 100
        default_filter = 'none'
        default_dh = 0
        default_db = 0

        # Fonction pour récupérer une valeur ou la valeur par défaut
        def get_value_with_default(values, index, default):
            return values[index] if index < len(values) and values[index] is not None else default

        # Transformation des images et application sur le template
        current_template = template.copy()
        
        # Transformation de chaque image
        for i, image in enumerate(images):
            try:
                logger.info(f"Traitement de l'image {i+1}/{len(images)}")
                # Copie indépendante de l'image originale
                new_image = image.copy()

                # Appliquer le rognage (les pourcentages restent les mêmes)
                top = get_value_with_default(dhs, i, default_dh)
                bottom = get_value_with_default(dbs, i, default_db)
                new_image = apply_crop(new_image, top, bottom)

                # Appliquer la rotation (les angles restent les mêmes)
                rotation = get_value_with_default(rs, i, default_rotation)
                new_image = apply_rotation(new_image, rotation)

                # Appliquer le filtre
                filter_ = get_value_with_default(cs, i, default_filter)
                new_image = apply_filter(new_image, filter_)

                # Appliquer le redimensionnement en tenant compte du facteur d'échelle
                width_factor = get_value_with_default(ws, i, default_width_percentage)
                scaled_width = int((width_factor / 100) * current_template.width)
                aspect_ratio = new_image.width / new_image.height
                scaled_height = int(scaled_width / aspect_ratio)

                if scaled_width <= 0 or scaled_height <= 0:
                    raise ValueError(f"Dimensions invalides à l'étape {i} : width={scaled_width}, height={scaled_height}")

                new_image = new_image.resize((scaled_width, scaled_height))

                # Appliquer le filigrane avec une taille adaptée
                if watermark_text:
                    new_image = apply_watermark(new_image, watermark_text)

                # Positionner l'image sur le template (les pourcentages restent les mêmes)
                x = int(get_value_with_default(xs, i, 0) / 100 * current_template.width)
                y = int(get_value_with_default(ys, i, 0) / 100 * current_template.height)
                current_template.paste(new_image, (x, y))

            except Exception as e:
                log_message = f"Erreur à l'étape {i} : {e}"
                log_to_ftp(ftp_host, ftp_username, ftp_password, log_message, log_folder="/error_logs")
                raise e

        # Traitement des paramètres de texte
        if ts and len(ts) > 0:
            logger.info(f"Ajout de {len(ts)} textes")
            for i in range(len(ts)):
                try:
                    # Vérifier que tous les paramètres nécessaires sont disponibles
                    if (i < len(ts) and i < len(tfs) and i < len(tcs) and 
                        i < len(tts) and i < len(txs) and i < len(tys)):
                        
                        text = ts[i]
                        font_name = tfs[i]
                        color = tcs[i]
                        font_size = tts[i]
                        tx = txs[i]
                        ty = tys[i]

                        # Ajuster la taille de la police en fonction de la taille finale
                        adjusted_font_size = int(font_size * scale_factor)
                        logger.info(f"Texte {i+1}: '{text}', police={font_name}, taille={font_size}->{adjusted_font_size}, position=({tx}%, {ty}%)")
                        
                        current_template = add_text(
                            img=current_template,
                            text=text,
                            font_name=font_name,
                            color=color,
                            font_size=adjusted_font_size,
                            x=tx,
                            y=ty,
                            strategy=TextRenderStrategy.COMBINED,
                            dpi=dpi
                        )
                except Exception as e:
                    log_message = f"Erreur ajout texte à l'étape {i} : {e}"
                    log_to_ftp(ftp_host, ftp_username, ftp_password, log_message, log_folder="/error_logs")
                    raise e

        # Redimensionner le template final si spécifié
        if result_w:
            logger.debug(f"Redimensionnement du template à {result_w}px de large...")
            current_template = apply_resize_template(current_template, result_w)

        # Sauvegarder et uploader le fichier
        if result_file:
            logger.info(f"Début de l'upload du fichier final: {result_file}")
            with BytesIO() as bio:
                logger.debug("Sauvegarde de l'image en mémoire")
                current_template.save(bio, format='JPEG', dpi=(dpi, dpi))
                bio.seek(0)
                
                try:
                    logger.info("Tentative de connexion FTP")
                    with FTP(ftp_host, ftp_username, ftp_password) as ftp:
                        # Log du répertoire initial
                        initial_dir = ftp.pwd()
                        logger.info(f"Répertoire FTP initial: {initial_dir}")
                        
                        directory_path, filename = os.path.split(result_file)
                        logger.info(f"Chemin du dossier: {directory_path}, Nom du fichier: {filename}")
                        
                        # D'abord naviguer vers le bon dossier
                        logger.info(f"Navigation vers le dossier: {directory_path}")
                        ensure_ftp_path(ftp, directory_path, create_dirs=True)
                        
                        # Vérifier le répertoire courant après navigation
                        current_dir = ftp.pwd()
                        logger.info(f"Répertoire FTP après navigation: {current_dir}")
                        
                        # Liste des fichiers dans le répertoire courant
                        try:
                            files = ftp.nlst()
                            logger.info(f"Fichiers dans le répertoire courant: {files}")
                        except Exception as e:
                            logger.warning(f"Impossible de lister les fichiers: {str(e)}")
                        
                        # Puis uploader le fichier en utilisant uniquement le nom du fichier
                        logger.info(f"Tentative d'upload du fichier: {filename} dans le dossier actuel: {current_dir}")
                        ftp.storbinary(f'STOR {filename}', bio)
                        
                        # Vérifier que le fichier a bien été créé
                        try:
                            new_files = ftp.nlst()
                            if filename in new_files:
                                logger.info(f"Fichier {filename} trouvé après upload")
                            else:
                                logger.warning(f"Fichier {filename} non trouvé après upload. Fichiers présents: {new_files}")
                        except Exception as e:
                            logger.warning(f"Impossible de vérifier la présence du fichier: {str(e)}")
                        
                        logger.info("Upload terminé avec succès")
                except Exception as e:
                    logger.error(f"Erreur lors de l'upload FTP: {type(e).__name__}: {str(e)}")
                    # Log des détails supplémentaires de l'erreur si disponibles
                    if hasattr(e, 'args'):
                        logger.error(f"Détails de l'erreur: {e.args}")
                    raise

    except Exception as e:
        error_message = f"Erreur lors du traitement de l'image: {str(e)}"
        logger.error(error_message)
        log_to_ftp(ftp_host, ftp_username, ftp_password, error_message, log_folder="/error_logs")
        raise

    finally:
        if result_file and os.path.exists(result_file):
            clean_up_files([result_file])
