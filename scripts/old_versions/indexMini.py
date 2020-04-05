#!/usr/bin/env python
# coding: utf-8

# -------------------------------------------------------------------------------------------------------------
#   python3 indexMini.py
#
#   Indexation des xml du dossier 'miniCorpus/FR/' :
#   Parcours des fichiers xml; pour chacun :
#       1. extraction du contenu textuel et sauvegarde
#
#   remarques :
#       - un fichier 'txt' temporaire est utilisé pour chaque xml
#       - un fichier 'log' est créé pour tracer les traitements
# -------------------------------------------------------------------------------------------------------------

import os
import sys
import re

tree-tagger = "/home/mlopezmalet/tree-tagger/cmd/tree-tagger-french"
# dfinition de fonctions 'bibliothèque' (plus pratique)

# lecture d'un fichier 'texte'
def litTexteDuFichier (fichier) :

    with open (fichier , "r") as FI :
        texte = "\n".join (FI.readlines())
    return texte


# écriture du texte dans un fichier
def ecritTexteDansUnFichier(texte, fichier) :

    with open (fichier, "w") as FI :
        FI.write (texte)

def lemmatiser(fichier_in, fichier_out, parseur):
    tokens = []
    os.system("sh %s %s %s" % (parseur, fichier_in, fichier_out))
    #lire le csv réduire aux colonnes lemmes et POS: matcher avec regex (groupe colonne 2 et groupe colonne 3
    #ouvrir le csv avec for i in csv.splitlines()






# ------------------------ MAIN --------------------------------

log = ""
fiLog = "./indexMini.log"
fiTxt= "./tempo.txt"
doCorpus = "./miniCorpus/FR/"



for fi in sorted(os.listdir (doCorpus)) :
    if fi.endswith (".xml") :
        # pour chaque xml
        print (fi)

        # extraction du texte du fichier XML
        fiXml = doCorpus + fi
        texte = litTexteDuFichier (fiXml)

        # suppression des balises xml  etr des lignes vierges
        texte = re.sub (r'<[^>]+>', '', texte)
        texte = re.sub (r'\n+', '\n', texte)

        # mise à jour formatée de la variable 'log'
        log += "\n\n%s\n\t%s" % (fiXml, texte)     # plus pratique que : "\n\n" + fiXml + "\n\t" + texte

        # sauvegarde du texte brut
        ecritTexteDansUnFichier (texte, fiTxt)

        # lemmatisation(fichier, langue, parseur)

        #filtrer mots vides
        #désaccentuer
        #minusculiser

# sauvegarde du log
ecritTexteDansUnFichier (log, "fiLog")
