#!/usr/bin/env python
# coding: utf-8

# -------------------------------------------------------------------------------------------------------------
#
#   --> fonctions utiles à l'indexation, utilisées dans indexeur.py et requête.py
#
# -------------------------------------------------------------------------------------------------------------

import re
import json
from langdetect import detect
import treetaggerwrapper


# index resultats
fiIndex = "./_index/indexInverse"
fiDocs = "./_index/indexDocuments"


# ----------------- gestion de fichiers ----------------------------

# LECTURE D'UN FICHIER TEXTE
def litTexteDuFichier(fichier):
    """renvoie une string contenant le texte d'un fichier"""
    with open(fichier, "r") as FI:
        texte = "\n".join(FI.readlines())
    return texte


# ECRITURE DU TEXTE DANS UN FICHIER
def ecritTexteDansUnFichier(texte, fichier):
    """ecrit le texte donné en paramètre dans un fichier"""
    with open(fichier, "w") as FI:
        FI.write(texte)


# LECTURE D'UN FICHIER JSON
def litJSONDepuisFichier(fichier):
    """renvoie le contenu d'un fichier json"""
    with open(fichier, "rb") as FI:
        objet = json.load(FI)
    return objet


# ECRITURE D'UN FICHIER JSON
def ecritJSONDansFichier(objet, fichier):
    """écrit dans un fichier en format json"""
    with open(fichier, "w+", encoding="utf8") as FI:
        json.dump(objet, FI, ensure_ascii=False, indent=4, separators=(',', ': '))


# ----------------- traitements TAL----------------------------------

# EXTRACTION DU TEXTE BRUT D'UN DOCUMENT XML
def extraitTexteDuDocument(fichier):
    """renvoie une string avec le texte d'un document, sans ses balises"""
    texte = litTexteDuFichier(fichier)
    # suppression des balises xml  et des lignes vierges
    texte = re.sub(r"<[^>]+>", "", texte)
    texte = re.sub(r"\n+", "\n", texte)
    print(detect(texte).upper())
    # mise à jour formatee de la variable globale 'log'
    global log  # obligatoire
    log += "\n\n%s\n\t%s" % (fichier, texte)
    return texte


# SUPPRESSION DES MOTS-VIDES D'APRES LE POS-tag
def filtreMotsVides(tokens, lang):
    """renvoie une liste de lemmes en fonction de leur catégorisation par tree-tagger (s'adapte au texte anglais et français)"""
    lemmeTokensPleins = []
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
def desaccentueLesTokens(lemmes):
    """retire l'accentuation des lemmes"""
    lemmesSansAccent = []
    table = str.maketrans("àâeéèêîïôùûüÿ", "aaeeeeiiouuuy")
    for lemme in lemmes:
        lemmesSansAccent.append(lemme.translate(table))
    return lemmesSansAccent


# MINUSCULISATION (des noms propres ou debut de phrases)
def minusculiseLesTokens(lemmes):
    """renvoie une liste de lemmes en minuscule"""
    lemmesEnMinuscule = []
    for lemme in lemmes:
        lemmesEnMinuscule.append(lemme.lower())
    return lemmesEnMinuscule


# NORMALISATION DES TOKENS
def normaliseTokens(tokens, lang):
    """normalise les tokens en retirant les mots vides, les accents et les majuscules"""
    tokens = filtreMotsVides(tokens, lang)
    tokens = desaccentueLesTokens(tokens)
    tokens = minusculiseLesTokens(tokens)
    return tokens


def normaliseTokensRequete(tokens):
    """retire les accents et les majuscules des termes de la requête"""
    tokens = desaccentueLesTokens(tokens)
    tokens = minusculiseLesTokens(tokens)
    return tokens


# FILTRAGE FIN
def filtrage_fin(tokens):
    """ filtre plus finement les tokens"""
    tokens_out = []
    for token in tokens:
        if len(token) == 1 or token == "":
            tokens.remove(token)
            tokens_out.append(token)
        elif (
            (token[:2] == "l’")
            or (token[:2] == "d’")
            or (token[:2] == "s’")
            or (token[:2] == "n’")
        ):
            fixed_token = token[2:]
            tokens.append(fixed_token)
            tokens.remove(token)
            tokens_out.append(token)
        elif token[:3] == "qu’":
            fixed_token = token[3:]
            tokens.append(fixed_token)
            tokens.remove(token)
            tokens_out.append(token)
        elif len(token) == 2 and "’" in token:
            tokens.remove(token)
            tokens_out.append(token)
    return tokens


# LEMMATISAION
def lemmatiseTermes(liste):
    """utilise tree-tagger en français ou en anglais selon le besoin pour renvoyer une liste de lemmes avec leurs POS"""
    tokensLemme = []
    # execute TreeTagger
    texte = " ".join(liste)
    if detect(texte) == "fr":
        tagger = treetaggerwrapper.TreeTagger(TAGLANG="fr")
        tags = tagger.tag_text(texte)
    else:
        tagger = treetaggerwrapper.TreeTagger(TAGLANG="en")
        tags = tagger.tag_text(texte)
    for ligne in tags:
        ligne = ligne.strip()
        defToken = ligne.split("\t")
        # filtre les tokens vides
        if len(defToken) >= 3:
            tokensLemme.append(defToken[2])
    # renvoie une liste de tokens (lemme et pos)
    return tokensLemme
