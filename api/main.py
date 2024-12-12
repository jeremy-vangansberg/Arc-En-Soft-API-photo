from fastapi import FastAPI
from router import image, intercalaire

description= """
### Documentation Améliorée de l'API de Traitement d'Images

L'API permet de traiter et de personnaliser des images en utilisant différents paramètres fournis par l'utilisateur. L'objectif est de générer une image finale combinant un modèle de fond, une image principale, des textes personnalisés, et éventuellement des filigranes (watermarks). L'image résultante peut être uploadée sur un serveur FTP.
"""

app = FastAPI(description=description)
app.include_router(image.router)
app.include_router(intercalaire.router)



