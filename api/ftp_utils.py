import pytz
from datetime import datetime
import os
from ftplib import FTP
from tempfile import NamedTemporaryFile
import os
import logging
from queue import Queue
import threading
from typing import List, Dict
import json
from dataclasses import dataclass
from time import time
from io import BytesIO

# Configuration du logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

@dataclass
class LogEntry:
    timestamp: float
    message: str
    level: str
    metadata: Dict

class LogBuffer:
    _instance = None
    BUFFER_SIZE = 50  # Nombre de logs avant écriture
    FLUSH_INTERVAL = 60  # Intervalle en secondes

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LogBuffer, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.buffer: List[LogEntry] = []
        self.lock = threading.Lock()
        self.last_flush = time()
        self._start_flush_timer()

    def _start_flush_timer(self):
        def flush_timer():
            while True:
                if time() - self.last_flush >= self.FLUSH_INTERVAL:
                    self.flush()
                threading.Event().wait(10)  # Check toutes les 10 secondes

        thread = threading.Thread(target=flush_timer, daemon=True)
        thread.start()

    def add_log(self, message: str, level: str = "INFO", metadata: Dict = None):
        log_entry = LogEntry(
            timestamp=time(),
            message=message,
            level=level,
            metadata=metadata or {}
        )
        
        with self.lock:
            self.buffer.append(log_entry)
            if len(self.buffer) >= self.BUFFER_SIZE:
                self.flush()

    def flush(self):
        with self.lock:
            if not self.buffer:
                return
            
            current_buffer = self.buffer
            self.buffer = []
            self.last_flush = time()
            
            return current_buffer

def write_logs_to_ftp(logs: List[LogEntry], ftp_host: str, ftp_username: str, ftp_password: str, log_folder: str):
    """Écrit un groupe de logs dans un seul fichier sur le FTP."""
    if not logs:
        return

    logger.info(f"Tentative d'écriture des logs dans le dossier: {log_folder}")
    
    # Créer un seul fichier pour tous les logs
    tz = pytz.timezone('Europe/Paris')
    now = datetime.now(tz)
    log_filename = f"batch_log_{now.strftime('%Y%m%d_%H%M%S')}.jsonl"
    logger.info(f"Nom du fichier de log: {log_filename}")
    
    with BytesIO() as bio:
        # Écrire tous les logs dans le buffer
        for log in logs:
            log_line = {
                "timestamp": log.timestamp,
                "message": log.message,
                "level": log.level,
                "metadata": log.metadata
            }
            bio.write(json.dumps(log_line).encode('utf-8') + b'\n')
        
        bio.seek(0)
        
        try:
            # Upload en une seule connexion FTP
            with FTP(ftp_host, ftp_username, ftp_password) as ftp:
                logger.info("Connexion FTP établie pour les logs")
                ftp.cwd('/')
                if log_folder != '/':
                    logger.info(f"Navigation vers le dossier de logs: {log_folder}")
                    ensure_ftp_path(ftp, log_folder, create_dirs=False)
                full_path = os.path.join(log_folder, log_filename)
                logger.info(f"Tentative d'upload du fichier de log: {full_path}")
                ftp.storbinary(f'STOR {full_path}', bio)
                logger.info("Upload des logs terminé avec succès")
        except Exception as e:
            logger.error(f"Erreur lors de l'upload des logs: {type(e).__name__}: {str(e)}")
            raise

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


def ensure_ftp_path(ftp, path, create_dirs=False):
    """
    Navigue vers le chemin spécifié sur le serveur FTP.
    Le chemin peut être absolu ou relatif.
    Args:
        ftp: Instance FTP
        path: Chemin à naviguer
        create_dirs: Si True, crée les dossiers s'ils n'existent pas. Par défaut False.
    """
    logger.info(f"Tentative de navigation FTP vers: {path} (create_dirs={create_dirs})")
    
    if not path:
        logger.debug("Chemin vide, retour immédiat")
        return
        
    try:
        current_dir = ftp.pwd()
        logger.info(f"Répertoire FTP actuel: {current_dir}")
    except Exception as e:
        logger.error(f"Impossible d'obtenir le répertoire courant: {str(e)}")
        
    if path.startswith('/'):
        logger.debug("Chemin absolu détecté, retour à la racine")
        ftp.cwd('/')
        path = path[1:]
    
    directories = path.split('/')
    logger.info(f"Navigation dans l'arborescence: {directories}")
    
    for directory in directories:
        if directory:
            try:
                logger.debug(f"Tentative d'accès au dossier: {directory}")
                ftp.cwd(directory)
                logger.info(f"Navigation réussie vers: {directory}")
            except Exception as e:
                if create_dirs:
                    try:
                        logger.info(f"Dossier {directory} non trouvé, tentative de création")
                        ftp.mkd(directory)
                        ftp.cwd(directory)
                        logger.info(f"Dossier {directory} créé et accédé avec succès")
                    except Exception as e:
                        logger.error(f"Échec de la création du dossier {directory}: {str(e)}")
                        logger.error(f"Détails de l'erreur: {type(e).__name__}: {str(e)}")
                        raise
                else:
                    logger.error(f"Le dossier {directory} n'existe pas et create_dirs est False")
                    logger.error(f"Détails de l'erreur: {type(e).__name__}: {str(e)}")
                    raise
    
    try:
        final_dir = ftp.pwd()
        logger.info(f"Navigation terminée. Répertoire final: {final_dir}")
    except Exception as e:
        logger.error(f"Impossible d'obtenir le répertoire final: {str(e)}")

def log_request_to_ftp(params: dict, ftp_host: str, ftp_username: str, ftp_password: str, log_folder: str = "/logs"):
    """Version optimisée utilisant le buffer de logs."""
    log_buffer = LogBuffer()
    log_buffer.add_log(
        message="Request received",
        level="INFO",
        metadata={"params": params, "timestamp": datetime.now().isoformat()}
    )

def log_to_ftp(ftp_host: str, ftp_username: str, ftp_password: str, log_message: str, log_folder: str = "error_logs"):
    """Version optimisée utilisant le buffer de logs."""
    log_buffer = LogBuffer()
    log_buffer.add_log(
        message=log_message,
        level="ERROR",
        metadata={"folder": log_folder}
    )

# Démarrer un thread pour vider périodiquement le buffer
def start_log_flusher(ftp_host: str, ftp_username: str, ftp_password: str):
    def flush_logs():
        log_buffer = LogBuffer()
        while True:
            logs = log_buffer.flush()
            if logs:
                write_logs_to_ftp(logs, ftp_host, ftp_username, ftp_password, "/logs")
            threading.Event().wait(LogBuffer.FLUSH_INTERVAL)

    thread = threading.Thread(target=flush_logs, daemon=True)
    thread.start()

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