import requests
from typing import Optional, List, Union
from PIL import Image, ImageOps, ImageDraw, ImageFont
from io import BytesIO
import cv2
import numpy as np

def apply_watermark(
    img: Image,
    text: str,
    font_name: str = "arial",
    color: str = "000000",  # Noir par défaut
    transparency: int = 100,  # De 0 (transparent) à 255 (opaque)
    repeat_count: int = 5,  # Nombre de répétitions du texte sur l'image
) -> Image:
    """
    Applique un filigrane sur une image avec des répétitions diagonales.
    La taille de la police est automatiquement proportionnelle à la taille de l'image.

    Args:
        img (Image): L'image sur laquelle appliquer le filigrane.
        text (str): Le texte du filigrane.
        font_name (str): Nom de la police (par défaut Arial).
        color (str): Couleur hexadécimale du texte (par défaut noir "000000").
        transparency (int): Transparence du texte (0 transparent, 255 opaque).
        repeat_count (int): Nombre de répétitions du texte en diagonale.

    Returns:
        Image: L'image avec le filigrane appliqué.
    """
    # Sélectionner un chemin de police dynamique
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

    # Obtenir les dimensions de l'image
    img_width, img_height = img.size

    # Ajuster dynamiquement la taille de la police en fonction de l'image
    base_font_size = min(img_width, img_height) // 20  # 5% de la plus petite dimension
    font_size = max(base_font_size, 10)  # S'assurer que la taille de police est raisonnable

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



def apply_resize_template(result_img: Image.Image, new_width: int) -> Image.Image:
    """
    Redimensionne une image en conservant ses proportions.
    
    Args:
        result_img (Image.Image): L'image à redimensionner
        new_width (int): La nouvelle largeur souhaitée en pixels
        
    Returns:
        Image.Image: L'image redimensionnée
    """
    width, height = result_img.size
    aspect_ratio = width / height
    new_height = int(new_width / aspect_ratio)
    resized_img = result_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    return resized_img



def apply_cartoon_filter(pil_img: Image.Image) -> Image.Image:
    """
    Applique un filtre cartoon à une image PIL.
    
    Args:
        pil_img (Image.Image): L'image PIL à transformer
        
    Returns:
        Image.Image: L'image avec le filtre cartoon appliqué
        
    Raises:
        ValueError: Si l'image n'est pas au format RGB
    """
    print(f"Type de l'image reçue : {type(pil_img)}")
    
    img = np.array(pil_img)
    print(f"Shape de l'image convertie en NumPy : {img.shape}")
    
    if img.shape[-1] == 3:  # RGB image
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    else:
        raise ValueError("L'image d'entrée n'est pas au format RGB.")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)
    edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                  cv2.THRESH_BINARY, 9, 7)
    color = cv2.bilateralFilter(img, 9, 300, 300)
    cartoon = cv2.bitwise_and(color, color, mask=edges)
    cartoon_rgb = cv2.cvtColor(cartoon, cv2.COLOR_BGR2RGB)
    print("Filtre cartoon appliqué avec succès.")
    return Image.fromarray(cartoon_rgb)


def load_image(image_url: Union[str, List[str]], is_template: bool = False) -> Union[Image.Image, List[Image.Image]]:
    """
    Charge une image ou une liste d'images depuis une URL ou une liste d'URLs.
    
    Args:
        image_url (Union[str, List[str]]): URL unique ou liste d'URLs des images à charger
        is_template (bool): Si True, l'URL est considérée comme unique même si c'est une liste
        
    Returns:
        Union[Image.Image, List[Image.Image]]: Une image ou une liste d'images PIL
    """
    if isinstance(image_url, list) and not is_template:
        return [load_image(url, is_template=True) for url in image_url]
    
    if isinstance(image_url, list):
        image_url = image_url[0]
    
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    return img

def apply_rotation(img: Image.Image, rotation: int) -> Image.Image:
    """
    Applique une rotation à une image.
    
    Args:
        img (Image.Image): L'image à faire pivoter
        rotation (int): L'angle de rotation en degrés
        
    Returns:
        Image.Image: L'image pivotée
    """
    print(f'rotation {rotation} appliquée')
    return img.rotate(rotation, expand=True, fillcolor=None)

def apply_crop(img: Image.Image, dh: float, db: float) -> Image.Image:
    """
    Rogne une image en haut et en bas selon des pourcentages.
    
    Args:
        img (Image.Image): L'image à rogner
        dh (float): Pourcentage à rogner depuis le haut (0-100)
        db (float): Pourcentage à rogner depuis le bas (0-100)
        
    Returns:
        Image.Image: L'image rognée
    """
    width, height = img.size
    top = (dh / 100) * height
    bottom = height - ((db / 100) * height)
    return img.crop((0, top, width, bottom))

def apply_filter(img: Image.Image, _filter: str) -> Image.Image:
    """
    Applique un filtre spécifique à une image PIL.
    
    Args:
        img (Image.Image): L'image à filtrer
        _filter (str): Le type de filtre à appliquer ('nb', 'cartoon', ou autre)
        
    Returns:
        Image.Image: L'image avec le filtre appliqué
        
    Notes:
        - 'nb' : Convertit l'image en niveaux de gris
        - 'cartoon' : Applique un effet cartoon
        - autre valeur : Retourne l'image sans modification
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
    img: Image.Image = Image.new('RGB', (100, 100)), 
    text: str = "Sample Text", 
    font_name: str = "arial",
    font_size: int = 20, 
    x: float = 10, 
    y: float = 10, 
    color: str = "FFFFFF",
    align: Optional[str] = "left"
) -> Image.Image:
    """
    Ajoute du texte sur une image.
    
    Args:
        img (Image.Image): L'image sur laquelle ajouter le texte
        text (str): Le texte à ajouter (supporte les sauts de ligne avec <br>)
        font_name (str): Nom de la police (arial, tnr, helvetica, verdana, avenir, roboto)
        font_size (int): Taille de la police en points
        x (float): Position horizontale en pourcentage (0-100)
        y (float): Position verticale en pourcentage (0-100)
        color (str): Couleur du texte en format hexadécimal sans #
        align (str, optional): Alignement du texte (left, center, right)
        
    Returns:
        Image.Image: L'image avec le texte ajouté
        
    Notes:
        - Les chemins des polices sont prédéfinis dans le système
        - Si la police n'est pas trouvée, utilise la police par défaut du système
        - Les sauts de ligne sont gérés avec la balise <br>
    """
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