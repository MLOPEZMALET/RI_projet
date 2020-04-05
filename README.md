PROJET RI

- Objet du projet final:
1. L’indexation ‘incrémentale’ d’un corpus bilingue français / anglais
2. L’interrogation booléenne de ce corpus par mots-clefs

→ Documents à renvoyer:
- code python
- documentation ‘readme’
- index calculés
- exemples de résultat de requête : mots-clés et liste documents trouves

1. Indexation

- index des documents: OK  
→ fonction indexeur_documents()  
→ A chaque id (dictionnaire) seront associés :le nom du fichier du document indexé + le titre de l’article  

- lemmes normalisés des documents en deux langues: OK  
→ fonction indexeur_termes(): extrait et prétraite les termes puis renvoie un set de termes uniques + un dictionnaire qui organise les termes par document   

- index inversé (pour chaque terme, il comporte, outre le numéro (ou id) du document, sa fréquence dans celui-ci): OK  
→ la fonction indexeur_termes() crée le vocabulaire qui sera le keyset du dictionnaire.  
→ la fonction indexeur_inverse() crée l'index inversé à partir de ce que renvoie l'indexeur de documents et l'indexeur de termes  

- stockage en json (json.dump, json.load): KO  
→ il faut stocker en json l'index des documents et l'index inversé, ça permettra de le rendre incrémental  

- Chaque document indexé sera dupliqué dans un unique dossier documentsIndexes: KO  
→ mais on a la fonction ecritTexteDansUnFichier(), il faudra juste l'ajouter  

- bilingue: OK  
→ avec langdetect, on reconnaît la langue, on passe le tree-tagger adéquat (fonction lemmatiseurTexte()), puis on filtre en fonction des balises de la langue reconnue (fonction filtreMotsVides() dans  normaliseTexte()  

- incrémental (l’indexation devra pouvoir être mise à jour sans doublons si on lui présente un nouveau dossier à indexer. Pour cela, avant d’indexer, il faudra lire l’éventuel fichier index depuis le disque): KO  
→ pour le moment, comme aucun stockage, ne permet pas d'ajouter des termes.  

- exécution ligne de commande (_python3 indexerDocuments <chemin de dossier>_): KO  
→ pas encore d'appel à des arguments proposés par l'utilisateur  



2. Requêtes

- à faire

3. Finitions

- création de logs: KO  
- try/except
- rédaction du README
- commenter, organiser, nettoyer code
- présenter un exemple d'utilisation
