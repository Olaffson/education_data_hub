"""
Import des données OpenDataSoft
"""

import json
import logging
import requests
from azure_upload import get_blob_list, upload_json_to_azure

# Configuration du logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Dossier dans Azure Blob
DESTINATION_FOLDER = "opendatasoft"
OUTPUT_FILENAME = "lycees-donnees-generales-combine.json"

# Liste des URL de l'API
urls = [
    "https://data.opendatasoft.com/api/explore/v2.1/catalog/datasets/lycees-donnees-generales@datailedefrance/records?limit=100&offset=0",
    "https://data.opendatasoft.com/api/explore/v2.1/catalog/datasets/lycees-donnees-generales@datailedefrance/records?limit=100&offset=100",
    "https://data.opendatasoft.com/api/explore/v2.1/catalog/datasets/lycees-donnees-generales@datailedefrance/records?limit=100&offset=200",
    "https://data.opendatasoft.com/api/explore/v2.1/catalog/datasets/lycees-donnees-generales@datailedefrance/records?limit=100&offset=300",
    "https://data.opendatasoft.com/api/explore/v2.1/catalog/datasets/lycees-donnees-generales@datailedefrance/records?limit=100&offset=400",
    "https://data.opendatasoft.com/api/explore/v2.1/catalog/datasets/lycees-donnees-generales@datailedefrance/records?limit=100&offset=500",
    "https://data.opendatasoft.com/api/explore/v2.1/catalog/datasets/lycees-donnees-generales@datailedefrance/records?limit=100&offset=600",
    "https://data.opendatasoft.com/api/explore/v2.1/catalog/datasets/lycees-donnees-generales@datailedefrance/records?limit=100&offset=700",
    "https://data.opendatasoft.com/api/explore/v2.1/catalog/datasets/lycees-donnees-generales@datailedefrance/records?limit=100&offset=800",
]


def check_files_exist():
    """
    Vérifie si le fichier JSON existe déjà dans le container.
    """
    existing_blobs = get_blob_list(DESTINATION_FOLDER)
    blob_path = f"{DESTINATION_FOLDER}/{OUTPUT_FILENAME}"
    exists = blob_path in existing_blobs
    logger.info("Fichier %s: %s", OUTPUT_FILENAME, 'Existe' if exists else 'N existe pas')
    return exists


def fetch_json_data(api_url):
    """
    Télécharge les données JSON depuis l'API.
    """
    try:
        logger.info("Téléchargement depuis %s", api_url)
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("results", [])
    except requests.exceptions.RequestException as e:
        logger.error("Erreur lors de la requête API: %s", str(e))
        raise
    except json.JSONDecodeError as e:
        logger.error("Erreur lors du décodage JSON: %s", str(e))
        raise


def main():
    """
    Fonction principale pour l'import des données OpenDataSoft
    """
    if check_files_exist():
        logger.info("Le fichier existe déjà. Arrêt de l'import.")
        with open("skip_import", "w", encoding="utf-8") as f:
            f.write("true")
        return

    logger.info("Début de l'import des données OpenDataSoft")
    all_results = []
    error_count = 0

    for url in urls:
        try:
            results = fetch_json_data(url)
            all_results.extend(results)
            logger.info("✅ %d enregistrements récupérés depuis %s", len(results), url)
        except Exception as e:
            error_count += 1
            logger.error("Erreur pour l'URL %s: %s", url, str(e))

    if error_count > 0:
        raise Exception(f"L'import s'est terminé avec {error_count} erreurs")

    combined_data = {"total_count": len(all_results), "results": all_results}
    logger.info("Upload du fichier combiné avec %d enregistrements", len(all_results))
    upload_json_to_azure(combined_data, DESTINATION_FOLDER, OUTPUT_FILENAME)
    logger.info("Import terminé avec succès")


if __name__ == "__main__":
    main()
