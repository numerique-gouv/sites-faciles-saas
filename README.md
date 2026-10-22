# Gestionnaire de déploiements pour Sites Conformes

Cet outil permet de déployer simplement une instance de [Sites Conformes](https://github.com/numerique-gouv/sites-conformes) sur [https://dashboard.scalingo.com/](Scalingo).

## Architecture

Le projet implémente des librairies d’interfaçage avec les APIs de Scalingo et Alwaysdata, respectivement situées dans `instances/service/scalingo.py` et `instances/service/alwaysdata.py`, normalisées de manière à toujours renvoyer un dictionnaire similaire.

L’essentiel de la progression du déploiement se fait via un formulaire `instances/forms.py` > `InstanceActionForm` avec un champ caché `action` qui appelle la prochaine étape du déploiement, dont la logique est gérée dans le modèle `instances/models.py` > `Instance`.

## Pages statiques

Le projet abrite dans `core/static/pages` des pages statiques pouvant être configurées comme pages d’erreur ou de maintenance
depuis une instance Scalingo (cf. [Documentation de Scalingo](https://doc.scalingo.com/platform/app/custom-error-page).)

Scalingo récupère ces pages et les met en cache : elles sont donc autonomes (CSS, images et favicon intégrés), et
l’application doit être redémarrée pour prendre en compte une modification de la variable correspondante.

Elles sont servies à l’adresse `https://<HOST_URL>/static/pages/<page>.html` :

| Page | Usage | Variable Scalingo |
| --- | --- | --- |
| `maintenance.html` | Instance arrêtée temporairement | `SCALINGO_STOPPED_PAGE_URL`, définie automatiquement par le gestionnaire lors de l’arrêt de l’instance |
| `disabled.html` | Instance désactivée définitivement | `SCALINGO_STOPPED_PAGE_URL`, définie automatiquement par le gestionnaire lors de l’arrêt de l’instance |
| `403.html` | Requête refusée par le pare-feu IP de l’application | `SCALINGO_FORBIDDEN_PAGE_URL` |
| `503.html` | Service indisponible : aucun conteneur `web` actif, erreur 502 ou délai dépassé (504) | `SCALINGO_NO_FRONT_ERROR_URL`, `SCALINGO_APP_ERROR_URL`, `SCALINGO_TIMEOUT_ERROR_URL` |

Les variables des pages 403 et 503 ne sont pas gérées par le gestionnaire : elles sont à définir manuellement sur chaque
application Scalingo concernée, par exemple :

```sh
scalingo --app <application> env-set \
  SCALINGO_FORBIDDEN_PAGE_URL=https://<HOST_URL>/static/pages/403.html \
  SCALINGO_NO_FRONT_ERROR_URL=https://<HOST_URL>/static/pages/503.html \
  SCALINGO_APP_ERROR_URL=https://<HOST_URL>/static/pages/503.html \
  SCALINGO_TIMEOUT_ERROR_URL=https://<HOST_URL>/static/pages/503.html
scalingo --app <application> restart
```

Pour prévisualiser les pages en local : `just stopped_pages_server`, qui sert le dossier et un index listant les pages.

## Documentation

* Une documentation détaillée de l’installation en local est disponible sur [ONBOARDING.md](./ONBOARDING.md).
* Une documentation expliquant comment contribuer est disponible sur [CONTRIBUTING.md](./CONTRIBUTING.md).
* Un guide d’utilisation est disponible dans la [documentation de Sites Conformes](https://sites.beta.gouv.fr/documentation/gestionnaire-de-sites/)
