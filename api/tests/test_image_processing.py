import pytest
from PIL import Image
from unittest.mock import patch, MagicMock
import numpy as np
from image_processing import process_image
from utils import process_and_upload

def test_image_resize_percentage():
    """Test le redimensionnement d'image avec un pourcentage"""
    # Créer une image test
    source_image = Image.new('RGB', (1000, 1000), color='black')
    
    with patch('image_processing.Image') as mock_pil:
        # Configuration du mock
        mock_pil.open.return_value = source_image
        mock_pil.LANCZOS = Image.LANCZOS
        
        # Appel de la fonction
        result = process_image(
            template_path="mock_template.jpg",
            image_path="mock_image.jpg",
            width_scale=10  # 10% de la largeur originale
        )
        
        # Vérification que l'image a été redimensionnée à 100x100 (10% de 1000x1000)
        assert result.size == (100, 100)

def test_image_quality():
    """Test la qualité de l'image après traitement"""
    source_image = Image.new('RGB', (1000, 1000), color='white')
    
    with patch('image_processing.Image') as mock_pil:
        mock_pil.open.return_value = source_image
        mock_pil.LANCZOS = Image.LANCZOS
        
        result = process_image(
            template_path="mock_template.jpg",
            image_path="mock_image.jpg",
            width_scale=100  # pas de redimensionnement
        )
        
        # Vérification basique de la qualité
        assert result.mode == 'RGB'
        assert result.size == (1000, 1000)

def create_test_image(width, height, color='white'):
    """Crée une image test avec les dimensions spécifiées."""
    return Image.new('RGB', (width, height), color=color)

def test_proportions_maintenues():
    """Test que les proportions sont maintenues lors du redimensionnement."""
    
    with patch('photo_utils.load_image') as mock_load_image, \
         patch('PIL.Image.Image.paste') as mock_paste, \
         patch('utils.upload_file_ftp') as mock_upload, \
         patch('utils.log_request_to_ftp') as mock_log_request, \
         patch('utils.log_to_ftp') as mock_log:
        
        # Créer un template 1000x1000 et une image source 200x100
        template = create_test_image(1000, 1000)
        source_image = create_test_image(200, 100, 'black')
        
        # Configuration des mocks
        mock_load_image.side_effect = [template, [source_image]]
        
        # Tester avec result_w = 2000 (double de la référence)
        process_and_upload(
            template_url="mock_template.jpg",
            image_url=["mock_image.jpg"],
            result_file="result.jpg",
            result_w=2000,  # Double de la référence
            xs=[10],  # 10% de la largeur
            ys=[20],  # 20% de la hauteur
            rs=[0],
            ws=[30],  # 30% de la largeur du template
            cs=['none'],
            dhs=[0],
            dbs=[0],
            ts=["Test"],
            tfs=["arial"],
            tcs=["000000"],
            tts=[24],  # Taille de police de base
            txs=[40],
            tys=[50],
            ftp_host="mock_host",
            ftp_username="mock_user",
            ftp_password="mock_pass",
            dpi=300,
            params={},
            watermark_text=None
        )
        
        # Vérifier que paste a été appelé avec les bonnes coordonnées
        paste_calls = mock_paste.call_args_list
        assert len(paste_calls) == 1, "paste devrait être appelé une fois"
        
        # Vérifier les coordonnées de collage (doivent être doublées)
        _, call_kwargs = paste_calls[0]
        x, y = call_kwargs.get('box', (0, 0))
        assert x == 200, "La position x devrait être 10% de 2000"
        assert y == 400, "La position y devrait être 20% de 2000"

