#PROJET RI

## M2 TAL parcours IM - Chen SUN, Mélanie LOPEZ MALET

### Objet du projet: 
1. L’indexation ‘incrémentale’ d’un corpus bilingue français / anglais en format XML
2. L’interrogation booléenne de ce corpus par mots-clefs

### Fonctionnement

##### 1. Indexer le corpus:
- exécuter en ligne de commande: '''python3 indexeur.py chemin/du/corpus/a/indexer'''
 	- index des documents:
		→ un index des documents du corpus sera crée dans le dossier _index/IndexDocs
		→ l'index des documents est constitué d'un id, du nom du fichier et  du titre du document
	- index inversé:
		→ création d'un index inversé à partir d'un vocabulaire bilingue normalisé
		→ l'index inversé se trouve dans _index/IndexInverse
		→ le programme associe à chaque terme du vocabulaire la liste des documents où il apparaît avec sa fréquence respective
	- corpus indexés:
		→ une copie de chaque document indexé est créée dans le dossier Corpus/documentsIndexes
 
##### 2. Enrichir le corpus:

- Si vous voulez ajouter des documents à votre index, pas de problème. Vous pouvez:
	→ ajouter les nouveaux documents dans le dossier Corpus/
	→ les stocker dans un nouveau dossier
- Dans les deux cas, vous n'avez qu'à relancer la commande '''python3 indexeur.py chemin/du/corpus/a/indexer''' pour que les nouveaux documents soient indexés, sans aucun doublon.

##### 3. Faire une requête:

- Pour interroger votre corpus, exécutez la commande '''python3 requete.py'''
- Ecrivez votre requête. Vous pouvez la préciser en utilisant la syntaxe suivante: en respectant les règles suivantes:
	-  +mot: le mot est obligatoirement présent dans le document
	- -mot: le mot est obligatoirement absent du document
	- mot: si le mot est recherché, mais sa présence n'est pas obligatoire
- Le programme vous renvoie une liste de résultats ordonnée par pertinence, à partir d'un calcul fondé sur le tf-idf (*overlap score measure*\*)   
\* Christopher Manning, Introduction to information retrieval, 2009, p.119


#### 4. Un exemple d'utilisation

- Vous trouverez dans le dossier Corpus/ un corpus de test composé d'articles du journal Le Monde Diplomatique, divisé en deux dossiers (initiaux et complémentaires)
- Le dossier _index/ contient l'index inversé et l'index des documents de ce corpus.
- Vous pouvez également consulter des exemples de requête et leurs résultats dans _log/requete.log

### En cas de problème:

Le dossier _log contient des fichiers qui se génèrent à chaque exécution du programme et permettent de s'assurer de son bon fonctionnement.
