# -*- coding: utf-8 -*-
"""
@author: BELGADA Zainab
"""


import numpy as np
import pandas as pd


# Fonction pour lire, nettoyer, et transformer le fichier laposte_poincont.csv
# Contenu  : Liste des services disponibles en bureaux de poste...
# Lien     : https://www.data.gouv.fr/fr/datasets/r/04ebbfe3-25ae-42bd-bd69-8fde1d548e45
def get_basic_info_and_services(file_path, p_cities, random_seed):
    """
    Keyword arguments:
        file_path    -- string, chemin vers le fichier laposte_poincont.csv (e.g. './data/laposte_poincont.csv')
        p_cities     -- float, fraction des localités à extraire (afin de réduire la taille du fichier source)
        random_seed  -- integer, (afin d'assurer la reproductibilité de l'échantillonnage)
        
    return:
        pandas dataframe
    """
    # Lire le fichier en pandas dataframe
    services = pd.read_csv(file_path, sep=';', header=0, low_memory=False)
    # Supprimer les bureaux de postes qui n'ont pas une adresse
    services.dropna(subset=['Adresse'], inplace=True)
    # Renommer la colonne '#Identifiant_du_site'
    services.rename(columns={'#Identifiant_du_site': 'Identifiant_du_site'}, inplace=True)
    # Supprimer les colonnes qui ne seront pas utilisé dans notre application
    services.drop(['Complément_d_adresse', 'Lieu_dit', 'Pays', 'Précision_du_géocodage', 'latlong'], axis=1, inplace=True)
    # Extraire les noms de localités disponibles dans le dataset
    unique_cities = services['Localité'].unique()
    # définir un random seed pour numpy (afin de permettre la reproductibilité du résultat de l'échantillonnage)
    np.random.seed(random_seed)
    # définir la taille de l'échantillon
    n_cities = int(unique_cities.shape[0] * p_cities)
    # échantillonnage des localités
    n_random_cities = np.random.choice(unique_cities, size=n_cities, replace=False)
    # filtrer les données (garder uniquement les données de l'échantillon)
    return services[services['Localité'].isin(n_random_cities)]


# Fonction pour lire, nettoyer, et transformer le fichier laposte_poincont2.csv
# Contenu : Liste des bureaux de poste, agences postales et relais poste
# Lien    : https://www.data.gouv.fr/fr/datasets/r/14990cf8-b618-42fe-a73d-92587b34ed46
def get_bureau_poste_type(file_path):
    """
    Keyword arguments:
        file_path -- string, chemin vers le fichier laposte_poincont2.csv (e.g. './data/laposte_poincont2.csv')
        
    return:
        pandas dataframe
    """
    # Lire le fichier en pandas dataframe
    caracteristics = pd.read_csv(file_path, sep=';', header=0, low_memory=False)
    # Renommer la colonne '#Identifiant_du_site'
    caracteristics.rename(columns={'#Identifiant_du_site': 'Identifiant_du_site'}, inplace=True)
    # On aura besoin que de 2 variables uniquement : Identifiant_du_site et Caractéristique_du_site
    return caracteristics[['Identifiant_du_site', 'Caractéristique_du_site']]


# Fonction pour lire, nettoyer, et transformer le fichier laposte_ouvertur.csv
# Contenu : Calendrier d’ouverture des bureaux de poste...
# Lien    : https://www.data.gouv.fr/fr/datasets/r/6f78a031-af14-4e5e-91a3-6417874d2d90
def get_opening_hours(file_path):
    """
    Keyword arguments:
        file_path -- string, chemin vers le fichier laposte_ouvertur.csv (e.g. './data/laposte_ouvertur.csv')
        
    return:
        pandas dataframe
    """
    # Lire le fichier en pandas dataframe
    horaires = pd.read_csv(file_path, sep=';', header=0, low_memory=False)
    # Renommer la colonne '#Identifiant_du_site'
    horaires.rename(columns={'#Identifiant_du_site': 'Identifiant_du_site'}, inplace=True)
    # Changer le type de la colonne Date_calendrier (afin de pouvoir manipuler des dates)
    horaires['Date_calendrier'] = pd.to_datetime(horaires['Date_calendrier'], format='%Y-%m-%d')
    # On aura besoin que de 7 variables uniquement
    return horaires[['Identifiant_du_site', 'Date_calendrier', 'Plage_horaire_1', 'Plage_horaire_2', 
                     'Heure_limite_dépôt_Courrier', 'Heure_limite_dépôt_Chrono', 'Heure_limite_dépôt_Colis']]


