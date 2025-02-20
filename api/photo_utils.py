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
        """Rendu basique du texte."""
        draw = ImageDraw.Draw(img)
        width, height = img.size
        x = (self.config.x / 100) * width
        y = (self.config.y / 100) * height
        
        lines = self.config.text.split("<br>")
        line_height = self.config.font_size + 5
        
        # Si nous utilisons la police par défaut, ajuster la position pour la mise à l'échelle
        if hasattr(self, 'scale_factor'):
            line_height = int(line_height * self.scale_factor)
        
        for i, line in enumerate(lines):
            # Position de base pour le texte
            pos_x, pos_y = x, y + i * line_height
            
            # Si nous utilisons la police par défaut, créer une image temporaire plus grande
            if hasattr(self, 'scale_factor'):
                # Créer une image temporaire pour le texte
                text_img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
                temp_draw = ImageDraw.Draw(text_img)
                temp_draw.text((pos_x, pos_y), line, font=self.font, fill="#" + self.config.color, align=self.config.align)
                
                # Redimensionner le texte selon le facteur d'échelle
                scaled_text = text_img.resize(
                    (int(width * self.scale_factor), int(height * self.scale_factor)),
                    Image.Resampling.LANCZOS
                )
                
                # Redimensionner à la taille originale
                final_text = scaled_text.resize((width, height), Image.Resampling.LANCZOS)
                
                # Fusionner avec l'image principale
                img = Image.alpha_composite(img.convert('RGBA'), final_text)
            else:
                # Rendu normal pour les polices TrueType
                draw.text((pos_x, pos_y), line, font=self.font, fill="#" + self.config.color, align=self.config.align)
        
        return img.convert('RGB') if img.mode == 'RGBA' else img

    def _render_high_res(self, img: Image.Image) -> Image.Image:
        """Rendu haute résolution avec downscaling."""
        # Calculer le scale_factor en fonction du DPI
        base_dpi = 72  # DPI de base pour les polices
        scale_factor = max(1, self.config.dpi / base_dpi)
        
        # Créer une image temporaire plus grande
        temp_img = img.copy().resize(
            (int(img.width * scale_factor), int(img.height * scale_factor)),
            Image.Resampling.LANCZOS
        )
        
        # Ajuster la taille de la police pour la plus grande image
        original_size = self.config.font_size
        self.config.font_size = int(original_size * scale_factor)
        self._prepare_font()
        
        # Rendre le texte sur l'image plus grande
        temp_img = self._render_basic(temp_img)
        
        # Restaurer la taille de police originale
        self.config.font_size = original_size
        self._prepare_font()
        
        # Redimensionner à la taille originale avec antialiasing de haute qualité
        return temp_img.resize(img.size, Image.Resampling.LANCZOS)

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
    strategy: TextRenderStrategy = TextRenderStrategy.COMBINED,
    dpi: int = 300
) -> Image.Image:
    """
    Ajoute du texte sur une image avec une qualité améliorée.
    
    Args:
        img (Image.Image): L'image sur laquelle ajouter le texte
        text (str): Le texte à ajouter (supporte les sauts de ligne avec <br>)
        font_name (str): Nom de la police (arial, tnr, helvetica, verdana, avenir, roboto)
        font_size (int): Taille de la police en points
        x (float): Position horizontale en pourcentage (0-100)
        y (float): Position verticale en pourcentage (0-100)
        color (str): Couleur du texte en format hexadécimal sans #
        align (str, optional): Alignement du texte (left, center, right)
        strategy (TextRenderStrategy): Stratégie de rendu du texte
        dpi (int): Résolution en DPI pour le calcul de la taille de police
        
    Returns:
        Image.Image: L'image avec le texte ajouté
        
    Raises:
        ValueError: Si les paramètres sont invalides
    """
    if not isinstance(img, Image.Image):
        raise ValueError("L'argument img doit être une instance de PIL.Image.Image")
        
    if not (0 <= x <= 100) or not (0 <= y <= 100):
        raise ValueError("Les positions x et y doivent être comprises entre 0 et 100")
        
    if not (1 <= font_size <= 1000):
        raise ValueError("La taille de la police doit être comprise entre 1 et 1000")
        
    if not len(color) == 6 or not all(c in '0123456789ABCDEFabcdef' for c in color):
        raise ValueError("La couleur doit être au format hexadécimal valide (6 caractères)")
    
    config = TextConfig(
        text=text,
        font_name=font_name,
        font_size=font_size,  # Utiliser la taille de police telle quelle
        x=x,
        y=y,
        color=color,
        align=align,
        strategy=strategy,
        dpi=dpi
    )
    
    renderer = TextRenderer(config)
    return renderer.render(img.copy())