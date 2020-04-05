#!/usr/bin/env python
# coding: utf-8

# -------------------------------------------------------------------------------------------------------------
#   python3 indexMini-TP.py
#
#   Indexation des xml d'un dossier (miniCorpus/FR/) :
#   Parcours des fichiers xml; pour chacun :
#       1. extraction du contenu textuel et sauvegarde
#       2. lemmatisation : TreeTagger
#       3. normalisation des tokens
#       4. mise à jour de l'index inverse
#       5. utilisation d'un dictionnaire des documents (id/chemin)
#   sauvegarde fichier des index (inverse & documents)
#
#   remarques :
#       - un fichier 'txt' temporaire est utilise pour chaque xml
#       - un fichier 'log' est cree pour tracer les traitements
#
#   attention :
# 	1. dans cette version, l'indexation n'est pas 'incrementale', c'est-à dire
# 	l'ajout à l'index de fichiers individuels ou d'un dossier ne fonctionne pas !
# 	2. les dossiers _log et _index doivent dejà exister !
# -------------------------------------------------------------------------------------------------------------


import os
import sys
import re
import pickle
from langdetect import detect


# -------- à parametrer ---------------
# corpus à indexer
doCorpus = "../corpus/initiaux/"
nomCorpus = "Corpus"
# -------------------------------------

# index resultats
fiIndex = "./_index/indexInverse"
fiDocs = "./_index/indexDocuments"

# dossier log & fichiers de travail (temporaires)
doLog = "./_log/"

# fichier du texte à indexer
fiTxt = "tempo.txt"

# fichier log de trace de l'execution
fiLog = "./_log/indexMini.log"
log = ""


# ----------------- gestion de fichiers ----------------------------

# LECTURE D'UN FICHIER TEXTE
def litTexteDuFichier(fichier):
    with open(fichier, "r") as FI:
        texte = "\n".join(FI.readlines())
    return texte


# ECRITURE DU TEXTE DANS UN FICHIER
def ecritTexteDansUnFichier(texte, fichier):
    with open(fichier, "w") as FI:
        FI.write(texte)


# LECTURE D'UN OBJET QUELCONQUE DEPUIS UN FICHIER BINAIRE
def litObjetDepuisFichier(fichier):
    with open(fichier, "rb") as FI:
        objet = pickle.load(FI)
    return objet


# ECRITURE D'UN OBJET DANS UN FICHIER BINAIRE
def ecritObjetDansFichier(objet, fichier):
    with open(fichier, "wb") as FI:
        pickle.dump(objet, FI)


# ----------------- traitements TAL----------------------------------

# EXTRACTION DU TEXTE BRUT D'UN DOCUMENT XML
#  -> renvoie une string
#  remarque : pour une indexation 'multilingue', il faudrait :
# 	- detecter la langue (langdetect.py)
#    	- la retourner aussi
def extraitTexteDuDocument(fichier):
    texte = litTexteDuFichier(fichier)
    # suppression des balises xml  et des lignes vierges
    texte = re.sub(r"<[^>]+>", "", texte)
    texte = re.sub(r"\n+", "\n", texte)
    print(detect(texte).upper())
    # mise à jour formatee de la variable globale 'log'
    global log  # obligatoire
    log += "\n\n%s\n\t%s" % (fichier, texte)
    return texte


# FONCTION PAS UTILISÉE (tree tagger en python à la place
def lemmatiseTexte(fichier):
    tokensLemmePos = []
    fiParse = fichier + ".par"
    # execute TreeTagger
    cmd = "tree-tagger-french"
    os.system("%s %s > %s" % (cmd, fichier, fiParse))
    # lit le csv produit par treeTagger
    with open(fiParse, "r") as FI:
        for ligne in FI:
            ligne = ligne.strip()
            defToken = ligne.split("\t")
            # filtre les tokens vides
            if len(defToken) >= 3:
                # reduit aux lemmes et pos
                token = [defToken[2], defToken[1]]
                tokensLemmePos.append(token)
    # renvoie une liste de tokens (lemme et pos)
    return tokensLemmePos


