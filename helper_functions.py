# -*- coding: utf-8 -*-
"""
@author: BELGADA Zainab
"""


# Fonction pour calculer la distance de Levenshtein
# Implémentation recursive basée sur le pseudocode :
# https://en.wikipedia.org/wiki/Levenshtein_distance#Recursive
def distance_de_Levenshtein(string1, string2):
    """
    Keyword arguments:
        string1 -- python string
        string2 -- python string
        
    return:
        un entier : Distance de Levenshtein entre string1 et string2. 
        Cette distance est d'autant plus grande que le nombre de différences entre les deux chaînes est grand.
    """
    n = len(string1)
    m = len(string2)
    if n == 0: return m    # il faut insérer m caractères pour construire string2
    if m == 0: return n    # il faut supprimer n caractères pour construire string2
    # pas de coût additionel si les premiers caractères sont les mêmes
    if string1[0] == string2[0]: return distance_de_Levenshtein(string1[1:], string2[1:]) 
    # sinon, essayer 3 actions possibles (inserer, supprimer, ou remplacer) et choisir la meilleur
    else:
        return 1 + min(
            distance_de_Levenshtein(string1, string2[1:]),    # insérer
            distance_de_Levenshtein(string1[1:], string2),    # supprimer
            distance_de_Levenshtein(string1[1:], string2[1:]) # remplacer
        )

        
# Fonction pour renvoyer une liste de dictionnaires
# Chaque dictionnaire représente un bureau de poste
# Implémentation par la méthode de compréhension de liste
def extraire_info(df, ids, cols):
    """
    Keyword arguments:
        df   -- pandas dataframe (from file data.csv)
        ids  -- a sequence of Identifiant_du_site (ID)
        cols -- a sequence of columns_names (e.g. Adresse, Code_postal, etc.)
        
    return:
        a list of dictionaries. Each dictionary contains information (cols) about a specific ID 
    """
    return [ df[df['Identifiant_du_site'] == id].iloc[0][cols].to_dict() for id in ids ]