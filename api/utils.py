import pytz
from datetime import datetime
import os
from ftplib import FTP
from fastapi import FastAPI, HTTPException, Query, Request
from starlette.responses import JSONResponse
from tempfile import NamedTemporaryFile
import subprocess
import requests
from typing import Optional, List
from PIL import Image, ImageOps, ImageDraw, ImageFont
from io import BytesIO
import httpx

def log_request_to_ftp(params: dict, ftp_host: str, ftp_username: str, ftp_password: str, log_folder: str = "/logs"):
    """
    Enregistre les paramètres de la requête dans un fichier texte et téléverse sur le serveur FTP.

    Args:
    - params (dict): Dictionnaire des paramètres de la requête.
    - ftp_host (str): L'hôte du serveur FTP.
    - ftp_username (str): Le nom d'utilisateur pour se connecter au serveur FTP.
    - ftp_password (str): Le mot de passe pour se connecter au serveur FTP.
    - log_folder (str): Le dossier sur le serveur FTP où le fichier de log sera enregistré.
    """
    log_message = f"Request received at {datetime.now().isoformat()} with parameters: {params}\n"
    
    # Crée un nom de fichier basé sur la date et l'heure actuelle
    tz = pytz.timezone('Europe/Paris')
    now = datetime.now(tz)
    log_filename = f"request_log_{now.strftime('%Y%m%d_%H%M%S')}.txt"
    log_file_path = os.path.join(log_folder, log_filename).replace('\\', '/')
    
    print(f"Creating log file at: {log_file_path}")  # Debugging message

    with NamedTemporaryFile("w", delete=False) as temp_log_file:
        temp_log_file.write(log_message)
        temp_log_path = temp_log_file.name

    print(f"Temporary log file created at: {temp_log_path}")  # Debugging message

    try:
        with FTP(ftp_host, ftp_username, ftp_password) as ftp:
            ftp.cwd('/')  # Assurez-vous d'être à la racine
            if log_folder != '/':  # Vérifie si le dossier de logs n'est pas la racine
                ensure_ftp_path(ftp, log_folder)
                print(f"Ensured FTP path: {log_folder}")  # Debugging message
            
            # Construire le chemin complet du fichier sur le serveur FTP
            complete_path = os.path.join(log_folder, log_filename).replace('\\', '/')
            print(f"Complete path on FTP: {complete_path}")  # Debugging message

            with open(temp_log_path, 'rb') as file:
                ftp.storbinary(f'STOR {complete_path}', file)
                print(f"Log file uploaded to FTP: {complete_path}")  # Debugging message

    except Exception as e:
        print(f"Erreur lors du téléversement du log sur FTP : {e}")

    finally:
        os.remove(temp_log_path)  # Nettoyage du fichier temporaire
        print(f"Temporary log file removed: {temp_log_path}")  # Debugging message


def log_to_ftp(ftp_host: str, ftp_username: str, ftp_password: str, log_message: str, log_folder: str = "error_logs"):
    """
    Enregistre un message de log dans un dossier spécifié sur un serveur FTP.

    Args:
    - ftp_host (str): L'hôte du serveur FTP.
    - ftp_username (str): Le nom d'utilisateur pour se connecter au serveur FTP.
    - ftp_password (str): Le mot de passe pour se connecter au serveur FTP.
    - log_message (str): Le message à enregistrer dans le fichier de log.
    - log_folder (str): Le dossier sur le serveur FTP où le fichier de log sera enregistré.
    """

    # Crée un nom de fichier basé sur la date et l'heure actuelle
    tz = pytz.timezone('Europe/Paris')

    now = datetime.now(tz)

    log_filename = f"error_log_{now.strftime('%Y%m%d_%H%M%S')}.txt"
    log_file_path = os.path.join(log_folder, log_filename).replace('\\', '/')
    
    print(f"Tentative de log FTP dans : {log_file_path}")  # Débogage
    
    with NamedTemporaryFile("w", delete=False) as temp_log_file:
        temp_log_file.write(log_message)
        temp_log_path = temp_log_file.name

    try:
        with FTP(ftp_host, ftp_username, ftp_password) as ftp:
            ftp.cwd('/')  # Assurez-vous d'être à la racine
            if log_folder != '/':  # Vérifie si le dossier de logs n'est pas la racine
                ensure_ftp_path(ftp, log_folder)
            with open(temp_log_path, 'rb') as file:
                ftp.storbinary(f'STOR {log_file_path}', file)
    except Exception as e:
        print(f"Erreur lors du téléversement du log sur FTP : {e}")
    finally:
        os.remove(temp_log_path)  # Nettoyage du fichier temporaire


def ensure_ftp_path(ftp, path):
    """
    Crée récursivement le chemin sur le serveur FTP si nécessaire.
    """
    path = path.lstrip('/')  # Supprime le slash initial pour éviter les chemins absolus
    directories = path.split('/')
    
    current_path = ''
    for directory in directories:
        if directory:  # Ignore les chaînes vides
            current_path +=  directory
            try:
                ftp.cwd(current_path)  # Tente de naviguer dans le dossier
                print(f"Navigated to: {current_path}")  # Debugging message
            except Exception:
                ftp.mkd(current_path)  # Crée le dossier s'il n'existe pas
                ftp.cwd(current_path)  # Navigue dans le dossier nouvellement créé
                print(f"Created and navigated to: {current_path}")  # Debugging message


