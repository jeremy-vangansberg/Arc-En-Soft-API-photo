import pytest
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from photo_utils import TextRenderer, TextConfig, TextRenderStrategy, add_text
from unittest.mock import patch

def test_text_size_consistency():
    """Vérifie que la taille du texte est cohérente après le rendu haute résolution."""
    img = Image.new('RGB', (400, 200), 'white')
    text = "Test"
    font_size = 24
    
    # Appliquer le texte avec différentes stratégies
    basic = add_text(img.copy(), text, font_size=font_size, strategy=TextRenderStrategy.BASIC)
    high_res = add_text(img.copy(), text, font_size=font_size, strategy=TextRenderStrategy.HIGH_RES)
    
    # Vérifier que les deux images ont la même taille
    assert basic.size == high_res.size, "Les dimensions des images devraient être identiques"

def test_text_position():
    """Vérifie que la position du texte est correcte."""
    img = Image.new('RGB', (400, 200), 'white')
    text = "Test"
    x, y = 50, 50  # Position en pourcentage
    
    result = add_text(img, text, x=x, y=y)
    
    # Vérifier que l'image a été modifiée (n'est plus entièrement blanche)
    result_array = np.array(result)
    assert not np.all(result_array == 255), "Le texte devrait être visible sur l'image"

def test_text_quality_metrics():
    """Vérifie la qualité du rendu du texte."""
    img = Image.new('RGB', (400, 200), 'white')
    text = "Quality Test"  # Texte plus long pour une meilleure mesure
    font_size = 48  # Taille plus grande pour une meilleure détection
    
    # Rendre le texte avec différentes stratégies
    basic = add_text(img.copy(), text, font_size=font_size, strategy=TextRenderStrategy.BASIC)
    high_res = add_text(img.copy(), text, font_size=font_size, strategy=TextRenderStrategy.HIGH_RES)
    
    # Convertir en array numpy et normaliser
    basic_array = np.array(basic).astype(float) / 255.0
    high_res_array = np.array(high_res).astype(float) / 255.0
    
    # Trouver les zones de texte avec un seuil plus strict
    text_mask = np.any(high_res_array < 0.5, axis=2)  # Seuil plus strict pour le texte
    
    if np.sum(text_mask) > 0:  # Vérifier qu'il y a du texte détecté
        # Calculer les gradients dans les zones de texte uniquement
        basic_edges = np.gradient(basic_array.mean(axis=2))
        high_res_edges = np.gradient(high_res_array.mean(axis=2))
        
        basic_edge_strength = np.mean(np.abs(basic_edges[0][text_mask]) + np.abs(basic_edges[1][text_mask]))
        high_res_edge_strength = np.mean(np.abs(high_res_edges[0][text_mask]) + np.abs(high_res_edges[1][text_mask]))
        
        assert high_res_edge_strength > basic_edge_strength, "Le rendu haute résolution devrait avoir des bords plus nets"

def test_multiline_text():
    """Vérifie le rendu du texte multiligne."""
    img = Image.new('RGB', (400, 200), 'white')
    text = "Ligne 1<br>Ligne 2"
    font_size = 48  # Taille plus grande pour une meilleure détection
    
    result = add_text(img, text, font_size=font_size, strategy=TextRenderStrategy.HIGH_RES)
    result_array = np.array(result)
    
    # Trouver les zones de texte avec un seuil plus strict
    text_pixels = np.any(result_array < 128, axis=2)  # Seuil plus strict pour le texte
    text_rows = np.sum(text_pixels, axis=1)
    
    # Trouver les lignes distinctes avec un seuil minimum
    min_pixels_per_line = 10  # Nombre minimum de pixels pour considérer une ligne
    gaps = np.where(text_rows < min_pixels_per_line)[0]
    
    # Trouver les groupes de lignes séparés par des gaps
    lines = []
    current_line = []
    
    for i in range(len(text_rows)):
        if text_rows[i] >= min_pixels_per_line:
            current_line.append(i)
        elif current_line:
            lines.append(current_line)
            current_line = []
    
    if current_line:
        lines.append(current_line)
    
    # Il devrait y avoir au moins 2 groupes de lignes
    assert len(lines) >= 2, "Le texte multiligne devrait avoir au moins deux lignes distinctes"
    
    # Vérifier l'espacement entre les lignes
    if len(lines) >= 2:
        line1_center = np.mean(lines[0])
        line2_center = np.mean(lines[1])
        line_spacing = abs(line2_center - line1_center)
        assert line_spacing > font_size, "Les lignes devraient être espacées d'au moins la taille de la police"

