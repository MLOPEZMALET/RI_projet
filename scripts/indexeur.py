#!/usr/bin/env python
# coding: utf-8

# -------------------------------------------------------------------------------------------------------------
#   python3 indexeur.py chemin/du/dossier/a/indexer
#
#   Indexation des xml d'un dossier:
#   Parcours des fichiers xml; pour chacun :
#       1. extraction du contenu textuel et sauvegarde
#       2. lemmatisation : TreeTagger
#       3. normalisation des tokens
#       4. mise à jour de l'index inverse
#       5. utilisation d'un dictionnaire des documents (id/chemin)
#   sauvegarde fichier des index (inverse & documents)
#
#   remarques :
#       - un fichier 'log' est cree pour tracer les traitements
# -------------------------------------------------------------------------------------------------------------


import os
import re
import glob
import sys
from fonctions_index import (
    litTexteDuFichier,
    ecritTexteDansUnFichier,
    normaliseTokens,
    ecritJSONDansFichier,
    filtrage_fin
)
import treetaggerwrapper
from collections import defaultdict
from langdetect import detect
import json

# TODO: gestion des erreurs
# TODO: log

# ___PATHS___

# corpus donnés
path_corpus_initiaux = os.path.join("..", "corpus", "initiaux")
path_corpus_complementaires = os.path.join("..", "corpus", "complémentaires")
# fichiers texte sans balise (cf lignes commentées de extraitTexteDuFichier())
path_sans_balise = os.path.join("..", "corpus", "sans_balises")
# scripts
path_scripts_relative = os.path.join("..", "..", "scripts")

# indexation
path_index = os.path.join(".", "_index")
chemin_index_inverse = "./_index/indexInverse"
chemin_index_docs = "./_index/indexDocuments"
path_docs_indexes = "/home/mlopezmalet/MLOPEZMALET/m2/RI/TP/RI_projet/corpus/documentsIndexes"

# log
doLog = "./_log/"

fiLog = "./_log/indexeur.log"
log = ""


# ___INDEXATION DOCUMENTS___

def indexeur_documents(chemin):
    """ renvoie un dictionnaire avec pour clé l'id d'un document, et en valeur une liste contenant son nom et son titre"""
    # vérifie si un index a déjà été créé et le lit
    if os.path.isfile(chemin_index_docs):
        initial = False
        with open(chemin_index_docs) as file:
            index_docs = json.load(file)
    # si aucun index n'est trouvé, en crée un nouveau
    else:
        initial = True
        index_docs = defaultdict()
    noms_fichiers = lister_noms_fichiers(chemin)
    chemins_fichiers = lister_chemins_fichiers(chemin)
    titres = []
    for fichier in chemins_fichiers:
        titre = extraitTitreDuFichier(fichier)
        titres.append(titre)
    # crée l'index de documents du corpus
    if initial:
        for i in range(len(noms_fichiers)):
            index_docs[i] = [noms_fichiers[i], titres[i]]
            ecritJSONDansFichier(index_docs, chemin_index_docs)
    # actualise l'index de documents en évitant les doublons
    else:
        for doc in index_docs.keys():
            titre = index_docs[doc][1]
            nom = index_docs[doc][0]
            if titre in titres and nom in noms_fichiers:
                titres.remove(titre)
                noms_fichiers.remove(nom)
                print("document doublon ignoré: " + nom)
            else:
                continue
        # indexe les nouveaux documents de façon incrémentale
        if len(titres) != 0 and len(noms_fichiers) != 0:
            new_index_docs = defaultdict()
            start_id = len(index_docs)
            stop_id = start_id + len(titres)
            list_id = [i for i in range(start_id, stop_id)]
            for id, nom, titre in zip(list_id, noms_fichiers, titres):
                new_index_docs[id] = [nom, titre]
            print("nouveaux documents indexés: " + str(len(new_index_docs)))
            index_docs.update(new_index_docs)
            ecritJSONDansFichier(index_docs, chemin_index_docs)
            print("total documents indexés: " + str(len(index_docs)))
        else:
            print("pas de nouveaux documents indexés")
    print("total documents dans l'index: " + str(len(index_docs)))
    return index_docs


# ___INDEXATION TERMES___


def indexeur_termes(chemin):
    """ à partir du chemin d'un dossier, renvoie un dictionnaire qui, pour chaque nom de fichier en clé, a pour valeur les lemmes des termes qu'il contient"""
    termes_par_doc = defaultdict()
    total_termes_indexes = []
    # choper erreur de placement: être au bon endroit pour lancer
    chemins = lister_chemins_fichiers(chemin)
    noms = lister_noms_fichiers(chemin)
    for chemin, nom in zip(chemins, noms):
        os.system(f"cp {chemin} ../corpus/documentsIndexes")
        print("extraction vocabulaire de " + str(nom))
        tokensLemmePos, lang = lemmatiseurTexteAvecLangue(chemin, nom)
        tokens_normalises = normaliseTokens(tokensLemmePos, lang)
        tokens = filtrage_fin(tokens_normalises)
        termes_par_doc[nom] = tokens
        for terme in tokens:
            total_termes_indexes.append(terme)
    # renvoie l'index en ordre alphabétique multilingue + le dictionnaire avec clé=doc / valeur=lemmes
    return sorted(set(total_termes_indexes)), termes_par_doc


