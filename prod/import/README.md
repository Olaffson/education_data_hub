# Scripts d'Import de Données

Ce dossier contient les scripts d'importation de données depuis différentes sources vers Azure Blob Storage.

## Configuration requise

Les dépendances nécessaires sont listées dans `requirements.txt`. Pour les installer :

```bash
pip install -r requirements.txt
```

## Structure des fichiers

- `azure_upload.py` : Module principal pour l'interaction avec Azure Blob Storage
- `import_insee.py` : Import des données INSEE
- `import_data_gouv.py` : Import des données data.gouv.fr
- `import_data_opendatasoft.py` : Import des données OpenDataSoft

## Configuration Azure

Les scripts utilisent Azure DefaultAzureCredential pour l'authentification. Assurez-vous d'avoir configuré :
- Un compte de stockage Azure
- Les permissions nécessaires via un Service Principal
- Les variables d'environnement appropriées

## Sources de données

### INSEE
- Données de financement des établissements

### Data.gouv.fr
- IPS des lycées
- Résultats du baccalauréat par académie
- Effectifs des écoles
- Données des effectifs en terminale générale

### OpenDataSoft
- Données générales sur les lycées d'Île-de-France

## Utilisation

Chaque script peut être exécuté individuellement :

```bash
python import_insee.py
python import_data_gouv.py
python import_data_opendatasoft.py
```

## Fonctionnalités communes

- Vérification de l'existence des fichiers avant import
- Logging détaillé des opérations
- Gestion des erreurs
- Création d'un fichier 'skip_import' si les données existent déjà

## Structure de stockage Azure

Les données sont stockées dans les dossiers suivants :
- `insee/` : Données INSEE
- `data_gouv/` : Données data.gouv.fr
- `opendatasoft/` : Données OpenDataSoft

## Logs

Les logs incluent :
- Horodatage
- Niveau de log
- Messages détaillés sur les opérations
- Erreurs éventuelles