def test_dpi_scaling():
    """Vérifie que le DPI affecte correctement la taille du texte."""
    img = Image.new('RGB', (400, 200), 'white')
    text = "DPI Test"
    font_size = 48  # Taille plus grande pour une meilleure détection
    
    # Rendre avec différents DPI
    low_dpi = add_text(img.copy(), text, font_size=font_size, dpi=72, strategy=TextRenderStrategy.HIGH_RES)
    high_dpi = add_text(img.copy(), text, font_size=font_size, dpi=300, strategy=TextRenderStrategy.HIGH_RES)
    
    # Convertir en array numpy
    low_dpi_array = np.array(low_dpi)
    high_dpi_array = np.array(high_dpi)
    
    # Trouver les zones de texte avec un seuil plus strict
    low_dpi_text = np.any(low_dpi_array < 128, axis=2)  # Seuil plus strict
    high_dpi_text = np.any(high_dpi_array < 128, axis=2)
    
    # Le texte en haute résolution devrait occuper plus de pixels
    low_dpi_pixels = np.sum(low_dpi_text)
    high_dpi_pixels = np.sum(high_dpi_text)
    
    assert high_dpi_pixels > low_dpi_pixels, "Le texte en haute résolution devrait être plus grand"

def test_parameter_validation():
    """Vérifie que les validations des paramètres fonctionnent correctement."""
    img = Image.new('RGB', (400, 200), 'white')
    
    # Test de validation de l'image
    with pytest.raises(ValueError, match="instance de PIL.Image.Image"):
        add_text("not_an_image", "Test")
    
    # Test de validation des positions
    with pytest.raises(ValueError, match="positions x et y"):
        add_text(img, "Test", x=101)
    with pytest.raises(ValueError, match="positions x et y"):
        add_text(img, "Test", y=-1)
    
    # Test de validation de la taille de police
    with pytest.raises(ValueError, match="taille de la police"):
        add_text(img, "Test", font_size=0)
    with pytest.raises(ValueError, match="taille de la police"):
        add_text(img, "Test", font_size=1001)
    
    # Test de validation de la couleur
    with pytest.raises(ValueError, match="format hexadécimal"):
        add_text(img, "Test", color="GG0000")
    with pytest.raises(ValueError, match="format hexadécimal"):
        add_text(img, "Test", color="12345")  # Trop court 

def test_text_size_scaling():
    """Vérifie que la taille du texte s'adapte correctement à la taille de l'image."""
    # Test avec différentes tailles d'images
    sizes = [(500, 500), (1000, 1000), (2000, 2000)]
    font_size = 36
    text = "Test"
    
    results = []
    for width, height in sizes:
        img = Image.new('RGB', (width, height), 'white')
        result = add_text(
            img=img,
            text=text,
            font_size=font_size,
            x=50,
            y=50,
            color="000000",
            strategy=TextRenderStrategy.COMBINED
        )
        results.append(result)
    
    # Convertir les images en arrays numpy pour analyse
    arrays = [np.array(img) for img in results]
    
    # Trouver les zones de texte dans chaque image
    text_areas = []
    for arr in arrays:
        # Convertir en niveaux de gris et trouver les pixels non blancs
        gray = arr.mean(axis=2)
        text_mask = gray < 250  # Les pixels de texte sont plus sombres
        
        # Trouver les limites du texte
        y_coords, x_coords = np.where(text_mask)
        if len(y_coords) > 0 and len(x_coords) > 0:
            text_height = y_coords.max() - y_coords.min()
            text_width = x_coords.max() - x_coords.min()
            text_areas.append((text_width, text_height))
        else:
            text_areas.append((0, 0))
    
    # Vérifier que les ratios de taille de texte correspondent aux ratios des tailles d'image
    base_width, base_height = text_areas[0]
    for i in range(1, len(sizes)):
        expected_ratio = sizes[i][0] / sizes[0][0]
        actual_ratio_width = text_areas[i][0] / base_width
        actual_ratio_height = text_areas[i][1] / base_height
        
        # Permettre une marge d'erreur de 10%
        assert abs(actual_ratio_width - expected_ratio) < 0.1, \
            f"La largeur du texte ne s'adapte pas correctement. Ratio attendu: {expected_ratio}, obtenu: {actual_ratio_width}"
        assert abs(actual_ratio_height - expected_ratio) < 0.1, \
            f"La hauteur du texte ne s'adapte pas correctement. Ratio attendu: {expected_ratio}, obtenu: {actual_ratio_height}" 

def test_font_fallback():
    """Vérifie que le système de polices de secours fonctionne correctement."""
    img = Image.new('RGB', (400, 200), 'white')
    text = "Test"
    font_size = 36
    
    # Test avec une police inexistante
    result = add_text(
        img=img,
        text=text,
        font_name="police_inexistante",
        font_size=font_size,
        color="000000"
    )
    
    # Vérifier que l'image a été modifiée
    result_array = np.array(result)
    assert not np.all(result_array == 255), "Le texte devrait être visible avec la police de secours"
    
    # Test avec Arial comme police de secours
    with patch('PIL.ImageFont.truetype') as mock_truetype:
        # Simuler l'échec du chargement de la première police
        mock_truetype.side_effect = [
            IOError("Police non trouvée"),
            ImageFont.truetype("/app/fonts/arial.ttf", font_size)
        ]
        
        result = add_text(
            img=img,
            text=text,
            font_name="police_inexistante",
            font_size=font_size,
            color="000000"
        )
        
        # Vérifier que la police Arial a été utilisée comme secours
        assert mock_truetype.call_count == 2, "Arial devrait être essayé comme police de secours"

