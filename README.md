# Gestionnaire de déploiements pour Sites Faciles

Cet outil permet de déployer simplement une instance de [Sites faciles](https://github.com/numerique-gouv/sites-faciles) sur [https://dashboard.scalingo.com/](Scalingo).

## Use

```bash
make runserver
```

## Installation

### Edit .env

Copier les variables d’environnement :
```
cp .env.example .env
```
puis modifier en le contenu pour correspondre à votre configuration.

- `HOST_URL` : le nom de domaine de l’URL principale de votre site, par exemple « mon-site.osc-fr1.scalingo.io »
- `ALLOWED_HOSTS` : le ou les domaines autorisés à accéder au site, séparés par des virgules s’il y en a plusieurs. On peut déjà entrer le domaine définitif si on le connaît, donc : « mon-site.osc-fr1.scalingo.io,mon-site.beta.gouv.fr »
- `SECRET_KEY` : clé secrète, par exemple générée dans un terminal avec la commande « `openssl rand -hex 32` »
- `DATABASE_URL` : pré-remplie sur Scalingo
- `DEBUG` : True en développement, False en production
- `HOST_PORT` : le port sur lequel tourne le site (8000 par défaut)
- `SCALINGO_API_TOKEN` : à générer via https://dashboard.scalingo.com/account/tokens
- `EMAIL_SECRETS`:
  - Créer un fichier `emailconfig.txt` avec le format suivant : """
   1;email;password
   2;email;password
   """
  - Lancer la commande `uv run python manage.py encode_email_secrets` et copier-coller le résultat

Note : pour pouvoir créer des instances SecNumCloud, l’authentification à deux facteurs doit être activée sur le compte Scalingo utilisé.

### Installer l’environnement et les dépendances

```bash
uv sync --no-dev
```

Pour une installation de dev en local, installer aussi les dépendances devs

```bash
uv sync
```

### Configurer la base de données

Installer PostgreSQL en fonction de votre OS : https://www.postgresql.org/download/
puis créer une base de données et configurer les paramètres correspondants dans DATABASE_URL de votre fichier .env.

### Remplir la base de données et collecter les fichiers statiques
```bash
just update
```

Cette commande peut être passée à chaque mise à jour.

### Créer le superuser
```bash
just createsuperuser
```

### Installation de pre-commit

[Pre-commit](https://pre-commit.com/) permet de linter et formater votre code avant chaque commit. Il exécute les commandes définies dans le fichier `.pre-commit-config.yaml`

Pour l’installer :

```bash
pre-commit install
```

Vous pouvez effectuer un premier passage sur tous les fichiers du repo avec :

```bash
just quality
```

### Internationalisation
Le dépôt est prêt pour l’[internationalisation](https://docs.djangoproject.com/en/5.0/topics/i18n/translation/).
Taper `just makemessages` pour générer les chaînes à traduire, et effectuer la traduction avec un outil tel que [Poedit](https://poedit.net/).

### Exécuter les tests manuellement

```bash
just test
```

### Accéder au shell Django avancé
```bash
just shell
```

## Documentation tierce
- [API Alwaysdata](https://help.alwaysdata.com/en/api/)
- [API Scalingo](https://developers.scalingo.com/)
