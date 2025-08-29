# Ynov Basket – Application Web NBA (Flask)

## Description
Application Flask qui affiche joueurs, équipes et matchs de la NBA via l’API balldontlie.

## Fonctionnalités
- Authentification (login / inscription)
- Liste et recherche de joueurs
- Pages de détail pour équipes et matchs
- Pagination (Suivant / Précédent)

## Lancement du projet

Étapes pour lancer le projet (dépendances, commandes).
```bash
cd ynov_basket
py -m venv .venv
#Installation des dépendances
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate      # Windows
pip install -r requirements.txt
python app.py
```



## Utilisation 

 Vous retrouverez la web app dans votre navigateur à cette addresse:
        
        -http://127.0.0.1:5000

Vous pourrez créer un compte en respectant la nomenclature email et un mot de passe. Ensuite, vous pourrez accéder à la page de connexion, puis les renseigner et enfin pouvoir voir les données de l'API.

## Améliorations possibles

- Ajout de barres de recherche
- Ajout d'une autre api(pour faire de vrai cartes avec photos ou compléter plus d'infos sur les joueurs)


