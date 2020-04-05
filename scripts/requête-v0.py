#!/usr/bin/env python
# coding: utf-8

# -------------------------------------------------------------------------------------------------------------
#   python3 requete-v0.py
#
#   Traitement d'une requête :
#       0. lecture fichier des index (inversé & documents)
#       1. lecture de la requête
#       2. extraction de ses tokens 
#       - lemmatisation
#       - normalisation 
#       3. recherche des documents correspondants dans l'index
#           par intersection d'ensemble (set)
#       4. affichage des résultats
# 
#   remarque : pb si aucun terme trouvé !
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

# 2. extraction de ses tokens (lemmatisation, normalisation)
ecritTexteDansUnFichier (requête, fiTxt)   
tokens = lemmatiseTexte (fiTxt, 'FR', PARSEUR)
motclefs = normaliseTokens (tokens, PARSEUR)
print (motclefs)

# 3. recherche des termes dans l'index
docs = set (indexDocuments.keys())
for motclef in motclefs:
    # pour chaque terme de la requête
    if motclef in indexInversé :
        docs = docs & set (indexInversé[motclef])
print (docs)

# 4. affichage des résultats
print ("%s documents trouvés:" % len (docs))
for doc in docs :
    print ("\t%s" % indexDocuments[doc])