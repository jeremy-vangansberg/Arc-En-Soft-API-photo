description_create_image = """
#### **Endpoint : `GET /create_image/`**

Cet endpoint déclenche le traitement de l'image avec les paramètres spécifiés. Voici les principales fonctionnalités :
- **Ajout d'une image personnalisée** sur un modèle (template).
- **Transformation de l'image** avec rognage, rotation, redimensionnement, et filtres (par exemple : noir et blanc).
- **Ajout de textes personnalisés** (position, taille, couleur, police) avec support pour un nombre illimité de textes.
- **Ajout facultatif d'un filigrane** (watermark) sur l'image.
- **Téléchargement de l'image finale** sur un serveur FTP avec support des chemins absolus.

---

#### **Paramètres Principaux**

| **Paramètre**          | **Description**                                                                                     | **Exemple**                                         |
|-------------------------|-----------------------------------------------------------------------------------------------------|-----------------------------------------------------|
| `ftp_id` (facultatif)   | ID du serveur FTP où l'image finale sera téléversée.                                               | `1`                                                 |
| `template_url`          | URL de l'image modèle utilisée comme fond.                                                         | `https://example.com/template.jpg`                 |
| `image_url`             | URL de l'image principale à ajouter.                                                              | `https://example.com/image.jpg`                    |
| `result_file` (facultatif) | Chemin relatif ou absolu du fichier final sur le FTP.                                             | `output.jpg` ou `/dossier/output.jpg`              |
| `dpi` (facultatif)      | Résolution de l'image finale en DPI.                                                              | `300`                                              |
| `watermark_text` (facultatif) | Texte du filigrane à ajouter sur l'image.                                                      | `Confidential`                                      |
| `result_w` (facultatif) | Largeur en pixels de l'image finale, avec conservation du ratio.                                   | `800`                                              |

---

#### **Options pour la Transformation d'Images**

1. **Positionnement** (facultatif) : 
   - `x1`, `y1`, ..., `x10`, `y10` : Coordonnées (en %) pour positionner les images sur le modèle.
2. **Rotation** (facultatif) :
   - `r1`, ..., `r10` : Angle de rotation (en degrés).
3. **Redimensionnement** (facultatif) :
   - `w1`, ..., `w10` : Largeur de l'image en % de la largeur originale.
4. **Rognage** (facultatif) :
   - `dh1`, `db1`, ..., `dh10`, `db10` : Pourcentage de découpe en haut et en bas de l'image.
5. **Filtres** (facultatif) :
   - `c1`, ..., `c10` : Filtres appliqués (par exemple : `nb` pour noir et blanc, `cartoon` pour effet cartoon).

---

#### **Options pour le Texte (Nouveau Format)**

Les textes sont maintenant gérés sous forme de listes parallèles, permettant d'ajouter un nombre illimité de textes :

| **Paramètre**          | **Description**                                                                                     | **Exemple**                                         |
|-------------------------|-----------------------------------------------------------------------------------------------------|-----------------------------------------------------|
| `texts`                | Liste des textes à ajouter                                                                         | `texts=Bonjour&texts=Monde`                        |
| `text_x_positions`     | Liste des positions x (en %) pour chaque texte                                                     | `text_x_positions=10&text_x_positions=50`          |
| `text_y_positions`     | Liste des positions y (en %) pour chaque texte                                                     | `text_y_positions=90&text_y_positions=90`          |
| `text_fonts`           | Liste des polices pour chaque texte (arial, avenir, helvetica, verdana, tnr, roboto)              | `text_fonts=arial&text_fonts=helvetica`            |
| `text_colors`          | Liste des couleurs en hexadécimal pour chaque texte                                               | `text_colors=000000&text_colors=FF0000`           |
| `text_sizes`           | Liste des tailles en points pour chaque texte                                                      | `text_sizes=12&text_sizes=24`                      |

**Notes importantes sur les textes :**
- Toutes les listes de paramètres de texte doivent avoir la même longueur
- Les positions x et y sont en pourcentage (0-100)
- Les tailles de texte sont en points (1-100)
- Les couleurs doivent être en format hexadécimal (6 caractères)
- Si certains paramètres sont omis, des valeurs par défaut sont utilisées
- Pour créer une liste, répétez le même paramètre avec des valeurs différentes

---

#### **Exemple d'Utilisation**

**Requête HTTP :**
```http
GET /create_image/
?template_url=https://example.com/template.jpg
&image_url=https://example.com/image.jpg
&result_file=/dossier/final.jpg
&dpi=300
&watermark_text=Confidential
&x1=10&y1=10&w1=50
&texts=Bonjour
&texts=Monde
&text_x_positions=50
&text_x_positions=70
&text_y_positions=90
&text_y_positions=90
&text_fonts=arial
&text_fonts=helvetica
&text_colors=000000
&text_colors=FF0000
&text_sizes=20
&text_sizes=24
```

**Explication :**
1. Charge le modèle et une image depuis leurs URLs respectives
2. Positionne l'image à 10% des bords avec une largeur de 50%
3. Ajoute deux textes en répétant chaque paramètre :
   - Premier texte : "Bonjour" en noir, police Arial, taille 20, position (50%, 90%)
   - Deuxième texte : "Monde" en rouge, police Helvetica, taille 24, position (70%, 90%)
4. Applique un filigrane "Confidential"
5. Sauvegarde le résultat dans `/dossier/final.jpg` sur le FTP

---

#### **Gestion des Erreurs**

L'API effectue plusieurs validations :
- Vérification des positions (0-100%)
- Validation des tailles de texte (1-100)
- Validation des couleurs hexadécimales
- Vérification de la cohérence des listes de paramètres de texte
- Validation des chemins FTP"""


