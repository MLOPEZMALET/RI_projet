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
from FS_fichiers import litTexteDuFichier, ecritTexteDansUnFichier
from FS_tal import lemmatiseTexte, normaliseTokens

PARSEUR = 'TALISMANE'
   
fiIndex = "./_index/indexInverse"
fiDocs = "./_index/indexDocuments"
doCorpus = "../corpus/miniCorpus/FR/"

fiTxt = "./_log/tempo.txt" 

fiLog = "./_log/requete.log"
log = ""


indexDocuments = dict()
indexInversé = dict ()

# 0. lecture des index
if os.path.isfile (fiDocs) :
    with open(fiDocs, 'rb') as FI :
        indexDocuments = pickle.load(FI)
    print (indexDocuments)

if os.path.isfile (fiIndex) :
    with open(fiIndex, 'rb') as FI :
        indexInversé = pickle.load(FI)
    print (indexInversé)
 
# 1. lecture de la requête (mots clés)
print("votre requête ?")
requête = input()
print("...", requête)
log += "\nrequête %s" % (requête)

# 2. extraction de ses tokens (lemmatisation, normalisation)
ecritTexteDansUnFichier (requête, fiTxt)   
tokens = lemmatiseTexte (fiTxt, 'FR', PARSEUR)
termes = normaliseTokens (tokens, PARSEUR)
log += "\n\ttermes %s" % (termes)

# 3. recherche des termes dans l'index
nbMatch = dict ()
for doc in indexDocuments.keys() : 
    nbMatch[doc] = 0

for terme in termes:
    # pour chaque terme de la requête
    if terme in indexInversé :
        for doc in indexInversé[terme] : nbMatch[doc] += 1
log += "\t%s" % (str (nbMatch))

# 4. affichage des résultats
for doc, nb in sorted(nbMatch.items(), key=lambda item: item[1], reverse=True) :
    if nb != 0 :
        print ("\t%s (%s)" % (indexDocuments[doc], str (nb)))
        
        
# sauvegarde du log
ecritTexteDansUnFichier (log, fiLog)