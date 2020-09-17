# -*- coding: utf-8 -*-
"""
@author: BELGADA Zainab
"""

import numpy as np
import pandas as pd
from flask import Flask, render_template, request
from datetime import datetime
from helper_functions import distance_de_Levenshtein, extraire_info


# Permet d'éviter un faux warning de pandas (false positive)
# source 1 : https://www.dataquest.io/blog/settingwithcopywarning/
# source 2 : https://stackoverflow.com/questions/20625582/how-to-deal-with-settingwithcopywarning-in-pandas
pd.set_option('mode.chained_assignment', None)


# Load dataset into a pandas dataframe
# data.csv est préparé en utilisant la fonction merge_datasets() 
# définie dans le fichier preprocess.py
data = pd.read_csv('./data/data.csv', sep=',', header=0, low_memory=False)


app = Flask('laposte')


# Affiche la page d'accueil
@app.route('/')
def index():
    return render_template('index.html')


# Affiche les résultats de recherche
# Recherche par ville : On affiche soit la liste des bureaux de poste disponible
# dans la localité saisie par l'utilisateur OU bien une liste de suggestions de ville
# si l'utilisateur opte pour une recherche approchée
@app.route('/search')
def display_search_results():
    # extraire le nom de la ville recherché par l'utilisateur
    # et le transformé en majuscule (même format que le champ Localité dans le dataframe) 
    nom_ville = request.args.get('nom_ville').upper()
    # Afficher un message personalisé si l'utilisateur saisi un nom de ville non valide 
    # (chaîne de caractère vide. A améliorer pour tenir compte d'autre cas)
    if nom_ville.strip() == '': 
        message = 'Veuillez saisir un nom de localité valide.'
        return render_template('results.html', message=message, bureaux_disponibles=None, nom_ville=nom_ville)
    # Si l'utilisateur souhaite faire une recherche par nom de ville incomplet
    # On affiche d'abord une liste des noms de ville qui contiennent la partie saisie
    # puis on classe les résultats obtenus par le score de Levenshtein
    elif request.args.get('resultats_approches') == 'true':
        # Liste des noms de ville (unique)
        villes_disponibles = pd.DataFrame({'Localité': data['Localité'].unique()})
        # Extraire les noms de ville qui contiennent le nom incomplet saisi par l'utilisateur
        suggestions_villes = villes_disponibles[villes_disponibles['Localité'].str.contains(nom_ville, case=False, regex=False)]
        suggestions_count = suggestions_villes.shape[0]
        # Message personalisé si on trouve pas de résultats similaires
        if suggestions_count == 0:
            message = 'Désolé ! Aucun résultat ne correspond à votre recherche.'
        # Sinon, classer les suggestion par score de Levenshtein
        else:
            # On définit une version "vectorisé" de la fonction distance_de_Levenshtein
            # afin de l'appliquer à chaque élément de l'array suggestions_villes['Localité']
            vect_distance_de_Levenshtein = np.vectorize(distance_de_Levenshtein)
            # Calculer Levenshtein Score
            suggestions_villes['Levenshtein_Score'] = vect_distance_de_Levenshtein(suggestions_villes['Localité'], nom_ville)
            suggestions_villes.sort_values('Levenshtein_Score', inplace=True)
            message = 'Nous avons trouvés {} {} à votre requête. '.format(suggestions_count, 'seule localité similaire' if suggestions_count == 1 else 'localités similaires')
            if suggestions_count == 1: 
                message += 'La voici :'
            elif suggestions_count <= 10:
                message += 'Les voici classées par score de Levenshtein :'
            else:
                # Si y a plusieurs suggestions (> 10), afficher uniquement les 10 premières
                # (ayant une score faible, donc plus proches de la requête)
                suggestions_villes = suggestions_villes.head(n=10)
                message += 'Voici les top 10 suggestions classées par score de Levenshtein :'
        return render_template('levenshtein_results.html', message=message, nom_ville=nom_ville, suggestions_count=suggestions_count, suggestions_villes=suggestions_villes.to_dict('records'))
    else:
        # L'utilisateur ne coche pas l'option de recherche approcheé 
        # donc souhaite de rechercher exactement le nom de ville saisi
        # Dans ce cas, on affiche directement la liste des bureaux de poste disponible dans cette ville
        ville_data = data[data['Localité'] == nom_ville]
        unique_bureaux = ville_data['Identifiant_du_site'].unique()
        count_results = unique_bureaux.shape[0]
        if count_results >= 1:
            message = 'Il y a ' + ('1 seul bureau' if count_results == 1 else '{} bureaux'.format(count_results))
            message += ' de poste à {}.'.format(nom_ville)
            bureaux_disponibles = extraire_info(data, unique_bureaux, ['Identifiant_du_site', 'Adresse'])
            return render_template('results.html', message=message, nom_ville=nom_ville, bureaux_disponibles=bureaux_disponibles)
        # Message personalisé si on trouve pas de résultats pour la localité saisie par l'utilisateur
        else:
            message = "Désolé ! Aucun bureau de poste n'a été trouvé dans cette localité."
            return render_template('results.html', message=message, nom_ville=nom_ville, bureaux_disponibles=None)


