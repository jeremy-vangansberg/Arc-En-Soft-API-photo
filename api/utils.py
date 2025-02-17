from datetime import datetime
import os
from ftplib import FTP
from typing import List, Dict
from PIL import Image
from photo_utils import apply_watermark, apply_resize_template, add_text, apply_filter, apply_crop, apply_rotation, load_image
from ftp_utils import log_request_to_ftp, log_to_ftp, upload_file_ftp



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

        # Save the image temporarily
        temp_file_path = f"/tmp/intercalaire_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        img.save(temp_file_path)

        # Upload the file to the FTP server
        upload_file_ftp(temp_file_path, ftp_host, ftp_username, ftp_password, result_file)

        # Clean up temporary files
        clean_up_files([temp_file_path])

        return {"message": "Intercalaire created successfully"}

    except Exception as e:
        log_message = f"Error creating intercalaire: {str(e)}"
        log_to_ftp(
            ftp_host=ftp_host,
            ftp_username=ftp_username,
            ftp_password=ftp_password,
            log_message=log_message,
            log_folder="error_logs"
        )
        raise e

def process_and_upload(template_url, image_url, result_file, result_w, xs, ys, rs, ws, cs, dhs, dbs, ts, tfs, tcs, tts, txs, tys, ftp_host, ftp_username, ftp_password, dpi, params, watermark_text):
    """
    Télécharge les données, applique les transformations et charge l'image sur un serveur.
    """
    log_request_to_ftp(params, ftp_host, ftp_username, ftp_password)

    try:
        print("=== DÉBUT DU PROCESSUS ===")
        # Charger le template et les images
        template = load_image(template_url, is_template=True)
        print(f"Template chargé, dimensions: {template.size}")
        
        images = load_image(image_url)
        if not isinstance(images, list):
            images = [images]
        print(f"Images source chargées, nombre: {len(images)}")

        # Redimensionner le template final en premier
        if result_w:
            print(f"Redimensionnement du template à {result_w}px de large...")
            template = apply_resize_template(template, result_w)
            print(f"Template redimensionné")

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
        print(f"\n=== TRAITEMENT TEMPLATE ===")
        
        # Transformation de chaque image
        for i, image in enumerate(images):
            try:
                print(f"\n=== TRAITEMENT IMAGE {i+1} ===")
                # Copie indépendante de l'image originale
                new_image = image.copy()
                print(f"Dimensions du template actuel: {current_template.size}")

                # Appliquer le rognage
                top = get_value_with_default(dhs, i, default_dh)
                bottom = get_value_with_default(dbs, i, default_db)
                new_image = apply_crop(new_image, top, bottom)
                print(f"Étape {i}: Après rognage : {new_image.size}")

                # Appliquer la rotation
                rotation = get_value_with_default(rs, i, default_rotation)
                new_image = apply_rotation(new_image, rotation)
                print(f"Étape {i}: Après rotation ({rotation}°) : {new_image.size}")

                # Appliquer le filtre
                filter_ = get_value_with_default(cs, i, default_filter)
                new_image = apply_filter(new_image, filter_)
                print(f"Étape {i}: Après filtre ({filter_}) : {new_image.size}")

                # Appliquer le redimensionnement
                width_factor = get_value_with_default(ws, i, default_width_percentage)
                print(f"Facteur de redimensionnement: {width_factor}%")
                # Calcul de la nouvelle largeur en pourcentage du template
                new_width = int((width_factor / 100) * current_template.width)
                print(f"Nouvelle largeur calculée: {new_width}px (template width: {current_template.width}px)")
                # Calcul de la nouvelle hauteur en conservant le ratio
                aspect_ratio = new_image.width / new_image.height
                new_height = int(new_width / aspect_ratio)
                print(f"Nouvelle hauteur calculée: {new_height}px (ratio: {aspect_ratio})")

                # Vérification que les dimensions sont valides
                if new_width <= 0 or new_height <= 0:
                    raise ValueError(f"Dimensions invalides à l'étape {i} : width={new_width}, height={new_height}")

                # Redimensionnement de l'image
                new_image = new_image.resize((new_width, new_height))
                print(f"Étape {i}: Après redimensionnement : {new_image.size}")

                # Appliquer le filigrane
                if watermark_text:
                    new_image = apply_watermark(new_image, watermark_text)
                    print(f"Étape {i}: Filigrane appliqué")

                # Positionner l'image sur le template
                x = int(get_value_with_default(xs, i, 0) / 100 * current_template.width)
                y = int(get_value_with_default(ys, i, 0) / 100 * current_template.height)
                current_template.paste(new_image, (x, y))
                print(f"Étape {i}: Image collée aux coordonnées ({x}, {y})")

            except Exception as e:
                log_message = f"Erreur à l'étape {i} : {e}"
                log_to_ftp(ftp_host, ftp_username, ftp_password, log_message, log_folder="/error_logs")
                raise e

        # Ajouter du texte
        for i in range(len(ts)):
            try:
                text = get_value_with_default(ts, i, "")
                font_name = get_value_with_default(tfs, i, "arial")
                color = get_value_with_default(tcs, i, "000000")
                font_size = get_value_with_default(tts, i, 20)
                tx = get_value_with_default(txs, i, 0)
                ty = get_value_with_default(tys, i, 0)

                if text:  # Ajouter uniquement si du texte est défini
                    current_template = add_text(
                        img=current_template,
                        text=text,
                        font_name=font_name,
                        color=color,
                        font_size=font_size,
                        x=tx,
                        y=ty
                    )
                    print(f"Étape texte {i}: Texte ajouté ({text})")
            except Exception as e:
                log_message = f"Erreur ajout texte à l'étape {i} : {e}"
                log_to_ftp(ftp_host, ftp_username, ftp_password, log_message, log_folder="/error_logs")
                raise e

        # Sauvegarder et uploader le fichier
        if result_file:
            if os.path.dirname(result_file):
                os.makedirs(os.path.dirname(result_file), exist_ok=True)
            
            current_template.save(result_file, dpi=(dpi, dpi))
            upload_file_ftp(result_file, ftp_host, ftp_username, ftp_password, result_file)
            print(f"Fichier enregistré et uploadé : {result_file}")

    except Exception as e:
        log_message = f"Erreur générale : {str(e)}"
        print(log_message)
        log_to_ftp(ftp_host, ftp_username, ftp_password, log_message, log_folder="/error_logs")

    finally:
        if result_file and os.path.exists(result_file):
            clean_up_files([result_file])
