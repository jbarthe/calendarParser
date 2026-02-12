# Guide de Déploiement et Partage

Voici les différentes méthodes pour rendre l'application accessible à vos collègues.

## Option 1 : Partage en Ligne (Recommandé)
Le moyen le plus simple est d'héberger l'application sur **Streamlit Community Cloud** (gratuit).

1.  Créez un compte sur [share.streamlit.io](https://share.streamlit.io/).
2.  Mettez votre code sur GitHub (je peux vous aider à initialiser le dépôt si besoin).
3.  Connectez Streamlit Cloud à votre dépôt GitHub.
4.  L'application sera accessible via une URL unique (ex: `https://mon-planning-conges.streamlit.app`) que vous pourrez envoyer à tout le monde.

## Option 2 : Partage sur le Réseau Local (Bureau)
Si vous êtes sur le même réseau Wifi/Ethernet que vos collègues :

1.  Lancez l'application sur votre mac via le terminal :
    ```bash
    streamlit run app.py
    ```
    Ou double-cliquez sur le fichier `launch_app.command` que j'ai créé.

2.  Regardez dans le terminal, il affichera deux adresses :
    -   `Local URL: http://localhost:8501` (pour vous)
    -   `Network URL: http://192.168.1.XX:8501` (pour vos collègues)

3.  Envoyez l'adresse **Network URL** à vos collègues. Tant que votre ordinateur est allumé et l'app lancée, ils pourront y accéder.

## Option 3 : Installation sur chaque poste
Si vous voulez que chacun puisse lancer l'app indépendamment :
1.  Installez Python sur leur machine.
2.  Copiez le dossier du projet.
3.  Installez les dépendances : `pip install -r requirements.txt`.
4.  Lancez avec `streamlit run app.py`.
