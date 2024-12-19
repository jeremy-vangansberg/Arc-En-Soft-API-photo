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
    A function to download data, process it, and upload it to a server.
    """
    log_request_to_ftp(params, ftp_host, ftp_username, ftp_password)

    try:
        template = load_image(template_url)
        image = load_image(image_url)
        
        default_rotation = 0
        default_width = 100
        default_filter = 'none'
        default_dh = 0
        default_db = 0

        # Transformation de l'image principale
        for i, _ in enumerate(xs):
            try:
                
                top = dhs[i] if i < len(dhs) else default_dh
                bottom = dbs[i] if i < len(dbs) else default_db
                new_image = apply_crop(image, top, bottom)

                rotation = rs[i] if i < len(rs) else default_rotation
                new_image = apply_rotation(new_image, rotation)
                
                filter_ = cs[i] if i < len(cs) else default_filter
                print(f"Étape {i}: Filtre appliqué : {filter_}, Type avant filtre : {type(new_image)}")
                new_image = apply_filter(new_image, filter_)
                print(f"Étape {i}: Type après filtre : {type(new_image)}")
                
                new_width = int((ws[i] / 100) * new_image.width) if i < len(ws) else int((default_width / 100) * new_image.width)
                new_height = int(new_width * new_image.height / new_image.width)
                if new_width <= 0 or new_height <= 0:
                    raise ValueError(f"Invalid dimensions for the image at step {i}: width={new_width}, height={new_height}")

                new_image = new_image.resize((new_width, new_height))

                # Appliquer le filigrane
                if watermark_text:
                    new_image = apply_watermark(new_image, watermark_text)

                x = int(xs[i] / 100 * template.width) if i < len(xs) else 0
                y = int(ys[i] / 100 * template.height) if i < len(ys) else 0
                template.paste(new_image, (x, y))
                
            except ValueError as e:
                log_message = f"Error at step {i}: {e}"
                log_to_ftp(
                    ftp_host=ftp_host,
                    ftp_username=ftp_username,
                    ftp_password=ftp_password,
                    log_message=log_message,
                    log_folder="/error_logs")

        # Ajout de texte
        for i, _ in enumerate(ts):
            try:
                text = ts[i]
                font_name = tfs[i] 
                color = tcs[i] 
                font_size = tts[i] 
                tx = txs[i]
                ty = tys[i]

                # Utilisation de la fonction add_text mise à jour
                template = add_text(img=template, text=text, font_name=font_name, color=color, font_size=font_size, x=tx, y=ty)
            
            except ValueError as e:
                log_message = f"Error adding text at step {i}: {e}"
                log_to_ftp(
                    ftp_host=ftp_host,
                    ftp_username=ftp_username,
                    ftp_password=ftp_password,
                    log_message=log_message,
                    log_folder="/error_logs")
        

        
        #resize img
        if result_w : 
            template = apply_resize_template(template, result_w)

        if result_file:
            if os.path.dirname(result_file):
                os.makedirs(os.path.dirname(result_file), exist_ok=True)
            
            template.save(result_file, dpi=(dpi, dpi))
            upload_file_ftp(result_file, ftp_host, ftp_username, ftp_password, result_file)
    
    except Exception as e:
        log_message = f"General error during processing: {str(e)}"
        print(log_message)
        log_to_ftp(
                    ftp_host=ftp_host,
                    ftp_username=ftp_username,
                    ftp_password=ftp_password,
                    log_message=log_message,
                    log_folder="/error_logs")
    
    finally:
        if result_file and os.path.exists(result_file):
            clean_up_files([result_file])
