from PIL import Image
import pytest
from utils import process_and_upload
from unittest.mock import MagicMock, patch

def test_image_resize_percentage():
    """Test le redimensionnement d'une image en pourcentage du template."""
    
    # Mock pour load_image
    with patch('photo_utils.load_image') as mock_load_image, \
         patch('PIL.Image.Image.resize') as mock_resize, \
         patch('PIL.Image.Image.paste') as mock_paste, \
         patch('utils.upload_file_ftp') as mock_upload, \
         patch('utils.log_request_to_ftp') as mock_log_request, \
         patch('utils.log_to_ftp') as mock_log:
        
        # Configurer les mocks
        template = Image.new('RGB', (500, 500), color='white')
        source_image = Image.new('RGB', (1000, 1000), color='black')
        mock_load_image.side_effect = [template, source_image]
        mock_resize.return_value = Image.new('RGB', (50, 50), color='black')
        
        # Appeler process_and_upload avec w1=10%
        process_and_upload(
            template_url="https://example.com/mock_template.jpg",
            image_url=["https://example.com/mock_image.jpg"],
            result_file="result.jpg",
            result_w=None,
            xs=[0],
            ys=[0],
            rs=[0],
            ws=[10],
            cs=['none'],
            dhs=[0],
            dbs=[0],
            ts=[],
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
        
        # Vérifier que les mocks ont été appelés correctement
        assert mock_load_image.call_count == 2, "load_image devrait être appelé deux fois"
        assert mock_resize.called, "resize devrait être appelé"
        assert mock_paste.called, "paste devrait être appelé"
        assert mock_upload.called, "upload_file_ftp devrait être appelé" 