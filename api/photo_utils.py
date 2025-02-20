import requests
from typing import Optional, List, Union, Tuple
from PIL import Image, ImageOps, ImageDraw, ImageFont
from io import BytesIO
import cv2
import numpy as np
from enum import Enum
from dataclasses import dataclass
import logging

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
    Redimensionne une image en préservant la qualité maximale.
    
    Args:
        result_img (Image.Image): L'image à redimensionner
        new_width (int): La nouvelle largeur souhaitée en pixels
        
    Returns:
        Image.Image: L'image redimensionnée
    """
    # Si l'image est déjà à la bonne taille, la retourner telle quelle
    if result_img.width == new_width:
        return result_img

    width, height = result_img.size
    aspect_ratio = width / height
    new_height = int(new_width / aspect_ratio)

    # Pour une réduction de taille
    if new_width < width:
        # Utiliser BOX pour un meilleur rendu lors de la réduction
        return result_img.resize((new_width, new_height), Image.Resampling.BOX)
    else:
        # Pour un agrandissement, utiliser BICUBIC sans filtrage
        return result_img.resize((new_width, new_height), Image.Resampling.BICUBIC, reducing_gap=None)



def apply_cartoon_filter(pil_img: Image.Image) -> Image.Image:
    """
    Applique un filtre cartoon à une image PIL avec un minimum de traitement.
    
    Args:
        pil_img (Image.Image): L'image PIL à transformer
        
    Returns:
        Image.Image: L'image avec le filtre cartoon appliqué
    """
    print(f"Type de l'image reçue : {type(pil_img)}")
    
    img = np.array(pil_img)
    print(f"Shape de l'image convertie en NumPy : {img.shape}")
    
    if img.shape[-1] == 3:  # RGB image
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    else:
        raise ValueError("L'image d'entrée n'est pas au format RGB.")

    # Réduction du flou médian pour préserver plus de détails
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 3)  # Réduit de 5 à 3 pour moins de flou
    
    # Ajustement des paramètres pour moins de distorsion
    edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                cv2.THRESH_BINARY, 7, 5)  # Réduit de 9 à 7
                                
    # Réduction de l'intensité du filtre bilatéral
    color = cv2.bilateralFilter(img, 5, 200, 200)  # Réduit de 9 à 5
    
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
        
    Raises:
        ValueError: Si l'URL est invalide ou si l'image ne peut pas être chargée
    """
    logger = logging.getLogger(__name__)
    
    if isinstance(image_url, list) and not is_template:
        return [load_image(url, is_template=True) for url in image_url]
    
    if isinstance(image_url, list):
        image_url = image_url[0]
    
    try:
        logger.info(f"Tentative de chargement de l'image: {image_url}")
        response = requests.get(image_url, timeout=30)  # Timeout après 30 secondes
        response.raise_for_status()  # Lève une exception si le status n'est pas 2xx
        
        img = Image.open(BytesIO(response.content))
        logger.info(f"Image chargée avec succès. Dimensions: {img.size}")
        return img
        
    except requests.exceptions.Timeout:
        logger.error(f"Timeout lors du chargement de l'image: {image_url}")
        raise ValueError(f"Le chargement de l'image a pris trop de temps: {image_url}")
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur lors du chargement de l'image {image_url}: {str(e)}")
        raise ValueError(f"Impossible de charger l'image depuis l'URL: {image_url}. Erreur: {str(e)}")
        
    except Exception as e:
        logger.error(f"Erreur inattendue lors du chargement de l'image {image_url}: {str(e)}")
        raise ValueError(f"Erreur lors du traitement de l'image: {str(e)}")

def apply_rotation(img: Image.Image, rotation: int) -> Image.Image:
    """
    Applique une rotation à une image en préservant la qualité.
    
    Args:
        img (Image.Image): L'image à faire pivoter
        rotation (int): L'angle de rotation en degrés
        
    Returns:
        Image.Image: L'image pivotée
    """
    if rotation == 0:
        return img
    
    # Pour les rotations de 90, 180, 270 degrés, utiliser une rotation sans interpolation
    if rotation in [90, 180, 270]:
        return img.rotate(rotation, expand=True, fillcolor=None, resample=Image.Resampling.NEAREST)
    
    # Pour les autres angles, utiliser une rotation de meilleure qualité
    # mais toujours avec un minimum de traitement
    return img.rotate(rotation, expand=True, fillcolor=None, resample=Image.Resampling.BICUBIC)

def apply_crop(img: Image.Image, dh: float, db: float) -> Image.Image:
    """
    Rogne une image en haut et en bas selon des pourcentages.
    Cette fonction est déjà optimale car elle ne fait pas de transformation de pixels.
    
    Args:
        img (Image.Image): L'image à rogner
        dh (float): Pourcentage à rogner depuis le haut (0-100)
        db (float): Pourcentage à rogner depuis le bas (0-100)
        
    Returns:
        Image.Image: L'image rognée
    """
    if dh == 0 and db == 0:
        return img
        
    width, height = img.size
    top = int((dh / 100) * height)
    bottom = int(height - ((db / 100) * height))
    return img.crop((0, top, width, bottom))

