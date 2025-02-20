# Gestionnaire de déploiements pour Sites Faciles

Cet outil permet de déployer simplement une instance de [Sites faciles](https://github.com/numerique-gouv/sites-faciles) sur [https://dashboard.scalingo.com/](Scalingo).

## Architecture
Le projet implémente des librairies d’interfaçage avec les APIs de Scalingo et Alwaysdata, respectivement situées dans `instances/service/scalingo.py` et `instances/service/alwaysdata.py`, normalisées de manière à toujours renvoyer un dictionnaire similaire.

L’essentiel de la progression du déploiement se fait via un formulaire `instances/forms.py` > `InstanceActionForm` avec un champ caché `action` qui appelle la prochaine étape du déploiement, dont la logique est gérée dans le modèle `instances/models.py` > `Instance`.

## Documentation
* Une documentation détaillée de l’installation en local est disponible sur [ONBOARDING.md](./ONBOARDING.md).
* Une documentation expliquant comment contribuer est disponible sur [CONTRIBUTING.md](./CONTRIBUTING.md).
* Un guide d’utilisation est disponible dans la [documentation de Sites Faciles](https://sites.beta.gouv.fr/documentation/gestionnaire-de-sites/)
