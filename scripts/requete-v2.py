#!/usr/bin/env python
# coding: utf-8

# -------------------------------------------------------------------------------------------------------------
#   python3 requete-v1.py
#
#   Traitement d'une requête :
#       0. lecture fichier des index (inversé & documents)
#       1. lecture de la requête
#       2. extraction de ses tokens 
#       - lemmatisation
#       - normalisation 
#       3. recherche des documents correspondants dans l'index
#           par comptage des matchs
#       4. affichage des résultats
# 
#   remarque :  ne donne pas d'info sur les termes trouvés
# -------------------------------------------------------------------------------------------------------------

import os
import sys
import re
import pickle 
import json
from fonctions_index import litTexteDuFichier, ecritTexteDansUnFichier, lemmatiseTexte, normaliseTokens, normaliseTokensRequete, lemmatiseTermes

PARSEUR = 'TALISMANE'
   
fiIndex = "./_index/indexInverse"
fiDocs = "./_index/indexDocuments"
doCorpus = "../corpus/miniCorpus/FR/"
corpus_sansBalise = "../corpus/sans_balises"

fiTxt = "./_log/tempo.txt" 

fiLog = "./_log/requete.log"
log = ""


#fonction pour lire le fichier indexDocument
def litIndexDocument(fichier):
    indexDocuments = dict()
    if os.path.isfile (fichier) :
        with open(fichier, 'rb') as FI :
            indexDocuments = json.load(FI)
    return indexDocuments

#fonction pour lire le fichier indexInverse
def litIndexInverse(fichier):
    indexInverse = dict ()
    if os.path.isfile (fichier) :
        with open(fichier, 'rb') as FI :
            indexInverse = json.load(FI)
    return indexInverse
 
#trier les termes saisis pour faire la reqête en trois parties
def trierTermesDeRequete(requete):
    termes_inclure = []
    termes_exclure = []
    termes_optionnel = []

    termes_avec_ponc = list(requete.split(" "))
    for terme in termes_avec_ponc:
        if terme.startswith("+"): 
            termes_inclure.append(terme[1:])
        elif terme.startswith("-"): 
            termes_exclure.append(terme[1:])
        else: termes_optionnel.append(terme)

    termes_totals = termes_inclure+termes_exclure+termes_optionnel
    return termes_totals, termes_inclure, termes_exclure, termes_optionnel


#recherche tous les termes dans l'index et stocker le résultat, retourne un résultat brut
def requeteDesTermes(termes, fichier_indexInverse):
    resultat_requete = dict ()
    for terme in termes:
        if terme in fichier_indexInverse:
            for liste in fichier_indexInverse[terme]:
                if resultat_requete.__contains__(liste[0]):
                    resultat_requete[liste[0]][terme] = liste[1]
                else:
                    valeur = {terme:liste[1]}
                    resultat_requete[liste[0]] = valeur
    return resultat_requete


#filtrer les résultats en fonctions des symboles "+" et "-"
def filtrerLeResultat(resultat_brut, termes_a_inclure, termes_a_exclure):
    def detecterLesTermes(document):
        termes = document[1]
        if all(terme in termes for terme in termes_a_inclure) == False:
            return False
        if any(terme in termes for terme in termes_a_exclure):
            return False
        return True
    nbMatch_filtre = dict(filter(detecterLesTermes, resultat_brut.items()))
    return nbMatch_filtre


def standardiseLesTermes(liste):
    liste = lemmatiseTermes(liste)
    liste = normaliseTokensRequete(liste)
    return liste

# 6. calculer les scores avec TF-IDF



#----------------------------------main-------------------------------------------

#lire les fichiers de l'index de documents et l'index inversé
indexDocuments = litIndexDocument(fiDocs)
indexInverse = litIndexInverse(fiIndex)

#input la requête
print("votre requête ?")
requete = input()
print("votre requête est: ", requete)
log += "\nrequête: %s \n" % (requete)

#stocker les termes triés
termes_totals, termes_inclure, termes_exclure, termes_optionnel = trierTermesDeRequete(requete)
print(f"所有的词{termes_totals},必须的词{termes_inclure},避免的词{termes_exclure},无所谓{termes_optionnel}")
termes_totals_string = " ".join(termes_totals)
ecritTexteDansUnFichier (termes_totals_string, fiTxt) 

#lematiser et normaliser tous les termes de requête
tokens = lemmatiseTermes(termes_totals)
termes_totals_a_chercher = normaliseTokensRequete (tokens)
log += "\ntermes: %s \n" % (termes_totals_a_chercher)

#lamatiser et normaliser les termes iclures et les termes exculres
termes_inclure_final = standardiseLesTermes(termes_inclure)
termes_exclure_final = standardiseLesTermes(termes_exclure)
termes_optionnel_final = standardiseLesTermes(termes_optionnel)

#faire la reqête, chercher tous les documents qui comprennent tous les termes saisis, on obtient un résultat brut
nbMatch = requeteDesTermes(termes_totals_a_chercher, indexInverse)
log += "\nrésultat: %s \n" % (str(nbMatch))

#filtrer le résultat brut en fonction des symboles "+" et "-"
nbMatch_final = filtrerLeResultat(nbMatch, termes_inclure_final, termes_exclure_final)
log += "\nrésultats filtrés: %s\n" % str(nbMatch_final)

#affichage du résultat dans le terminal
print("\n{nombre} documents ont été trouvés!\n".format(nombre=len(nbMatch_final)))
print(nbMatch_final)


#extraire les sous-titres s'ils existent et les stocker dans "log"
log += "\nrésultats détaillées: \n"
for doc, nb in nbMatch_final.items():#sorted(nbMatch.items(), key=lambda item: item[0], reverse=True) :
    info_document = indexDocuments[str(doc)]
    nom_fichier = info_document[0]
    titre_complet = info_document[1]

    if "\n\n" in titre_complet:
        titre_principal = titre_complet[:titre_complet.index("\n\n")]
        sous_titre = titre_complet[titre_complet.index("\n\n")+2:]
        log += f"nom de fichier: {nom_fichier}\n titre de texte: {titre_principal}\n sous-titre: {sous_titre}\n termes trouvés dans ce fichier: {nb}\n\n"
    else:
        log += f"nom de fichier: {nom_fichier}\n titre de texte: {titre_complet}\n termes trouvés dans ce fichier: {nb}\n\n"



# sauvegarde du log
ecritTexteDansUnFichier (log, fiLog)