# Fonction pour préparer le dataset final qui sera utilisée dans notre application
# C'est le résultat de la fusion de trois source de données : 
#   - laposte_poincont.csv
#   - laposte_poincont2.csv
#   - laposte_ouvertur.csv
# La colonne 'Identifiant_du_site' est utilisé comme clé de fusion
def merge_datasets(p_cities=0.014, random_seed=1, services_file='./data/laposte_poincont.csv', 
                   bureaux_poste_file='./data/laposte_poincont2.csv', 
                   opening_hours_file='./data/laposte_ouvertur.csv', save_to='./data/data.csv'):
    """
    Keyword arguments:
        p_cities            -- float, fraction des localités à extraire. Mettre 1 afin de fonctionner le projet avec le dataset complet. 
        random_seed         -- integer, (afin d'assurer la reproductibilité de l'échantillonnage)
        services_file       -- string, chemin vers le fichier laposte_poincont.csv
        bureaux_poste_file  -- string, chemin vers le fichier laposte_poincont2.csv
        opening_hours_file  -- string, chemin vers le fichier laposte_ouvertur.csv
        save_to             -- string spécifiant le chemin où sauvgarder le dateset final. None si on ne souhaite pas sauvgarder dans le disque.
    
    return:
        pandas dataframe (NB: également sauvgarder en format csv si l'argument save_to n'est pas None)
    """
    # Lire les 3 fichiers en utilisant les fonctions définies en haut
    try:
        bureau_poste_services = get_basic_info_and_services(file_path=services_file, p_cities=p_cities, 
                                                            random_seed=random_seed)
        bureau_poste_type = get_bureau_poste_type(bureaux_poste_file)
        opening_hours = get_opening_hours(opening_hours_file)
    except FileNotFoundError:
        print("Veuillez d'abord télécharger les 3 fichiers sources utilisés dans ce projet et les mettre dans les chemins précisés en argument.")
        print("Fichier 1 : laposte_poincont.csv   --->  Lien : https://www.data.gouv.fr/fr/datasets/r/04ebbfe3-25ae-42bd-bd69-8fde1d548e45")
        print("Fichier 2 : laposte_poincont2.csv  --->  Lien : https://www.data.gouv.fr/fr/datasets/r/14990cf8-b618-42fe-a73d-92587b34ed46")
        print("Fichier 3 : laposte_ouvertur.csv   --->  Lien : https://www.data.gouv.fr/fr/datasets/r/6f78a031-af14-4e5e-91a3-6417874d2d90")
        return None
    # Fusion des 3 dataframes
    # how='left' nous permet de garder que les localités disponibles dans le dataframe bureau_poste_services
    # puisque c'est dans ce dataframe où on a procéder à l'échantillonnage (argument p_cities) 
    data = pd.merge(bureau_poste_services, bureau_poste_type, on='Identifiant_du_site', how='left')
    data = pd.merge(data, opening_hours, on='Identifiant_du_site', how='left')
    # sauvgarder une copie sur le disque (format csv)
    if save_to is not None:
        data.to_csv(save_to, index=False)
    return data


# Permet d'exécuter ce script afin de préparer le dataset final
# Doit être exécuter avant de lancer l'application flask (app.py)
# par défaut p_cities=0.014 (1.4%, ce qui correspond à 188 localités au total)
# Mettre p_cities=1 permet de fonctionner le projet avec le dataset complet.
if __name__ == '__main__':
    merge_datasets()




























