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
python -m venv .venv
#Installation des dépendances
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate      # Windows
pip install -r requirements.txt
python app.py
```



## Utilisation 

 Vous retrouverez la web app dans votre navigateur à cette addresse:
        
        -http://127.0.0.1:5000



## Structure du projet

Ynov_Basket/
│
├── app.py                # Application Flask principale
├── requirements.txt      # Dépendances Python
├── .venv/                # Environnement virtuel
│
├── templates/            # Fichiers HTML (Jinja2)
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── players.html
│   ├── player_detail.html
│   ├── teams.html
│   ├── team_detail.html
│   ├── games.html
│   └── game_detail.html
│
├── static/               # Ressources statiques
│   └──style.css


## Améliorations possibles

- Ajout de barres de recherche
- Ajout d'une autre api(pour faire de vrai cartes avec photos)


