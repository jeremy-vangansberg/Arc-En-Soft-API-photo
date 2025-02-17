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