def clean_up_files(file_paths: list):
    """Supprime les fichiers temporaires spécifiés."""
    for path in file_paths:
        if path and os.path.exists(path):
            os.remove(path)

def upload_file_ftp(file_path: str, ftp_host: str, ftp_username: str, ftp_password: str, output_path: str):
    """
    Téléverse un fichier sur un serveur FTP.

    Args:
    - file_path (str): Le chemin local du fichier à téléverser.
    - ftp_host (str): L'hôte du serveur FTP.
    - ftp_username (str): Le nom d'utilisateur pour se connecter au serveur FTP.
    - ftp_password (str): Le mot de passe pour se connecter au serveur FTP.
    - output_path (str): Le chemin complet sur le serveur FTP où le fichier doit être téléversé.

    Cette fonction assure que le chemin de destination existe sur le serveur FTP
    et téléverse le fichier spécifié à cet emplacement.
    """
    with FTP(ftp_host, ftp_username, ftp_password) as ftp:
        # Assure que le chemin du dossier existe sur le serveur FTP
        directory_path, filename = os.path.split(output_path)
        ensure_ftp_path(ftp, directory_path)
        
        # Construit le chemin complet du fichier sur le serveur FTP
        ftp.cwd('/')  # S'assure de partir de la racine
        complete_path = os.path.join(directory_path, filename).lstrip('/')
        
        # Téléverse le fichier
        with open(file_path, 'rb') as file:
            ftp.storbinary(f'STOR {complete_path}', file)


def load_image(image_url: str) -> Image:
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    return img

def apply_rotation(img: Image, rotation: int) -> Image:
    return img.rotate(rotation, expand=True, fillcolor=None)

def apply_crop(img: Image, dh: int, db: int) -> Image:
    width, height = img.size
    top = (dh / 100) * height
    bottom = height - (db / 100) * height
    return img.crop((0, top, width, bottom))

def apply_filter(img: Image, filter: str) -> Image:
    if filter == 'NB':
        return ImageOps.grayscale(img)
    else:
        return img

def add_text(
    img: Image = Image.new('RGB', (100, 100)), 
    text: str = "Sample Text", 
    font_name: str = "arial",  # Path to Arial font
    font_size: int = 20, 
    x: int = 10, 
    y: int = 10, 
    color: str = "black",
    align: Optional[str] = "left"
) -> Image:
    
    font_path = ''
    if font_name == "arial":
        font_path = "/usr/share/fonts/arial.ttf"
    elif font_name == "tnr":
        font_path = "/usr/share/fonts/TimesNewRoman.ttf"
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        print("Font not found. Using default font.")
        font = ImageFont.load_default()

    draw = ImageDraw.Draw(img)

    # _, text_height = draw.textsize(text, font=font)
    _, heigth = img.size

    y = heigth - y - font_size
    if color == "black":
        color = (255, 255, 255)
    else:
        color = (0, 0, 0)

    x = (x / 100) * img.width
    y = img.height - ((y / 100) * img.height)

    draw.text((x, y), text, font=font, fill=color, align=align)
    
    return img

def process_and_upload(template_url, image_url, result_file, xs, ys, rs, ws, cs, dhs, dbs, ts, tfs, tcs, tts, txs, tys, ftp_host, ftp_username, ftp_password, params):
    """
    A function to download data, process it, and upload it to a server.
    """
    log_request_to_ftp(params, ftp_host, ftp_username, ftp_password)

    try:
        template = load_image(template_url)
        image = load_image(image_url)
        
        default_rotation = rs[0] if rs else 0
        default_width = ws[0] if ws else 100
        default_filter = cs[0] if cs else 'none'
        default_dh = dhs[0] if dhs else 0
        default_db = dbs[0] if dbs else 0

        # Transformation de l'image principale
        for i, _ in enumerate(xs):
            try:
                rotation = rs[i] if i < len(rs) else default_rotation
                new_image = apply_rotation(image, rotation)
                
                top = dhs[i] if i < len(dhs) else default_dh
                bottom = dbs[i] if i < len(dbs) else default_db
                new_image = apply_crop(new_image, top, bottom)
                
                filter_ = cs[i] if i < len(cs) else default_filter
                new_image = apply_filter(new_image, filter_)
                
                new_width = int((ws[i] / 100) * new_image.width) if i < len(ws) else int((default_width / 100) * new_image.width)
                new_height = int(new_width * new_image.height / new_image.width)
                new_image = new_image.resize((new_width, new_height))

                x = int(xs[i] / 100 * template.width) if i < len(xs) else 0
                y = int(template.height - (ys[i] / 100 * template.height) - new_image.height) if i < len(ys) else 0
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
                font_name = tfs[i] if i < len(tfs) else 'arial'
                color = tcs[i] if i < len(tcs) else 'black'
                font_size = tts[i] if i < len(tts) else 10
                tx = txs[i] if i < len(txs) else 0
                ty = tys[i] if i < len(tys) else 0

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

        if result_file:
            if os.path.dirname(result_file):
                os.makedirs(os.path.dirname(result_file), exist_ok=True)
            template.save(result_file)
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