def apply_filter(img: Image.Image, _filter: str) -> Image.Image:
    """
    Applique un filtre spécifique à une image PIL.
    Minimise les transformations pour préserver la qualité.
    
    Args:
        img (Image.Image): L'image à filtrer
        _filter (str): Le type de filtre à appliquer ('nb', 'cartoon', ou autre)
        
    Returns:
        Image.Image: L'image avec le filtre appliqué
    """
    print(f"Filtre demandé : {_filter}, Type de l'image : {type(img)}")

    match _filter:
        case 'nb':
            # Conversion directe en niveaux de gris sans post-traitement
            return img.convert('L')
        case 'cartoon':
            return apply_cartoon_filter(img)
        case _:
            print(f"Filtre inconnu : {_filter}. Aucun filtre appliqué.")
            return img

class TextRenderStrategy(str, Enum):
    BASIC = "basic"           # Rendu basique
    HIGH_RES = "high_res"     # Rendu haute résolution avec downscaling
    OUTLINED = "outlined"     # Texte avec contour
    SHADOW = "shadow"         # Texte avec ombre
    COMBINED = "combined"     # Combine plusieurs stratégies

@dataclass
class TextConfig:
    text: str
    font_name: str = "arial"
    font_size: int = 20
    x: float = 10
    y: float = 10
    color: str = "FFFFFF"
    align: Optional[str] = "left"
    strategy: TextRenderStrategy = TextRenderStrategy.BASIC
    dpi: int = 300
    stroke_width: int = 0
    shadow_offset: Tuple[int, int] = (2, 2)
    background_blur: bool = False