description_intercalaire = """
### Documentation pour l'Endpoint `GET /intercalaire/`

Cet endpoint permet de générer une image appelée "intercalaire". Cette image est constituée d'un arrière-plan de couleur personnalisée et d'un ou plusieurs blocs de texte positionnés à des emplacements spécifiques. L'image résultante peut être téléversée sur un serveur FTP.

---

#### **Fonctionnalités principales**
- **Création d'une image avec arrière-plan personnalisé** : Définissez la couleur, la largeur, et la hauteur.
- **Ajout de plusieurs blocs de texte personnalisés** : Position, taille, couleur, police, et alignement.
- **Téléversement de l'image sur un serveur FTP** : Téléchargez automatiquement l'image générée.

---

#### **Paramètres**

| **Paramètre**            | **Type**          | **Description**                                                                                     | **Exemple**                                       |
|---------------------------|-------------------|-----------------------------------------------------------------------------------------------------|--------------------------------------------------|
| `result_file` (facultatif)| `str`            | Nom du fichier résultant à générer.                                                               | `intercalaire.png`                               |
| `ftp_id`(facultatif)     | `str`             | Id du serveur FTP pour le téléversement de l'image.                                                | `ftp.example.com`                                |
| `background_color`       | `str`             | Couleur de l'arrière-plan au format hexadécimal.                                                   | `FFFFFF` (blanc), `000000` (noir)               |
| `width`                  | `int`             | Largeur de l'image en pixels.                                                                      | `800`                                            |
| `height`                 | `int`             | Hauteur de l'image en pixels.                                                                      | `600`                                            |
| `text1` (facultatif)     | `str`             | Texte du premier bloc. Utilisez `<br>` pour les sauts de ligne.                                    | `Première ligne <br>Deuxième ligne`             |
| `x1` (facultatif)        | `int`             | Position horizontale (en %) du premier bloc de texte.                                              | `10`                                             |
| `y1` (facultatif)        | `int`             | Position verticale (en %) du premier bloc de texte.                                                | `10`                                             |
| `font_size1` (facultatif)| `int`             | Taille de la police pour le premier bloc de texte.                                                 | `20`                                             |
| `color1` (facultatif)    | `str`             | Couleur du texte du premier bloc au format hexadécimal.                                            | `000000` pour noir, `FF0000` pour rouge         |
| `font_name1` (facultatif)| `str`             | Police utilisée pour le premier bloc de texte.                                                     | `arial`                                          |
| `align1` (facultatif)    | `str`             | Alignement du premier bloc de texte : `left`, `center`, ou `right`.                                | `left`                                           |

Répétez ces paramètres pour les blocs de texte supplémentaires (jusqu'à 5 blocs) en remplaçant `1` par `2`, `3`, etc. Exemples :
- `text2`, `x2`, `y2`, `font_size2`, `color2`, `font_name2`, `align2`.
- `text3`, ..., `text5`.

---

#### **Exemple d'Utilisation**

**Requête HTTP :**
```http
GET /intercalaire/
?result_file=intercalaire.png
&ftp_host=ftp.example.com
&background_color=FFFFFF
&width=800
&height=600
&text1=Première ligne<br>Deuxième ligne
&x1=10
&y1=10
&font_size1=20
&color1=000000
&font_name1=arial
&align1=left
&text2=Texte additionnel
&x2=50
&y2=30
&font_size2=25
&color2=FF0000
&font_name2=verdana
&align2=center
```

**Explication :**
1. **Arrière-plan blanc** de 800x600 pixels.
2. **Premier bloc de texte** : 
   - Texte : "Première ligne<br>Deuxième ligne"
   - Position : 10% en horizontal, 10% en vertical.
   - Taille : 20px, couleur noire (`000000`), police Arial, aligné à gauche.
3. **Deuxième bloc de texte** : 
   - Texte : "Texte additionnel"
   - Position : 50% en horizontal, 30% en vertical.
   - Taille : 25px, couleur rouge (`FF0000`), police Verdana, centré.
4. **Image téléversée sur le serveur FTP** à l'adresse `ftp.example.com`.

---

#### **Erreurs possibles**
- **Dimensions invalides** : Assurez-vous que `width` et `height` sont des entiers positifs.
- **Police non reconnue** : Si la police spécifiée n'est pas disponible, une police par défaut sera utilisée.
- **Surcharge FTP** : Vérifiez les permissions et la disponibilité du serveur FTP.
"""