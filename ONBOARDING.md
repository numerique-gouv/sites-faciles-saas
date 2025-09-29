## Installation en local

### Edit .env

Copier les variables d’environnement :
```
cp .env.example .env
```
puis modifier en le contenu pour correspondre à votre configuration.

- `HOST_URL` : le nom de domaine de l’URL principale de votre site, par exemple « mon-site.osc-fr1.scalingo.io »
- `ALLOWED_HOSTS` : le ou les domaines autorisés à accéder au site, séparés par des virgules s’il y en a plusieurs. On peut déjà entrer le domaine définitif si on le connaît, même s’il n’existe pas encore. Par exemple : « mon-site.osc-fr1.scalingo.io,mon-site.beta.gouv.fr »
- `SECRET_KEY` : clé secrète, par exemple générée dans un terminal avec la commande « `openssl rand -hex 32` »
- `DATABASE_URL` : pré-remplie sur Scalingo
- `DEBUG` : `True` en développement, `False` en production
- `HOST_PORT` : le port sur lequel tourne le site (8000 par défaut)
- `SCALINGO_API_TOKEN` : à générer via https://dashboard.scalingo.com/account/tokens
- `ALWAYSDATA_ROOT_DOMAIN` : le domaine dans lequel vont être créés les sous-domaines chez Alwaysdata
- `EMAIL_SECRETS`:
  - Créer un fichier `.secrets_email.txt` avec le format suivant : """
   1;email;password
   2;email;password
   """
  - Lancer la commande `just encode_secrets email` et copier-coller le résultat

- `STORAGE_SECRETS`:
  - Créer un fichier `.secrets_storage.txt` avec le format suivant : """
   1;key_id;key_secret;commentaire (par ex: bucket_name@host)
   2;key_id;key_secret;commentaire (par ex: bucket_name@host)
   """
  - Lancer la commande `just encode_secrets storage` et copier-coller le résultat

Note : pour pouvoir créer des instances SecNumCloud, l’authentification à deux facteurs doit être activée sur le compte Scalingo utilisé.

- Optionnels:
  - `SCALINGO_APPLICATION_PREFIX` : permet de remplacer le préfixe par défaut ajouté au nom des applications Scalingo (par défaut, "sf")
  - `SCALINGO_PROJECT`: permet de définir l’identifiant d’un projet Scalingo dans lequel créer l’application (si vide, utilise le projet par défaut de l’utilisateur)
  - `USE_UV` : mettre à `true` en mode développement pour préfixer les recettes `just` avec `env run`.

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

## Utilisation

```bash
just runserver
```
