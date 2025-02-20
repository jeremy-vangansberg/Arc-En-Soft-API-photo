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

    # Créer un seul fichier pour tous les logs
    tz = pytz.timezone('Europe/Paris')
    now = datetime.now(tz)
    log_filename = f"batch_log_{now.strftime('%Y%m%d_%H%M%S')}.jsonl"
    
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
        
        # Upload en une seule connexion FTP
        with FTP(ftp_host, ftp_username, ftp_password) as ftp:
            ftp.cwd('/')
            if log_folder != '/':
                ensure_ftp_path(ftp, log_folder)
            ftp.storbinary(f'STOR {os.path.join(log_folder, log_filename)}', bio)

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
    Navigue vers le chemin spécifié sur le serveur FTP.
    Le chemin peut être absolu ou relatif.
    Les dossiers doivent exister au préalable.
    """
    # Gestion des chemins absolus et relatifs
    if path.startswith('/'):
        # Pour un chemin absolu, on commence par la racine
        ftp.cwd('/')
        # On retire le premier slash pour le split
        path = path[1:]
    
    # Navigation dans l'arborescence
    directories = path.split('/')
    for directory in directories:
        if directory:  # Ignore les chaînes vides
            try:
                ftp.cwd(directory)
                logger.debug(f"Navigated to: {directory}")
            except Exception as e:
                logger.error(f"Failed to navigate to directory {directory}: {str(e)}")
                raise

                
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