# ___INDEX INVERSÉ___

def indexeur_inverse(total_termes_indexes, termes_par_doc, index_documents):
    """ paramètres:
        - total_termes_indexes: vocabulaire du corpus, résultat de indexeur_termes()
        - termes_par_doc: vocabulaire du corpus par document, résultat de indexeur_termes()
        - index_documents: index des documents des corpus avec leurs noms et titres, résultat de indexeur_documents()
        renvoie:
        - un dictionnaire avec en clé un terme et en valeur une liste de tuples tels que terme:[(id doc1, freq terme doc1), (id doc2, freq terme doc2)...]"""
    # vérifie si un index inversé existe déjà, si non, le crée
    if os.path.isfile(chemin_index_inverse):
        with open(chemin_index_inverse) as file:
            index_inverse = json.load(file)
    else:
        index_inverse = defaultdict()
    # ajoute les termes nouveaux au vocabulaire si besoin
    for terme in total_termes_indexes:
        if terme not in index_inverse.keys():
            index_inverse[terme] = []
        else:
            continue
        # récupère l'id des documents o sont présents les documents,
        for id_doc in index_documents.keys():
            titre = index_documents[id_doc][0]
            for doc in termes_par_doc.keys():
                if (titre == doc) and (terme in termes_par_doc[doc]):
                    voc_doc = termes_par_doc[doc]
                    id_et_freq = (id_doc, voc_doc.count(terme))
                    index_inverse[terme].append(id_et_freq)
    ecritJSONDansFichier(index_inverse, chemin_index_inverse)
    return index_inverse


# ___UTILS___


def lister_chemins_fichiers(chemin):
    """renvoie une liste contenant les chemins de tous les fichiers du dossier"""
    liste_chemins_fichier = glob.glob(chemin + "/*.txt")
    return liste_chemins_fichier


def lister_noms_fichiers(chemin):
    """ renvoie une liste contenant les noms de tous les fichier du dossier"""
    os.chdir(chemin)
    liste_noms_fichiers = glob.glob("*.txt")
    os.chdir(path_scripts_relative)
    return liste_noms_fichiers


def extraitTitreDuFichier(fichier):
    """à partir d'un chemin, renvoie le contenu de la balise <titre>"""
    contenu = litTexteDuFichier(fichier)
    match_titre = re.search("<titre>[\s\S]*<\/titre>", contenu)
    titre_balise = match_titre.group(0)
    titre = re.sub(r"<[^>]+>", "", titre_balise)
    return titre


def extraitTexteDuFichier(fichier, nom_fichier):
    """à partir d'un chemin, renvoie le contenu de la balise <texte> + peut écrire un fichier avec ce texte (lignes commentées)"""
    contenu = litTexteDuFichier(fichier)
    match_texte = re.search("<texte>[\s\S]*<\/texte>", contenu)
    texte_balise = match_texte.group(0)
    texte = re.sub(r"<[^>]+>", "", texte_balise)
    #à décommenter pour créer des fichiers avec le texte sans balises
    #fichier_clean = "../corpus/sans_balises/" + nom_fichier + ".txt"
    #ecritTexteDansUnFichier(texte, fichier_clean)
    return texte


def lemmatiseurTexteAvecLangue(fichier, nom_fichier):
    """ appelle tree-tagger en fonction de la langue du texte, puis renvoie une liste de tokens+lemme+POS ainsi que la langue du document"""
    tokensLemmePos = []
    # execute TreeTagger
    texte = extraitTexteDuFichier(fichier, nom_fichier)
    if detect(texte) == "fr":
        tagger = treetaggerwrapper.TreeTagger(TAGLANG="fr")
        tags = tagger.tag_text(texte)
        lang = "FR"
    else:
        tagger = treetaggerwrapper.TreeTagger(TAGLANG="en")
        tags = tagger.tag_text(texte)
        lang = "EN"
    for ligne in tags:
        ligne = ligne.strip()
        defToken = ligne.split("\t")
        # filtre les tokens vides
        if len(defToken) >= 3:
            # reduit aux lemmes et pos
            token = [defToken[2], defToken[1]]
            tokensLemmePos.append(token)
    # renvoie une liste de tokens (lemme et pos)
    return tokensLemmePos, lang


# ___PIPELINE___


def indexation_corpus(chemin_corpus):
    global log
    etapes = ["1. Indexation des documents", "2. Indexation des termes", "3. Création de l'index inversé", "Indexation finalisée"]
    print(etapes[0])
    index_docs = indexeur_documents(chemin_corpus)
    log += etapes[0]
    log += str(index_docs)
    print(etapes[1])
    vocabulaire, termes_par_doc = indexeur_termes(chemin_corpus)
    log += etapes[1]
    log += str(termes_par_doc)
    print(etapes[2])
    index_inverse = indexeur_inverse(vocabulaire, termes_par_doc, index_docs)
    log += etapes[2]
    log += str(index_inverse)
    print(etapes[3])


# ___MAIN___

if __name__ == "__main__":
    log = "chemin du corpus\n"
    chemin = sys.argv[1]
    print(f"Indexation du corpus situé à {chemin}")
    log += chemin
    log += "\n"
    indexation_corpus(chemin)
    # sauvegarde du log
    ecritTexteDansUnFichier(log, fiLog)
