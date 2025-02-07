from PIL import Image
import pytest
from utils import process_and_upload
from unittest.mock import MagicMock, patch

def test_image_resize_percentage():
    """Test le redimensionnement d'une image en pourcentage du template."""
    
    # Créer un template 500x500
    template = Image.new('RGB', (500, 500), color='white')
    
    # Créer une image source 1000x1000
    source_image = Image.new('RGB', (1000, 1000), color='black')
    
    # Mock pour la fonction resize
    original_resize = Image.resize
    resize_dimensions = []
    
    def mock_resize(self, size, *args, **kwargs):
        resize_dimensions.append(size)
        return original_resize(self, size, *args, **kwargs)
    
    Image.resize = mock_resize
    
    try:
        # Mock pour load_image
        with patch('photo_utils.load_image') as mock_load_image:
            mock_load_image.side_effect = [template, source_image]
            
            # Mock pour les fonctions FTP
            with patch('utils.upload_file_ftp'), \
                 patch('utils.log_request_to_ftp'), \
                 patch('utils.log_to_ftp'):
                
                # Appeler process_and_upload avec w1=10%
                process_and_upload(
                    template_url="mock_template.jpg",
                    image_url="mock_image.jpg",
                    result_file="result.jpg",
                    result_w=None,  # Pas de redimensionnement du template
                    xs=[0],  # Position x
                    ys=[0],  # Position y
                    rs=[0],  # Pas de rotation
                    ws=[10],  # 10% de la largeur du template
                    cs=['none'],  # Pas de filtre
                    dhs=[0],  # Pas de rognage haut
                    dbs=[0],  # Pas de rognage bas
                    ts=[],  # Pas de texte
                    tfs=[],
                    tcs=[],
                    tts=[],
                    txs=[],
                    tys=[],
                    ftp_host="mock_host",
                    ftp_username="mock_user",
                    ftp_password="mock_pass",
                    dpi=300,
                    params={},
                    watermark_text=None
                )
                
                # Vérifier les dimensions du dernier redimensionnement
                assert any(dim == (50, 50) for dim in resize_dimensions), \
                    "L'image doit être redimensionnée à 50x50 (10% de 500x500)"
    
    finally:
        # Restaurer la fonction resize originale
        Image.resize = original_resize 