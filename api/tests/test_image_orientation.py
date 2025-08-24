#!/usr/bin/env python3
"""
Test pour analyser les problèmes d'orientation des images.
"""

import pytest
from PIL import Image, ImageOps
import os
import sys

# Ajouter le chemin du projet pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from photo_utils import load_image, apply_rotation, apply_crop, apply_filter


class TestImageOrientation:
    """Tests pour vérifier l'orientation des images."""
    
    def test_local_image_orientation(self):
        """Test l'orientation de l'image locale problématique."""
        image_path = "media/99c137ea-49d1-4305-b560-c3a062e4fe55.jpeg"
        
        if not os.path.exists(image_path):
            pytest.skip(f"Image de test non trouvée: {image_path}")
        
        # Charger l'image
        img = Image.open(image_path)
        assert img.size == (852, 1280), f"Dimensions attendues (852, 1280), obtenues {img.size}"
        
        # Vérifier qu'elle est en mode portrait
        width, height = img.size
        assert width < height, "L'image devrait être en mode portrait"
        
        # Vérifier les métadonnées EXIF
        exif_data = img.getexif()
        if exif_data:
            orientation = exif_data.get(274, 1)
            print(f"Orientation EXIF détectée: {orientation}")
        else:
            print("Aucune métadonnée EXIF trouvée")
    
    def test_exif_transpose_correction(self):
        """Test que exif_transpose fonctionne correctement."""
        image_path = "media/99c137ea-49d1-4305-b560-c3a062e4fe55.jpeg"
        
        if not os.path.exists(image_path):
            pytest.skip(f"Image de test non trouvée: {image_path}")
        
        # Charger l'image
        original_img = Image.open(image_path)
        original_size = original_img.size
        
        # Appliquer exif_transpose
        corrected_img = ImageOps.exif_transpose(original_img)
        corrected_size = corrected_img.size
        
        # Vérifier que les dimensions sont cohérentes
        assert corrected_size == original_size, f"exif_transpose ne devrait pas changer les dimensions: {original_size} → {corrected_size}"
    
    def test_api_processing_simulation(self):
        """Simule le traitement de l'API pour identifier les problèmes."""
        image_path = "media/99c137ea-49d1-4305-b560-c3a062e4fe55.jpeg"
        
        if not os.path.exists(image_path):
            pytest.skip(f"Image de test non trouvée: {image_path}")
        
        # Charger l'image comme dans load_image
        original_img = Image.open(image_path)
        img_after_exif = ImageOps.exif_transpose(original_img)
        
        # Simuler le processus de l'API
        working_img = img_after_exif.copy()
        
        # Test du rognage
        cropped_img = apply_crop(working_img, 0, 0)
        assert cropped_img.size == working_img.size, "Le rognage 0% ne devrait pas changer les dimensions"
        
        # Test de la rotation
        rotated_img = apply_rotation(cropped_img, 0)
        assert rotated_img.size == cropped_img.size, "La rotation 0° ne devrait pas changer les dimensions"
        
        # Test du filtre
        filtered_img = apply_filter(rotated_img, 'none')
        assert filtered_img.size == rotated_img.size, "Le filtre 'none' ne devrait pas changer les dimensions"
        
        # Test du redimensionnement
        template_width = 1000
        width_factor = 30.0
        scaled_width = int((width_factor / 100) * template_width)
        aspect_ratio = filtered_img.width / filtered_img.height
        scaled_height = int(scaled_width / aspect_ratio)
        
        resized_img = filtered_img.resize((scaled_width, scaled_height))
        
        # Vérifier que les proportions sont conservées
        original_ratio = original_img.width / original_img.height
        final_ratio = resized_img.width / resized_img.height
        
        assert abs(original_ratio - final_ratio) < 0.01, f"Les proportions ont changé: {original_ratio:.3f} → {final_ratio:.3f}"
    
    def test_rotation_functions(self):
        """Test que les fonctions de rotation fonctionnent correctement."""
        image_path = "media/99c137ea-49d1-4305-b560-c3a062e4fe55.jpeg"
        
        if not os.path.exists(image_path):
            pytest.skip(f"Image de test non trouvée: {image_path}")
        
        img = Image.open(image_path)
        
        # Test des rotations de base
        rotations = [90, 180, 270]
        for rotation in rotations:
            rotated = apply_rotation(img, rotation)
            if rotation in [90, 270]:
                # 90° et 270° inversent largeur et hauteur
                expected_size = (img.size[1], img.size[0])
                assert rotated.size == expected_size, f"Rotation {rotation}°: {img.size} → {rotated.size}, attendu {expected_size}"
            elif rotation == 180:
                # 180° garde les mêmes dimensions
                assert rotated.size == img.size, f"Rotation 180°: {img.size} → {rotated.size}"
    
    def test_image_dimensions_consistency(self):
        """Vérifie que les dimensions restent cohérentes tout au long du processus."""
        image_path = "media/99c137ea-49d1-4305-b560-c3a062e4fe55.jpeg"
        
        if not os.path.exists(image_path):
            pytest.skip(f"Image de test non trouvée: {image_path}")
        
        # Charger l'image
        img = Image.open(image_path)
        initial_size = img.size
        
        print(f"\n=== TEST DE COHÉRENCE DES DIMENSIONS ===")
        print(f"Dimensions initiales: {initial_size}")
        
        # Appliquer exif_transpose
        img = ImageOps.exif_transpose(img)
        print(f"Après exif_transpose: {img.size}")
        
        # Copier l'image
        img = img.copy()
        print(f"Après copy(): {img.size}")
        
        # Appliquer le rognage
        img = apply_crop(img, 0, 0)
        print(f"Après rognage: {img.size}")
        
        # Appliquer la rotation
        img = apply_rotation(img, 0)
        print(f"Après rotation 0°: {img.size}")
        
        # Appliquer le filtre
        img = apply_filter(img, 'none')
        print(f"Après filtre: {img.size}")
        
        # Vérifier que les dimensions de base sont conservées
        assert img.size == initial_size, f"Les dimensions ont changé: {initial_size} → {img.size}"
        print(f"✅ Dimensions finales cohérentes: {img.size}")


if __name__ == "__main__":
    # Exécuter les tests
    pytest.main([__file__, "-v"])
