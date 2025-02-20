import logging
import sys

def configure_logging():
    """Configure le logging pour l'application"""
    # Configuration de base
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

    # Réduire la verbosité des logs externes
    logging.getLogger('PIL').setLevel(logging.WARNING)
    logging.getLogger('celery').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)

    # Créer le logger pour notre application
    logger = logging.getLogger('photo_arc')
    logger.setLevel(logging.INFO)

    return logger 