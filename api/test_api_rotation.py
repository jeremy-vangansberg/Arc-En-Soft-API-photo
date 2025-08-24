#!/usr/bin/env python3
"""
Script de test pour simuler le traitement de l'image comme dans l'API
et identifier pourquoi elle fait une rotation non voulue.
"""

import sys
import os

# Ajouter le chemin du site-packages de l'environnement virtuel
venv_path = os.path.join(os.path.dirname(__file__), '.venv', 'lib', 'python3.12', 'site-packages')
if os.path.exists(venv_path):
    sys.path.append(venv_path)

from PIL import Image, ImageOps
import requests
from io import BytesIO

def simulate_api_processing():
    """
    Simule exactement ce qui se passe dans l'API pour identifier le problème de rotation.
    """
    print("=== SIMULATION DU TRAITEMENT API ===")
    print()
    
    # 1. Charger l'image locale (comme elle est stockée)
    local_path = "media/99c137ea-49d1-4305-b560-c3a062e4fe55.jpeg"
    
    if not os.path.exists(local_path):
        print(f"❌ Image locale non trouvée: {local_path}")
        return
    
    print("1. CHARGEMENT DE L'IMAGE LOCALE:")
    local_img = Image.open(local_path)
    print(f"   - Dimensions: {local_img.size}")
    print(f"   - Mode: {local_img.mode}")
    
    # Vérifier l'orientation locale
    local_exif = local_img.getexif()
    if local_exif:
        local_orientation = local_exif.get(274, 1)
        print(f"   - Orientation EXIF locale: {local_orientation}")
    else:
        print(f"   - Aucune orientation EXIF locale")
    
    print()
    
    # 2. Simuler le chargement via URL (comme dans l'API)
    print("2. SIMULATION DU CHARGEMENT VIA URL (comme dans l'API):")
    
    # Créer une URL locale pour simuler
    try:
        # Simuler le processus de l'API : sauvegarder et recharger
        temp_path = "temp_test_image.jpg"
        local_img.save(temp_path, "JPEG")
        
        # Maintenant recharger comme si c'était une URL
        with open(temp_path, 'rb') as f:
            content = f.read()
        
        # Simuler Image.open(BytesIO(response.content)) de l'API
        api_img = Image.open(BytesIO(content))
        print(f"   - Dimensions après rechargement: {api_img.size}")
        print(f"   - Mode: {api_img.mode}")
        
        # Vérifier l'orientation après rechargement
        api_exif = api_img.getexif()
        if api_exif:
            api_orientation = api_exif.get(274, 1)
            print(f"   - Orientation EXIF après rechargement: {api_orientation}")
        else:
            print(f"   - Aucune orientation EXIF après rechargement")
        
        # Nettoyer
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
    except Exception as e:
        print(f"   ❌ Erreur lors de la simulation: {str(e)}")
    
    print()
    
    # 3. Test de la correction EXIF
    print("3. TEST DE LA CORRECTION EXIF:")
    
    # Test sur l'image locale
    local_corrected = ImageOps.exif_transpose(local_img)
    print(f"   - Local - Avant correction: {local_img.size}")
    print(f"   - Local - Après correction: {local_corrected.size}")
    
    # Test sur l'image simulée API
    try:
        api_corrected = ImageOps.exif_transpose(api_img)
        print(f"   - API simulée - Avant correction: {api_img.size}")
        print(f"   - API simulée - Après correction: {api_corrected.size}")
    except:
        print(f"   - API simulée - Erreur lors de la correction")
    
    print()
    
    # 4. Analyse des différences
    print("4. ANALYSE DES DIFFÉRENCES:")
    
    if local_img.size != local_corrected.size:
        print(f"   ✅ L'image locale nécessite une correction EXIF")
        print(f"      Dimensions changent: {local_img.size} → {local_corrected.size}")
    else:
        print(f"   ℹ️  L'image locale ne nécessite pas de correction EXIF")
    
    try:
        if api_img.size != api_corrected.size:
            print(f"   ✅ L'image API simulée nécessite une correction EXIF")
            print(f"      Dimensions changent: {api_img.size} → {api_corrected.size}")
        else:
            print(f"   ℹ️  L'image API simulée ne nécessite pas de correction EXIF")
    except:
        print(f"   ❌ Impossible de tester la correction sur l'image API simulée")
    
    print()
    
    # 5. Vérification des métadonnées
    print("5. VÉRIFICATION DES MÉTADONNÉES:")
    
    print(f"   - Image locale - Nombre de tags EXIF: {len(local_exif) if local_exif else 0}")
    if local_exif:
        for tag_id in local_exif:
            tag_name = local_exif.get_ifd(tag_id)
            if tag_name:
                print(f"     Tag {tag_id}: {tag_name}")
    
    try:
        print(f"   - Image API simulée - Nombre de tags EXIF: {len(api_exif) if api_exif else 0}")
        if api_exif:
            for tag_id in api_exif:
                tag_name = api_exif.get_ifd(tag_id)
                if tag_name:
                    print(f"     Tag {tag_id}: {tag_name}")
    except:
        print(f"   - Image API simulée - Erreur lors de la vérification")

def main():
    """
    Fonction principale.
    """
    print("Test de simulation du traitement API pour identifier la rotation")
    print("=" * 70)
    print()
    
    simulate_api_processing()
    
    print("=" * 70)
    print("Test terminé.")

if __name__ == "__main__":
    main()