# SUPPRESSION DES MOTS-VIDES D'APRES LE SEUL POS
#   -> renvoie une liste de lemmes
def filtreMotsVides(tokens, lang):
    lemmeTokensPleins = []
    # pos acceptes : noms communs et propres, adjectifs, verbes, numeraux et abreviations
    if lang == "FR":
        catPleines = ["NOM", "NAM", "ADJ", "VER", "NUM", "ABR"]
    else:
        catPleines = [
            "NN",
            "NNS",
            "NP",
            "NPS",
            "JJ",
            "JJR",
            "JJS",
            "VB",
            "VBD",
            "VBG",
            "VBN",
            "VBZ",
            "VBP",
            "VD",
            "VDD",
            "VDG",
            "VDN",
            "VDZ",
            "VDP",
            "VH",
            "VHD",
            "VHG",
            "VHN",
            "VHZ",
            "VHP",
            "VV",
            "VVD",
            "VVG",
            "VVN",
            "VVP",
            "VVZ ",
            "CD",
            "FW",
        ]
    for defToken in tokens:
        lemme = defToken[0]
        catGram = defToken[1]
        if catGram in catPleines:
            lemmeTokensPleins.append(lemme)
    return lemmeTokensPleins


# DESACCENTUATIONS DES LEMMES (du français)
#   -> renvoie une liste de lemmes desaccentues
def desaccentueLesTokens(lemmes):
    lemmesSansAccent = []
    table = str.maketrans("àâeéèêîïôùûüÿ", "aaeeeeiiouuuy")
    for lemme in lemmes:
        lemmesSansAccent.append(lemme.translate(table))
    return lemmesSansAccent


# MINUSCULISATION (des noms propres ou debut de phrases)
def minusculiseLesTokens(lemmes):
    lemmesEnMinuscule = []
    for lemme in lemmes:
        lemmesEnMinuscule.append(lemme.lower())
    return lemmesEnMinuscule


# NORMALISATION DES TOKENS
def normaliseTokens(tokens, lang):
    tokens = filtreMotsVides(tokens, lang)
    tokens = desaccentueLesTokens(tokens)
    tokens = minusculiseLesTokens(tokens)
    return tokens

"""
# ------------------ MAIN ---------------------------------------
indexDocuments = dict()
indexInverse = dict()

# lecture des index
if os.path.isfile(fiDocs):
    indexDocuments = litObjetDepuisFichier(fiDocs)

if os.path.isfile(fiIndex):
    indexInverse = litObjetDepuisFichier(fiIndex)

# affichage de l'etat de l'index initial
nbDocsIndexes = len(indexDocuments.keys())
nbTermesIndexes = len(indexInverse.keys())
print(
    "dejà indexes : %s documents, %s termes\n"
    % (str(nbDocsIndexes), str(nbTermesIndexes))
)


# identifiant de document
idDoc = 0

for fi in sorted(os.listdir(doCorpus)):
    # parcours du corpus specifie

    if fi.endswith(".txt"):
        # pour chaque xml
        print(fi)

        # extraction du texte du fichier XML
        fiDoc = doCorpus + fi
        texte = extraitTexteDuDocument(fiDoc)

        # sauvegarde du texte brut
        ecritTexteDansUnFichier(texte, fiTxt)

        # lemmatisation du texte
        tokens = lemmatiseTexte(fiTxt)

        # normalisation des tokens : les termes de l'index...
        termes = normaliseTokens(tokens)
        log += "\n" + str(termes)
        print("\t%s termes" % len(termes))

        # id du document courant
        idDoc += 1
        indexDocuments[idDoc] = fiDoc

        # mise à jour de l'index inverse...
        for terme in termes:
            # recuperation de la liste des documents du terme
            docsTerme = []
            if terme in indexInverse.keys():
                docsTerme = indexInverse[terme]

            if idDoc not in docsTerme:
                # les documents ne sont ajoutes qu'une fois
                docsTerme.append(idDoc)
                indexInverse[terme] = docsTerme

# affichage de l'etat de l'index resultant
nbDocsIndexes = len(indexDocuments.keys())
nbTermesIndexes = len(indexInverse.keys())
print(
    "dejà indexes : %s documents, %s termes\n"
    % (str(nbDocsIndexes), str(nbTermesIndexes))
)

log += "\n\n" + str(indexInverse)

# ----- sauvegarde de l'index des documents et de l'index inverse des termes
ecritObjetDansFichier(indexDocuments, fiDocs)
ecritObjetDansFichier(indexInverse, fiIndex)

# sauvegarde du log
ecritTexteDansUnFichier(log, fiLog)
"""