def test_taille_texte_adaptee():
    """Test que la taille du texte s'adapte correctement."""
    
    with patch('photo_utils.load_image') as mock_load_image, \
         patch('photo_utils.add_text') as mock_add_text, \
         patch('utils.upload_file_ftp') as mock_upload, \
         patch('utils.log_request_to_ftp') as mock_log_request, \
         patch('utils.log_to_ftp') as mock_log:
        
        # Créer un template et configurer les mocks
        template = create_test_image(1000, 1000)
        mock_load_image.side_effect = [template, []]
        
        # Test avec différentes tailles de sortie
        test_sizes = [500, 1000, 2000]  # Moitié, référence, double
        base_font_size = 24
        
        for result_w in test_sizes:
            process_and_upload(
                template_url="mock_template.jpg",
                image_url=[],
                result_file="result.jpg",
                result_w=result_w,
                xs=[],
                ys=[],
                rs=[],
                ws=[],
                cs=[],
                dhs=[],
                dbs=[],
                ts=["Test"],
                tfs=["arial"],
                tcs=["000000"],
                tts=[base_font_size],
                txs=[50],
                tys=[50],
                ftp_host="mock_host",
                ftp_username="mock_user",
                ftp_password="mock_pass",
                dpi=300,
                params={},
                watermark_text=None
            )
            
            # Vérifier que add_text a été appelé avec la bonne taille de police
            expected_font_size = int(base_font_size * (result_w / 1000))
            actual_font_size = mock_add_text.call_args[1]['font_size']
            assert actual_font_size == expected_font_size, \
                f"La taille de police devrait être {expected_font_size} pour result_w={result_w}"

def test_dimensions_image_adaptees():
    """Test que les dimensions des images s'adaptent correctement."""
    
    with patch('photo_utils.load_image') as mock_load_image, \
         patch('PIL.Image.Image.resize') as mock_resize, \
         patch('PIL.Image.Image.paste') as mock_paste, \
         patch('utils.upload_file_ftp') as mock_upload, \
         patch('utils.log_request_to_ftp') as mock_log_request, \
         patch('utils.log_to_ftp') as mock_log:
        
        # Créer des images test
        template = create_test_image(1000, 1000)
        source_image = create_test_image(200, 100)  # Ratio 2:1
        mock_load_image.side_effect = [template, [source_image]]
        
        # Test avec un template de 2000px de large
        process_and_upload(
            template_url="mock_template.jpg",
            image_url=["mock_image.jpg"],
            result_file="result.jpg",
            result_w=2000,
            xs=[0],
            ys=[0],
            rs=[0],
            ws=[50],  # 50% de la largeur du template
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
        
        # Vérifier les dimensions du redimensionnement
        resize_calls = mock_resize.call_args_list
        assert len(resize_calls) == 1, "resize devrait être appelé une fois"
        
        # La largeur devrait être 50% de 2000 = 1000
        # La hauteur devrait maintenir le ratio 2:1
        resize_size = resize_calls[0][0][0]
        assert resize_size[0] == 1000, "La largeur devrait être 1000 (50% de 2000)"
        assert resize_size[1] == 500, "La hauteur devrait maintenir le ratio 2:1"

def test_parametres_inchanges():
    """Test que certains paramètres restent inchangés lors du redimensionnement."""
    
    with patch('photo_utils.load_image') as mock_load_image, \
         patch('photo_utils.apply_rotation') as mock_rotate, \
         patch('photo_utils.apply_crop') as mock_crop, \
         patch('utils.upload_file_ftp') as mock_upload, \
         patch('utils.log_request_to_ftp') as mock_log_request, \
         patch('utils.log_to_ftp') as mock_log:
        
        # Créer des images test
        template = create_test_image(1000, 1000)
        source_image = create_test_image(200, 200)
        mock_load_image.side_effect = [template, [source_image]]
        
        # Paramètres de test
        rotation_angle = 45
        crop_top = 10
        crop_bottom = 20
        
        process_and_upload(
            template_url="mock_template.jpg",
            image_url=["mock_image.jpg"],
            result_file="result.jpg",
            result_w=2000,  # Double de la taille
            xs=[0],
            ys=[0],
            rs=[rotation_angle],
            ws=[50],
            cs=['none'],
            dhs=[crop_top],
            dbs=[crop_bottom],
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
        
        # Vérifier que la rotation est inchangée
        mock_rotate.assert_called_once()
        assert mock_rotate.call_args[0][1] == rotation_angle, \
            "L'angle de rotation ne devrait pas changer"
        
        # Vérifier que les paramètres de rognage sont inchangés
        mock_crop.assert_called_once()
        assert mock_crop.call_args[0][1] == crop_top, \
            "Le pourcentage de rognage supérieur ne devrait pas changer"
        assert mock_crop.call_args[0][2] == crop_bottom, \
            "Le pourcentage de rognage inférieur ne devrait pas changer" 