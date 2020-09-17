Plateforme
===========
- Windows 8.1 Professionnel
- Conda 4.8.2
- Python 3.7.6

Python Packages
===============
1. numpy
2. pandas
3. flask
3. datetime

Pour lancer l'application avec l'échantillon de données préparé
===============================================================
Exécuter la commande :  
  
`> python app.py`  

Pour lancer l'application avec toutes les villes (ou un échantillon plus grand)
==============================================================================
1. Télécharger les 3 fichiers sources dans le sous-dossier `data` (warning : plus de 137 Mo) :   
  
	- [laposte_poincont.csv](https://www.data.gouv.fr/fr/datasets/r/04ebbfe3-25ae-42bd-bd69-8fde1d548e45)
	- [laposte_poincont2.csv](https://www.data.gouv.fr/fr/datasets/r/14990cf8-b618-42fe-a73d-92587b34ed46)
	- [laposte_ouvertur.csv](https://www.data.gouv.fr/fr/datasets/r/6f78a031-af14-4e5e-91a3-6417874d2d90)		

2. Dans le fichier `preprocess.py`, la ligne 130, préciser la fraction des villes à utiliser en modifiant l'argument `p_cities` de la fonction `merge_datasets()`. Par exemple, `merge_datasets(p_cities=1)` permet d'utiliser le dataset complet. Par défaut, j'ai utilisé p_cities=0.014 (1.4%) afin de limiter la taille du dataset à < 5 Mo (4.75 Mo exactement).

3. Vous pouvez également modifier d'autres arguments tels que les chemins vers les fichiers sourcent, la random seed...

4. Exécuter la commande :  
  
	`> python preprocess.py` 

5. Un fichier `data.csv` sera sauvegardé dans le sous-dossier `data`. Vous pouvez désormais lancer l'application en exécutant la commande :    
  
	`> python app.py`