def test_default_font_scaling():
    """Vérifie que la mise à l'échelle fonctionne correctement avec la police par défaut."""
    img = Image.new('RGB', (400, 200), 'white')
    text = "Test"
    font_sizes = [24, 48, 72]  # Différentes tailles de police à tester
    
    # Simuler l'utilisation de la police par défaut
    with patch('PIL.ImageFont.truetype') as mock_truetype:
        mock_truetype.side_effect = IOError("Police non trouvée")
        
        results = []
        for size in font_sizes:
            result = add_text(
                img=img.copy(),
                text=text,
                font_name="police_inexistante",
                font_size=size,
                color="000000"
            )
            results.append(result)
        
        # Convertir les images en arrays numpy
        arrays = [np.array(img) for img in results]
        
        # Trouver les zones de texte
        text_areas = []
        for arr in arrays:
            text_mask = arr.mean(axis=2) < 250  # Les pixels de texte sont plus sombres
            y_coords, x_coords = np.where(text_mask)
            if len(y_coords) > 0 and len(x_coords) > 0:
                text_height = y_coords.max() - y_coords.min()
                text_width = x_coords.max() - x_coords.min()
                text_areas.append((text_width, text_height))
        
        # Vérifier que les ratios de taille correspondent aux ratios des tailles de police
        base_width, base_height = text_areas[0]
        for i in range(1, len(font_sizes)):
            expected_ratio = font_sizes[i] / font_sizes[0]
            actual_ratio_width = text_areas[i][0] / base_width
            actual_ratio_height = text_areas[i][1] / base_height
            
            # Permettre une marge d'erreur de 20% car la police par défaut peut avoir des comportements différents
            assert abs(actual_ratio_width - expected_ratio) < 0.2, \
                f"La largeur du texte ne s'adapte pas correctement avec la police par défaut"
            assert abs(actual_ratio_height - expected_ratio) < 0.2, \
                f"La hauteur du texte ne s'adapte pas correctement avec la police par défaut"

def test_multiline_default_font():
    """Vérifie que le texte multiligne fonctionne correctement avec la police par défaut."""
    img = Image.new('RGB', (400, 200), 'white')
    text = "Ligne 1<br>Ligne 2"
    font_size = 48
    
    # Simuler l'utilisation de la police par défaut
    with patch('PIL.ImageFont.truetype') as mock_truetype:
        mock_truetype.side_effect = IOError("Police non trouvée")
        
        result = add_text(
            img=img,
            text=text,
            font_name="police_inexistante",
            font_size=font_size,
            color="000000"
        )
        
        result_array = np.array(result)
        text_mask = result_array.mean(axis=2) < 250
        
        # Trouver les lignes de texte
        text_rows = np.sum(text_mask, axis=1)
        peaks = np.where(text_rows > np.mean(text_rows))[0]
        
        if len(peaks) > 0:
            # Grouper les pics en lignes
            line_groups = []
            current_group = [peaks[0]]
            
            for i in range(1, len(peaks)):
                if peaks[i] - peaks[i-1] > font_size/2:  # Nouvelle ligne si l'écart est grand
                    line_groups.append(current_group)
                    current_group = []
                current_group.append(peaks[i])
            
            if current_group:
                line_groups.append(current_group)
            
            # Il devrait y avoir deux lignes distinctes
            assert len(line_groups) == 2, "Le texte multiligne devrait avoir deux lignes distinctes"
            
            # Vérifier l'espacement entre les lignes
            line1_center = np.mean(line_groups[0])
            line2_center = np.mean(line_groups[1])
            line_spacing = line2_center - line1_center
            
            # L'espacement devrait être proportionnel à la taille de la police
            assert line_spacing > font_size * 0.8, \
                "L'espacement des lignes devrait être proportionnel à la taille de la police"

def test_text_alignment_with_default_font():
    """Vérifie que l'alignement du texte fonctionne correctement avec la police par défaut."""
    img = Image.new('RGB', (400, 200), 'white')
    text = "Test"
    font_size = 36
    
    # Simuler l'utilisation de la police par défaut
    with patch('PIL.ImageFont.truetype') as mock_truetype:
        mock_truetype.side_effect = IOError("Police non trouvée")
        
        # Tester différents alignements
        alignments = ['left', 'center', 'right']
        results = []
        
        for align in alignments:
            result = add_text(
                img=img.copy(),
                text=text,
                font_name="police_inexistante",
                font_size=font_size,
                color="000000",
                align=align,
                x=50  # Position centrale
            )
            results.append(result)
        
        # Convertir en arrays numpy et trouver les positions du texte
        positions = []
        for result in results:
            arr = np.array(result)
            text_mask = arr.mean(axis=2) < 250
            x_coords = np.where(np.any(text_mask, axis=0))[0]
            if len(x_coords) > 0:
                text_start = x_coords[0]
                text_end = x_coords[-1]
                positions.append((text_start, text_end))
        
        # Vérifier que les positions correspondent aux alignements
        assert positions[0][0] < positions[1][0], \
            "Le texte aligné à gauche devrait commencer avant le texte centré"
        assert positions[2][1] > positions[1][1], \
            "Le texte aligné à droite devrait finir après le texte centré" 