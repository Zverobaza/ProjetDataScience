# ProjetDataScience

├── backend/
│   ├── __init__.py -> Laissez tomber
│   ├── models.py -> Definitions des modeles
│   ├── predictions.py -> Predire les outputs
│   ├── routes.py -> Ce fichier definit les routes de l'API FastAPI. relie backend et frontend
│   └── services.py -> Fichier pour traiter les donnees 
├── data/
│   ├── conso_mix_RTE_2023.xlsx
│   ├── conso_mix_RTE_2024.xlsx
│   └── conso_mix_RTE_2025.xlsx
├── frontend/
│   └── app.py -> Interface utilisateur
├── main.py -> Lancer le serveur FastAPI et configurer les routes
├── README.md -> Fournir des instructions pour utiliser le projet
└── requirements.txt -> les dependances necessaires (ce que j'ai sur mon pc) 


Pour executer le script: 
Dans un fenetre de terminal taper la commande suivante
uvicorn main:app --reload

You should have:
INFO:     Will watch for changes in these directories: ['/Users/macos/Desktop/PDS']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [55709] using StatReload
INFO:     Started server process [55711]
INFO:     Waiting for application startup.
INFO:     Application startup complete.

Dans un autre fenetre:
python3 frontend/app.py

Yous should have:
Dash is running on http://127.0.0.1:8050/

 * Serving Flask app 'app'
 * Debug mode: on

Copy  http://127.0.0.1:8050/ and paste it to browser. Done. The amazing interface is on.