# Affiche des informations sur un bureau de poste spécifique
# ex. Localisation (avec lien Google Maps), 
# Calendrier d'ouverture dans les prochains 15 jours...
@app.route('/details/<identifiant_du_site>')
def show_details(identifiant_du_site):
    # filtrer le dataset pour garder uniquement les lignes qui correspondent à 
    # identifiant_du_site en question. NB: le dataset contient 3 mois de données par identifiant
    # (qui correspondent à l'horaire d'ouverture dans les prochains 3 mois)
    data_subset = data[data['Identifiant_du_site'] == identifiant_du_site]
    # Pour extraire des informations basiques (localisation, services disponibles...), on aura 
    # besoin que de la première ligne. 
    info = data_subset.iloc[0].to_dict()
    # Extraire les horaires d'ouvertures pour les prochains 15 jours
    # Pour ce faire, on aura besoin de la date d'aujourd'hui
    data_subset['Date_calendrier'] = pd.to_datetime(data_subset['Date_calendrier'], format='%Y-%m-%d')
    data_subset = data_subset.sort_values(['Date_calendrier'])
    current_date = datetime.today().strftime('%Y-%m-%d')
    horaires = data_subset[data_subset['Date_calendrier'] >= current_date].iloc[0:15]
    horaires['Date_calendrier'] = horaires['Date_calendrier'].dt.date
    horaires = horaires[['Date_calendrier', 'Plage_horaire_1', 'Plage_horaire_2', 
                         'Heure_limite_dépôt_Courrier', 'Heure_limite_dépôt_Chrono', 'Heure_limite_dépôt_Colis']]
    # Afin d'afficher '-' au lieu de 'Nan' dans les horaires pour les jours de fermeture
    horaires.fillna('-', inplace=True)
    return render_template('details.html', info=info, days=horaires.to_dict('records'))


# Affiches les 100 premières villes du dataset classées par nombre de bureaux 
# de poste disponibles
@app.route('/cities')
def show_cities():
    # nombre de villes disponibles dans le dataset
    number_of_cities = data['Localité'].unique().shape[0]
    # Calcule le nombre de bureaux de poste par ville
    # NB: on fait appel a nunique() au lieu de count() car chaque identifiant et représenté par 
    # 3 mois de données (horaire d'ouverture dans le 3 prochains mois)
    top_n = data.groupby('Localité')['Identifiant_du_site'].nunique().sort_values(ascending=False)[:100].to_dict()
    # Classer les villes par le nombre de bureaux de poste
    top_n = sorted(list(top_n.items()), key=lambda tup: -tup[1])
    return render_template('cities.html', number_of_cities=number_of_cities, top_n=top_n)


if __name__ == '__main__':
    app.run(debug=True)



















