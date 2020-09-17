[![Build Status](https://travis-ci.com/belzaina/postefrance.svg?branch=master)](https://travis-ci.com/belzaina/postefrance)

Motivations
===========
  
L’objectif est de développer une application Flask permettant la recherche et l’affichage des points de contact du réseau postal français. 

Lien
===========
https://postefrance.herokuapp.com/
  
Points Importants
==================
  
À partir d’une interface utilisateur simple et intuitive, l’utilisateur peut :

### 1. Effectuer une recherche par nom de localité (ex. ST JOSEPH)  
  
Dans ce cas l’application affiche la liste des bureaux de poste disponible dans cette localité. L’utilisateur peut ensuite cliquer sur un bureau de poste parmi cette liste afin d’afficher :  
	  
- Des informations d’ordre général sur ce bureau de poste (ex. Libellé, type, code INSEE, etc.) ;
- Sa localisation avec un lien pour le montrer sur **Google Maps** ;
- Les services disponibles dans ce bureau de poste ;
- Les services proposés aux personnes à mobilité réduite ;
- Son calendrier d’ouverture dans les 15 prochains jours.
  
Si aucune localité ne correspond à la recherche de l’utilisateur, l’application propose à l’utilisateur 3 alternatives :

- Un lien pour consulter la liste des localités disponibles (affichage limité à 100 lignes ; on affiche donc la liste des 100 premières localités classées par nombre de bureaux de poste).
- Vérifier l’orthographe des termes de sa recherche ;
- Effectuer une recherche approximative (cocher l’option `Rechercher des résultats approchés ?`).

### 2. Effectuer une recherche approximative (distance de Levenshtein)  
  
En cas de doute concernant le nom exact de la localité recherchée, l’utilisateur peut écrire juste une fraction du nom dans la barre de recherche (ex. jo) puis cocher l’option `Rechercher des résultats approchés ?`.  

Dans ce cas, l’application procède comme suivant :  
  
- Filtrer la liste les localités disponibles en gardant uniquement ceux dont le nom contient la fraction saisie par l’utilisateur (liste des suggestions) ;
- Ordonner la liste des suggestions par la **distance de Levenshtein** afin d’afficher les suggestions les plus proches à la requête de l’utilisateur en premier. 

Démarche
========
  
### 1. La préparation du dataset  

Le jeu de données des [points de contact du réseau postal français](https://www.data.gouv.fr/fr/datasets/liste-des-points-de-contact-du-reseau-postal-francais-horaires-equipements-et-services-associes/#_) propose cinq ressources :
  
- [laposte_poincont.csv](https://www.data.gouv.fr/fr/datasets/r/04ebbfe3-25ae-42bd-bd69-8fde1d548e45)
- [laposte_poincont2.csv](https://www.data.gouv.fr/fr/datasets/r/14990cf8-b618-42fe-a73d-92587b34ed46)
- [laposte_ouvertur.csv](https://www.data.gouv.fr/fr/datasets/r/6f78a031-af14-4e5e-91a3-6417874d2d90) 
- [laposte_autompre.csv](https://www.data.gouv.fr/fr/datasets/r/beb7d6e9-90a7-4ebe-9bbc-c584fa5f2cb9)
- [laposte_handicap.csv](https://www.data.gouv.fr/fr/datasets/r/8ca00d57-df2b-4c21-8780-ff372ccbee04)
  
Cependant, après une analyse exploratoire de chaque ressource (avec pandas dans un jupyter notebook), j’ai décidé d’utiliser uniquement les 3 premières ressources, car :  
  
- Les informations sur les services proposés aux PMR (ressource laposte_handicap.csv) et  
- La liste des automates (ressource laposte_autompre.csv)

on peut les obtenir aussi depuis la première ressource (liste des services : laposte_poincont.csv). 
    
Dans le fichier `preprocess.py`, j’ai défini 4 fonctions afin de préparer le dataset final qui sera utilisé par l’application :
  
- La fonction ’get_basic_info_and_services’ permet de lire et nettoyer les données du fichier ’laposte_poincont.csv` ; elle permet aussi d’effectuer un échantillonnage aléatoire afin de réduire la taille du dataset final (< 5 Mo)
- La fonction ’get_bureau_poste_type’ permet de lire et nettoyer les données du fichier `laposte_poincont2.csv`
- La fonction ’get_opening_hours’ permet de lire et nettoyer les données du fichier ’laposte_ouvertur.csv`
- La fonction ’merge_datasets’ permet de fusionner les trois datasets et sauvegardé le résultat dans le fichier `data.csv` (c’est ce fichier qui sera exploité par l’application Flask)
  

### 2. L’application Flask
  
Pour lancer l’application, il suffit de l’exécuter la commande :  

`python app.py`
  
Pour lancer l’application avec le dataset complet (ou un échantillon plus grand), veuillez suivre les étapes décrites dans le fichier `INSTALL.md`.
  
Améliorations Possibles Futures
===============================
- Optimiser la fonction ’distance_de_Levenshtein’ (définis dans le fichier ’helper_functions.py`) : Pour calculer la distance entre la requête de l’utilisateur et toutes les localités disponibles dans le dataset, cette implémentation prend un peu de temps (quelques secondes). Pour cette raison, j’ai limité l’espace de recherche aux noms de localités qui contiennent la fraction du mot saisi par l’utilisateur. 
- Couvrir autres cas d’input non valide saisi par l’utilisateur : Dans cette version on teste uniquement si la chaîne de caractère saisi est non vide. Il faut aussi tester si la requête contient des nombres, caractères spéciaux, etc.