class TextRenderer:
    def __init__(self, config: TextConfig):
        self.config = config
        self._prepare_font()

    def _prepare_font(self):
        """Prépare la police avec le bon chemin et la bonne taille."""
        font_path = ''
        match self.config.font_name.lower():
            case "arial":
                font_path = "/app/fonts/arial.ttf"
            case "tnr":
                font_path = "/app/fonts/TimesNewRoman.ttf"
            case "helvetica":
                font_path = "/app/fonts/Helvetica.ttf"
            case "verdana":
                font_path = "/app/fonts/Verdana.ttf"
            case "avenir":
                font_path = "/app/fonts/AvenirNextCyr-Regular.ttf"
            case "roboto":
                font_path = "/app/fonts/Roboto-Medium.ttf"
            case _:
                font_path = "/app/fonts/arial.ttf"  # Police par défaut
        
        logger = logging.getLogger(__name__)
        logger.info(f"Chargement de la police : {font_path}")
        
        try:
            self.font = ImageFont.truetype(font_path, self.config.font_size)
            logger.info(f"Police chargée avec succès : {self.config.font_name}, taille={self.config.font_size}")
        except Exception as e:
            logger.error(f"Erreur lors du chargement de la police {font_path}: {str(e)}")
            logger.warning("Tentative de chargement de la police de secours (arial.ttf)")
            try:
                # Essayer de charger arial comme police de secours avec la taille demandée
                self.font = ImageFont.truetype("/app/fonts/arial.ttf", self.config.font_size)
                logger.info("Police de secours (arial.ttf) chargée avec succès")
            except Exception as e:
                logger.error(f"Échec du chargement de la police de secours : {str(e)}")
                logger.warning("Utilisation de la police système par défaut (taille fixe)")
                self.font = ImageFont.load_default()
                # Ajuster la taille du texte en utilisant un facteur d'échelle
                self.scale_factor = self.config.font_size / 10  # 10 est la taille approximative de la police par défaut

    def _get_text_size(self, text: str) -> Tuple[int, int]:
        """Calcule la taille du texte avec la police actuelle."""
        draw = ImageDraw.Draw(Image.new('RGB', (1, 1)))
        return draw.textsize(text, font=self.font)

    def _render_basic(self, img: Image.Image) -> Image.Image:
        """Rendu basique du texte avec qualité optimisée."""
        # Créer une image temporaire avec canal alpha
        text_overlay = Image.new('RGBA', img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(text_overlay)
        
        width, height = img.size
        x = (self.config.x / 100) * width
        y = (self.config.y / 100) * height
        
        lines = self.config.text.split("<br>")
        line_height = self.config.font_size + 5
        
        # Si nous utilisons la police par défaut, ajuster la position
        if hasattr(self, 'scale_factor'):
            line_height = int(line_height * self.scale_factor)
        
        for i, line in enumerate(lines):
            pos_x, pos_y = x, y + i * line_height
            
            if hasattr(self, 'scale_factor'):
                # Pour la police par défaut, créer une image plus grande
                large_overlay = Image.new('RGBA', 
                    (int(width * self.scale_factor), int(height * self.scale_factor)), 
                    (255, 255, 255, 0))
                temp_draw = ImageDraw.Draw(large_overlay)
                
                # Dessiner le texte à haute résolution
                scaled_x = pos_x * self.scale_factor
                scaled_y = pos_y * self.scale_factor
                temp_draw.text(
                    (scaled_x, scaled_y), 
                    line, 
                    font=self.font, 
                    fill="#" + self.config.color, 
                    align=self.config.align,
                    antialias=True
                )
                
                # Redimensionner avec BOX pour un meilleur rendu
                resized_text = large_overlay.resize(img.size, Image.Resampling.BOX)
                text_overlay = Image.alpha_composite(text_overlay, resized_text)
            else:
                # Pour les polices TrueType, utiliser le rendu antialiasé natif
                draw.text(
                    (pos_x, pos_y), 
                    line, 
                    font=self.font, 
                    fill="#" + self.config.color, 
                    align=self.config.align,
                    antialias=True
                )
        
        # Fusionner le texte avec l'image d'origine
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        result = Image.alpha_composite(img, text_overlay)
        
        return result.convert('RGB') if img.mode == 'RGBA' else result

    def _render_high_res(self, img: Image.Image) -> Image.Image:
        """Rendu haute résolution avec downscaling optimisé."""
        # Augmenter la résolution de travail
        scale_factor = 4  # Facteur fixe pour une meilleure qualité
        
        # Créer une image temporaire haute résolution
        temp_img = Image.new('RGBA', 
            (img.width * scale_factor, img.height * scale_factor),
            (255, 255, 255, 0))
        
        # Ajuster la taille de la police pour la haute résolution
        original_size = self.config.font_size
        self.config.font_size = int(original_size * scale_factor)
        self._prepare_font()
        
        # Rendre le texte en haute résolution
        temp_img = self._render_basic(temp_img)
        
        # Restaurer la taille de police originale
        self.config.font_size = original_size
        self._prepare_font()
        
        # Redimensionner avec BOX pour un meilleur rendu
        return temp_img.resize(img.size, Image.Resampling.BOX)

    def _render_outlined(self, img: Image.Image) -> Image.Image:
        """Rendu avec contour."""
        draw = ImageDraw.Draw(img)
        width, height = img.size
        x = (self.config.x / 100) * width
        y = (self.config.y / 100) * height
        
        lines = self.config.text.split("<br>")
        line_height = self.config.font_size + 5
        stroke_width = max(1, self.config.font_size // 30)
        
        for i, line in enumerate(lines):
            # Dessiner le contour
            draw.text(
                (x, y + i * line_height),
                line,
                font=self.font,
                fill="#000000",
                stroke_width=stroke_width,
                align=self.config.align
            )
            # Dessiner le texte
            draw.text(
                (x, y + i * line_height),
                line,
                font=self.font,
                fill="#" + self.config.color,
                align=self.config.align
            )
        return img

    def _render_shadow(self, img: Image.Image) -> Image.Image:
        """Rendu avec ombre portée."""
        draw = ImageDraw.Draw(img)
        width, height = img.size
        x = (self.config.x / 100) * width
        y = (self.config.y / 100) * height
        
        lines = self.config.text.split("<br>")
        line_height = self.config.font_size + 5
        
        for i, line in enumerate(lines):
            # Dessiner l'ombre
            draw.text(
                (x + self.config.shadow_offset[0], y + i * line_height + self.config.shadow_offset[1]),
                line,
                font=self.font,
                fill="#000000",
                align=self.config.align
            )
            # Dessiner le texte
            draw.text(
                (x, y + i * line_height),
                line,
                font=self.font,
                fill="#" + self.config.color,
                align=self.config.align
            )
        return img

    def render(self, img: Image.Image) -> Image.Image:
        """Applique la stratégie de rendu sélectionnée."""
        match self.config.strategy:
            case TextRenderStrategy.BASIC:
                return self._render_basic(img)
            case TextRenderStrategy.HIGH_RES:
                return self._render_high_res(img)
            case TextRenderStrategy.OUTLINED:
                return self._render_outlined(img)
            case TextRenderStrategy.SHADOW:
                return self._render_shadow(img)
            case TextRenderStrategy.COMBINED:
                # Utiliser uniquement le rendu haute résolution
                return self._render_high_res(img)
        return img

def add_text(
    img: Image.Image,
    text: str = "Sample Text", 
    font_name: str = "arial",
    font_size: int = 20, 
    x: float = 10, 
    y: float = 10, 
    color: str = "FFFFFF",
    align: Optional[str] = "left",
    strategy: TextRenderStrategy = TextRenderStrategy.BASIC,
    dpi: int = 300
) -> Image.Image:
    """
    Ajoute du texte sur une image.
    """
    # Créer une copie de l'image
    result = img.copy()
    draw = ImageDraw.Draw(result)
    
    # Charger la police
    try:
        font = ImageFont.truetype(f"/app/fonts/{font_name}.ttf", font_size)
    except:
        try:
            font = ImageFont.truetype("/app/fonts/arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
    
    # Calculer les positions en pixels
    width, height = img.size
    pos_x = (x / 100) * width
    pos_y = (y / 100) * height
    
    # Gérer le texte multiligne
    lines = text.split("<br>")
    line_height = font_size + 5
    
    # Dessiner chaque ligne
    for i, line in enumerate(lines):
        draw.text(
            (pos_x, pos_y + i * line_height),
            line,
            font=font,
            fill="#" + color,
            align=align
        )
    
    return result