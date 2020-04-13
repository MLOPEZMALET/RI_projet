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
import numpy as np
from numpy import dot
from numpy.linalg import norm

import os
import sys
import math
import re
import pickle 
import json
from fonctions_index import litTexteDuFichier, ecritTexteDansUnFichier, lemmatiseTexte, normaliseTokens, normaliseTokensRequete, lemmatiseTermes

   
fiIndex = "./_index/indexInverse"
fiDocs = "./_index/indexDocuments"
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




#---------------les fonctions pour la parite scores avec TF-IDF----------------------
#créer une matrice avec les documents en ligne, les termes en colonne. 
#et dans la case, l'occurence d'un terme dans un document 
def creerMatrice(document_index, index_inverse):
    #créer une liste de tous les termes 
    listeDesTermes = []
    for terme in index_inverse:
        listeDesTermes.append(terme)

    #créer une matrice
    matrice = np.zeros([len(document_index),len(index_inverse)])

    #ajouter les occurrences dans la matrice
    for doc in document_index:
        for terme in index_inverse:
            for couple in index_inverse.get(terme):
                if str(couple[0]) == doc:
                    matrice[int(doc), listeDesTermes.index(terme)] = couple[1]
    return matrice

#créer la matrice avec les valeurs tf-idf de chaque terme
def TFIDF(matrice):
    matrice_TFIDF = np.zeros(matrice.shape)
    for i in range (matrice.shape[0]):
        for j in range (matrice.shape[1]):
          tf = matrice[i,j]
          idf = math.log(matrice.shape[0] /(np.count_nonzero(matrice[:,j])))  
          matrice_TFIDF[i,j] = tf * idf 
    return matrice_TFIDF


#retourner le idf de tous les termes dans indexInverse
def getIDF(doc_indexInverse, doc_indexDocuments):
    dicIDF = {}
    for terme in doc_indexInverse:
        idf = math.log(len(doc_indexDocuments) / len(doc_indexInverse[terme]))
        dicIDF[terme] = idf
    return dicIDF


#retourner le vecteur de la requete(tf-idf), avec les termes à inclure et les termes optionnels
def vec_termesRequete(listeDesTermes, doc_idf):
    tf = 1 / len(listeDesTermes)
    tfidf_liste = []
    for terme in listeDesTermes:
        if terme in doc_idf:
            tf_idf = tf * doc_idf[terme]
            tfidf_liste.append(tf_idf)
    return tfidf_liste


#retourner une liste qui comprend tous les termes dans le ducoment index inverse
def getTousTermes(document_indexInverse): 
    tousLesTermes = []
    for terme in document_indexInverse:
        tousLesTermes.append(terme)
    return tousLesTermes


#trier les documents selon la similarité consinu
def trierDocuments(resultatFinal, termesEffectifs, matriceTFIDF, listeTousTermes):
    resultat_avec_score = {}
    
    for id_doc, occus in resultatFinal.items():
        vec_doc = []
        for mot in termesEffectifs:
            if mot in occus:
                vec_doc.append(matriceTFIDF[id_doc][listeTousTermes.index(mot)])
            else:
                vec_doc.append(0)
            
        score = sum(vec_doc)
        resultat_avec_score[id_doc] = score
        
    resultat_sorted = sorted(resultat_avec_score.items(), key=lambda x: x[1], reverse=True)
    return resultat_sorted



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
termes_totals_string = " ".join(termes_totals)
ecritTexteDansUnFichier (termes_totals_string, fiTxt) 

#lematiser et normaliser tous les termes de requête
tokens = lemmatiseTermes(termes_totals)
termes_totals_a_chercher = normaliseTokensRequete (tokens)
log += "\ntermes: %s \n" % (termes_totals_a_chercher)

#lamatiser et normaliser les termes iclures et les termes exculres
if len(termes_inclure) != 0:
    termes_inclure_final = standardiseLesTermes(termes_inclure)
else:
    termes_inclure_final = termes_inclure

if len(termes_exclure) != 0:
    termes_exclure_final = standardiseLesTermes(termes_exclure)
else:
    termes_exclure_final = termes_exclure

if len(termes_optionnel) != 0:
    termes_optionnel_final = standardiseLesTermes(termes_optionnel)
else:
    termes_optionnel_final = termes_optionnel

#faire la reqête, chercher tous les documents qui comprennent tous les termes saisis, on obtient un résultat brut
nbMatch = requeteDesTermes(termes_totals_a_chercher, indexInverse)
log += "\nrésultat: %s \n" % (str(nbMatch))

#filtrer le résultat brut en fonction des symboles "+" et "-"
nbMatch_final = filtrerLeResultat(nbMatch, termes_inclure_final, termes_exclure_final)
log += "\nrésultats filtrés: %s\n" % str(nbMatch_final)

#affichage du résultat dans le terminal
print("\n{nombre} documents ont été trouvés!\n".format(nombre=len(nbMatch_final)))

#--------------------------trier les documents--------------------------------
termes_effectifs = termes_inclure_final + termes_optionnel_final

#obtenir le vecteur de la requête
liste_idf = getIDF(indexInverse, indexDocuments)
vec_req = vec_termesRequete(termes_effectifs, liste_idf)
#la liste de tous les termes sert à retirer la postition des termes
liste_termes_totals = getTousTermes(indexInverse)
#créer les matrice_freqs
matrice_freqs = creerMatrice(indexDocuments,indexInverse)
matrice_tfidf = TFIDF(matrice_freqs)

resultat_final_sorted = trierDocuments(nbMatch_final, termes_effectifs, matrice_tfidf, liste_termes_totals)



#extraire les sous-titres s'ils existent et les stocker dans "log"
log += "\nrésultats rangés et détaillés: \n\n"
for doc in resultat_final_sorted:
    nb_doc, score = doc
    info_document = indexDocuments[str(nb_doc)]
    nom_fichier = info_document[0]
    titre_complet = info_document[1]
    titre_principal = ""

    if "\n\n" in titre_complet:
        titre_principal = titre_complet[:titre_complet.index("\n\n")]
        sous_titre = titre_complet[titre_complet.index("\n\n")+2:]
        log += f"score: {score}\n id: {nb_doc}\n nom de fichier: {nom_fichier}\n titre de texte: {titre_principal}\n sous-titre: {sous_titre}\n\n" + "-"*40+"\n"
    else:
        log += f"score: {score}\n id: {nb_doc}\n nom de fichier: {nom_fichier}\n titre de texte: {titre_complet}\n\n" + "-"*40+"\n"

    print(f"rang: {resultat_final_sorted.index(doc)+1}\nid: {nb_doc}\n score: {score}\ntitre: {titre_principal}\n" + "-"*40)

# sauvegarde du log
ecritTexteDansUnFichier (log, fiLog)