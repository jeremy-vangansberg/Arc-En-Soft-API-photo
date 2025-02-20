13/02/2024
- Gestion des chemins absolus sur le FTP
- Suppression de la création des dossiers sur le ftp pour de l'upload
- Suppression du endpoint intercalaire/
- Ajout de la gestion des listes dans les paramètres de texte afin de pouvoir gérer un nombre infini de texte (pour remplacer le endpoint intercalaire)
- Suppression du Reverse Proxy Caddy (c'est déjà géré par EasyPanel ça faisait doublon)
- mis-à-jour de la documentation


17/02/2024
- gestion de image_url sous forme de liste
- nom des arguments : ajout des prefix image_
- validation : il faut désormais mettre une valeur pour chaque paramètre associé à la liste :
image_url 
image_x 
image_y 
image_width 
image_rotation -> Valeur à mettre pour ne pas appliquer de rotation : 0
image_filter -> Valeur à mettre pour ne pas appliquer de filtre : none
image_crop_top -> Valeur à mettre pour ne pas rognage : 0
image_crop_bottom -> Valeur à mettre pour ne pas rognage : 0


20/02/2024
- Optimisation majeure du système de logs
- Mise en place d'un buffer de logs pour réduire les connexions FTP
- Passage au format JSONL pour les logs
- Suppression des fichiers temporaires pour les logs
- Ajout d'un système de flush automatique des logs

21/02/2024
- Correction des tests unitaires :
  - Problème de mock Celery pour reset_queue
  - Erreur d'accès à PIL.Image.resize
  - Tests de rendu de texte échoués (qualité, multiline, DPI)
- Mise à jour des dépendances dans le container de test

22/02/2024
- Amélioration majeure de la gestion des polices :
  - Correction des chemins des polices dans le conteneur Docker (/app/fonts/)
  - Mise en place d'un système de polices de secours en cascade :
    * Tentative de chargement de la police demandée
    * Si échec, tentative de chargement d'Arial comme police de secours
    * En dernier recours, utilisation de la police système avec mise à l'échelle
  - Amélioration du rendu avec la police par défaut :
    * Ajout d'un facteur d'échelle pour respecter la taille demandée
    * Support du texte multiligne avec espacement proportionnel
    * Gestion correcte des alignements (gauche, centre, droite)
  - Ajout de logs détaillés pour le chargement des polices
  - Ajout de tests unitaires complets :
    * Test du système de polices de secours
    * Test de la mise à l'échelle avec la police par défaut
    * Test du support multiligne
    * Test des alignements de texte