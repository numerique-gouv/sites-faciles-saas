# Beta x Django

## Introduction

Ce repo est un kit de démarrage pour vos projets en Django. Il intègre :

- le [Design System de l’État](https://www.systeme-de-design.gouv.fr/) (DSFR) avec [django-dsfr](https://pypi.org/project/django-dsfr/)
- des Content Security Policies avec django-csp
- les paramètres pour se connecter à une base de données PostgreSQL
- Pre-commit, pour formater votre code à chaque commit
- une ébauche de CI pour vos tests automatiques
- une ébauche de Makefile pour gérer les commandes fréquentes
- Pipenv pour la gestion des dépendances
- les modules django-extensions et django-debug-toolbar pour faciliter le développement

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

### Installer l’environnement et les dépendances

```
pipenv install
```

Pour une installation de dev en local, installer aussi les dépendances devs
```
pipenv install --dev
```

### Configurer la base de données

Installer PostgreSQL en fonction de votre OS : https://www.postgresql.org/download/
puis créer une base de données et configurer les paramètres correspondants dans DATABASE_URI de votre fichier .env.

### Remplir la base de données et collecter les fichiers statiques
```bash
make update
```

Cette commande peut être passée à chaque mise à jour.

### Installation de pre-commit

[Pre-commit](https://pre-commit.com/) permet de linter et formater votre code avant chaque commit. Il exécute les commandes définies dans le fichier `.pre-commit-config.yaml`

Pour l’installer :

```bash
pre-commit install
```

Vous pouvez effectuer un premier passage sur tous les fichiers du repo avec :

```bash
make checkstyle
```

### Internationalisation
Le dépôt est prêt pour l’[internationalisation](https://docs.djangoproject.com/en/5.0/topics/i18n/translation/).
Taper `make messages` pour générer les chaînes à traduire, et effectuer la traduction avec un outil tel que [Poedit](https://poedit.net/).

### Exécuter les tests manuellement

```bash
make test
```

### Accéder au shell Django avancé
```bash
pipenv run python manage.py shell_plus
```
