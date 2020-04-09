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
from fonctions_index import litTexteDuFichier, ecritTexteDansUnFichier, lemmatiseTexte, normaliseTokens, normaliseTokensRequete, lemmatiseTokensRequete

PARSEUR = 'TALISMANE'
   
fiIndex = "./_index/indexInverse"
fiDocs = "./_index/indexDocuments"
doCorpus = "../corpus/miniCorpus/FR/"
corpus_sansBalise = "../corpus/sans_balises"

fiTxt = "./_log/tempo.txt" 

fiLog = "./_log/requete.log"
log = ""


indexDocuments = dict()
indexInverse = dict ()

# 0. lecture des index
if os.path.isfile (fiDocs) :
    with open(fiDocs, 'rb') as FI :
        #indexDocuments = pickle.load(FI)
        indexDocuments = json.load(FI)
    print ("index de cuduments bien lu")

if os.path.isfile (fiIndex) :
    with open(fiIndex, 'rb') as FI :
        #indexInverse = pickle.load(FI)
        indexInverse = json.load(FI)
    print ("index inversé bien lu")
 
# 1. lecture de la requête (mots clés)
print("votre requête ?")
requete = input()
print("...", requete)
log += "\nrequête: %s \n" % (requete)

# 2. extraction de ses tokens (lemmatisation, normalisation)
ecritTexteDansUnFichier (requete, fiTxt)   
tokens = lemmatiseTokensRequete (fiTxt)
termes = normaliseTokensRequete (tokens)
log += "\ntermes: %s \n" % (termes)

# 3. recherche tous les termes sans tenir compte des symboles dans l'index et stocker le résultat
nbMatch = dict ()
for terme in termes:
    # pour chaque terme de la requête
    if terme in indexInverse:
        for liste in indexInverse[terme]:
            if nbMatch.__contains__(liste[0]):
                nbMatch[liste[0]][terme] = liste[1]
            else:
                valeur = {terme:liste[1]}
                nbMatch[liste[0]] = valeur

log += "\nrésultat: %s \n" % (str (nbMatch) )


# 4. filtrer les résultats en fonctions des symboles "+" et "-"
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

def filtrage_resultats(document):
    termes = document[1]
    if all(terme in termes for terme in termes_inclure) == False:
        return False
    if any(terme in termes for terme in termes_exclure):
        return False
    return True

nbMatch_filtre = dict(filter(filtrage_resultats, nbMatch.items()))
log += "\nrésultats filtrés: %s\n" % str(nbMatch_filtre)


# 5. affichage des résultats
log += "\nrésultats détaillées: \n"
print("{nombre} documents ont été trouvés!\n".format(nombre=len(nbMatch_filtre)))
print(nbMatch_filtre)

for doc, nb in nbMatch_filtre.items():#sorted(nbMatch.items(), key=lambda item: item[0], reverse=True) :
    info_document = indexDocuments[str(doc)]
    #print(f"{info_document} --> {nb}")
    nom_fichier = info_document[0]
    titre_complet = info_document[1]

    if "\n\n" in titre_complet:
        titre_principal = titre_complet[:titre_complet.index("\n\n")]
        sous_titre = titre_complet[titre_complet.index("\n\n")+2:]
        log += f"nom de fichier: {nom_fichier}\n titre de texte: {titre_principal}\n sous-titre: {sous_titre}\n termes trouvés dans ce fichier: {nb}\n\n"
    else:
        log += f"nom de fichier: {nom_fichier}\n titre de texte: {titre_complet}\n termes trouvés dans ce fichier: {nb}\n\n"

# 6. calculer les scores avec TF-IDF






# sauvegarde du log
ecritTexteDansUnFichier (log, fiLog)