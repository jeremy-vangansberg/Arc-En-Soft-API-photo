import pytz
from datetime import datetime
import os
from ftplib import FTP
from tempfile import NamedTemporaryFile
import os
import logging

# Configuration du logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def ftp_security(ftp__id):
    """
    Récupère les informations de sécurité FTP pour un identifiant donné.

    Args:
        ftp__id (int): Identifiant FTP (1 pour le moment).

    Returns:
        tuple: FTP_HOST, FTP_USERNAME, FTP_PASSWORD
    """
    logger.info(f"Fetching FTP credentials for FTP ID: {ftp__id}")
    
    try:
        if ftp__id == 1:
            FTP_HOST = os.getenv("FTP_HOST_1")
            FTP_USERNAME = os.getenv("FTP_USERNAME_1")
            FTP_PASSWORD = os.getenv("FTP_PASSWORD_1")
            
            # Vérification des variables d'environnement
            if not FTP_HOST:
                logger.error("FTP_HOST_1 environment variable is missing!")
                raise ValueError("Missing environment variable: FTP_HOST_1")
            if not FTP_USERNAME:
                logger.error("FTP_USERNAME_1 environment variable is missing!")
                raise ValueError("Missing environment variable: FTP_USERNAME_1")
            if not FTP_PASSWORD:
                logger.error("FTP_PASSWORD_1 environment variable is missing!")
                raise ValueError("Missing environment variable: FTP_PASSWORD_1")

            logger.info("FTP credentials successfully retrieved (host and username).")
            return FTP_HOST, FTP_USERNAME, FTP_PASSWORD
        
        else:
            logger.error(f"Unsupported FTP ID: {ftp__id}")
            raise ValueError(f"FTP ID {ftp__id} is not supported.")
    
    except Exception as e:
        logger.exception(f"Error while fetching FTP credentials: {e}")
        raise


def ensure_ftp_path(ftp, path):
    """
    Crée récursivement le chemin sur le serveur FTP si nécessaire.
    """
    path = path.lstrip('/')  # Supprime le slash initial pour éviter les chemins absolus
    directories = path.split('/')
    
    current_path = ''
    for directory in directories:
        if directory:  # Ignore les chaînes vides
            current_path += directory
            try:
                ftp.cwd(current_path)  # Tente de naviguer dans le dossier
                print(f"Navigated to: {current_path}")  # Debugging message
            except Exception:
                ftp.mkd(current_path)  # Crée le dossier s'il n'existe pas
                ftp.cwd(current_path)  # Navigue dans le dossier nouvellement créé
                print(f"Created and navigated to: {current_path}")  # Debugging message
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