import requests
from typing import Optional, List
from PIL import Image, ImageOps, ImageDraw, ImageFont
from io import BytesIO

import cv2


def apply_watermark(
    img: Image,
    text: str,
    font_name: str = "arial",
    font_size: int = 30,
    color: str = "000000",  # Noir par défaut
    transparency: int = 100,  # De 0 (transparent) à 255 (opaque)
    repeat_count: int = 5,  # Nombre de répétitions du texte sur l'image
) -> Image:
    """
    Applique un filigrane sur une image avec des répétitions diagonales.

    Args:
        img (Image): L'image sur laquelle appliquer le filigrane.
        text (str): Le texte du filigrane.
        font_name (str): Nom de la police (par défaut Arial).
        font_size (int): Taille de la police (par défaut 30).
        color (str): Couleur hexadécimale du texte (par défaut noir "000000").
        transparency (int): Transparence du texte (0 transparent, 255 opaque).
        repeat_count (int): Nombre de répétitions du texte en diagonale.

    Returns:
        Image: L'image avec le filigrane appliqué.
    """
    font_path = ''
    match font_name:
        case "arial":
            font_path = "/usr/share/fonts/arial.ttf"
        case "tnr":
            font_path = "/usr/share/fonts/TimesNewRoman.ttf"
        case "helvetica":
            font_path = "/usr/share/fonts/Helvetica.ttf"
        case "verdana":
            font_path = "/usr/share/fonts/Verdana.ttf"
        case "avenir":
            font_path = "/usr/share/fonts/AvenirNextCyr-Regular.ttf"

    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        print("Font not found. Using default font.")
        font = ImageFont.load_default()

    # Crée un calque transparent pour le filigrane
    watermark_layer = Image.new("RGBA", img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(watermark_layer)

    # Convertir la couleur hexadécimale en RGBA avec transparence
    color_with_transparency = tuple(int(color[i:i+2], 16) for i in (0, 2, 4)) + (transparency,)

    # Dimensions de l'image
    img_width, img_height = img.size

    # Répartir les filigranes en diagonale
    step_x = img_width // (repeat_count + 1)  # Espacement horizontal entre les filigranes
    step_y = img_height // (repeat_count + 1)  # Espacement vertical entre les filigranes

    for i in range(repeat_count + 1):
        # Position relative en diagonale
        x = step_x * i
        y = step_y * i

        # Ajouter le texte en diagonale
        draw.text((x, y), text, font=font, fill=color_with_transparency)

    # Combiner le filigrane avec l'image d'origine
    return Image.alpha_composite(img.convert("RGBA"), watermark_layer).convert("RGB")


def apply_resize_template(result_img, new_width):
    width, height = result_img.size
    new_height = int((new_width / width) * height)
    resized_img = result_img.resize((new_width, new_height))
    return resized_img

import cv2
import numpy as np
from PIL import Image

def apply_cartoon_filter(pil_img):
    """
    Applique un filtre cartoon à une image PIL.
    """
    # Log du format de l'image
    print(f"Type de l'image reçue : {type(pil_img)}")
    
    # Convertir PIL.Image en tableau NumPy
    img = np.array(pil_img)
    print(f"Shape de l'image convertie en NumPy : {img.shape}")
    
    if img.shape[-1] == 3:  # RGB image
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    else:
        raise ValueError("L'image d'entrée n'est pas au format RGB.")

    # Transformation en niveaux de gris
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)

    # Détection des contours
    edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                  cv2.THRESH_BINARY, 9, 7)

    # Réduction des couleurs
    color = cv2.bilateralFilter(img, 9, 300, 300)

    # Fusionner les contours et l'image colorée
    cartoon = cv2.bitwise_and(color, color, mask=edges)

    # Convertir de BGR à RGB pour PIL.Image
    cartoon_rgb = cv2.cvtColor(cartoon, cv2.COLOR_BGR2RGB)
    print("Filtre cartoon appliqué avec succès.")
    return Image.fromarray(cartoon_rgb)


def load_image(image_url: str) -> Image:
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    return img

def apply_rotation(img: Image, rotation: int) -> Image:
    return img.rotate(rotation, expand=True, fillcolor=None)

def apply_crop(img: Image, dh: float, db: float) -> Image:
    width, height = img.size
    top = (dh / 100) * height  # Rognage depuis le haut
    bottom = height - ((db / 100) * height)  # Rognage depuis le bas
    return img.crop((0, top, width, bottom))

def apply_filter(img: Image, _filter: str) -> Image:
    """
    Applique un filtre spécifique à une image PIL.
    """
    print(f"Filtre demandé : {_filter}, Type de l'image : {type(img)}")

    match _filter:
        case 'nb':
            return ImageOps.grayscale(img)
        case 'cartoon':
            return apply_cartoon_filter(img)
        case _:
            print(f"Filtre inconnu : {_filter}. Aucun filtre appliqué.")
            return img


def add_text(
    img: Image = Image.new('RGB', (100, 100)), 
    text: str = "Sample Text", 
    font_name: str = "arial",  # Path to Arial font
    font_size: int = 20, 
    x: float = 10, 
    y: float = 10, 
    color: str = "FFFFFF",
    align: Optional[str] = "left"
) -> Image:
    
    font_path = ''

    match font_name:
        case "arial" :
            font_path = "/usr/share/fonts/arial.ttf"
        case "tnr" :
            font_path = "/usr/share/fonts/TimesNewRoman.ttf"
        case "helvetica" :
            font_path = "/usr/share/fonts/Helvetica.ttf"
        case "verdana" :
            font_path = "/usr/share/fonts/Verdana.ttf"
        case "avenir" :
            font_path = "/usr/share/fonts/AvenirNextCyr-Regular.ttf"
        case "roboto" :
            font_path = "/usr/share/fonts/Roboto-Medium.ttf"
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        print("Font not found. Using default font.")
        font = ImageFont.load_default()

    draw = ImageDraw.Draw(img)
    width, height = img.size
    y = (y / 100) * height
    x = (x / 100) * width
    color = "#" + color

    # Diviser le texte en lignes
    lines = text.split("<br>")
    line_height = font_size + 5  # Ajouter un espace entre les lignes
    
    for i, line in enumerate(lines):
        draw.text((x, y + i * line_height), line, font=font, fill=color, align=align)

    return img