# Mosifra

Petit projet Django pour démarrer Mosifra.

## Démarrage
1. `python -m venv .venv`
2. `.\.venv\Scripts\activate` (Windows) ou `source .venv/bin/activate`
3. `pip install -r requirements.txt`
4. `docker compose down` pour être sur
5. `docker compose up -d db` 
6. `python manage.py migrate`
7. `python manage.py runserver`
8. créer le fichier .env avec les mdp... dedans
9. `npm run tailwind:watch` pour tailwind

- http://127.0.0.1:8001/ pour l'accueil
- http://127.0.0.1:8001/accounts/register/ pour créer un compte
- http://127.0.0.1:8001/accounts/login/ pour te connecter
- http://127.0.0.1:8001/admin
- http://127.0.0.1:8001/accounts/invitations/upload pour upload le csv

## Structure
- `src/config/` : settings et urls
- `src/accounts/` : modèle utilisateur, vues login/register
- `src/templates/` : layout HTML
- `tests/` : test