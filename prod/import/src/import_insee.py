"""
Import des données INSEE
"""

import logging

from azure_upload import get_blob_list, upload_from_url

# Configuration du logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Dossier dans Azure Blob
DESTINATION_FOLDER = "insee"

# Liste des fichiers à télécharger
urls_with_filenames = {
    "https://www.insee.fr/fr/statistiques/fichier/4277761/T20F103.xlsx": "financement.xlsx"
}


def check_files_exist():
    """
    Vérifie si tous les fichiers existent déjà dans le container.
    Retourne True si tous les fichiers existent, False sinon.
    """
    existing_blobs = get_blob_list(DESTINATION_FOLDER)
    logger.info("Vérification de l'existence des fichiers dans %s/", DESTINATION_FOLDER)

    all_exist = True
    for _, file_name in urls_with_filenames.items():
        blob_path = f"{DESTINATION_FOLDER}/{file_name}"
        exists = blob_path in existing_blobs
        logger.info("Fichier %s: %s", file_name, 'Existe' if exists else 'N existe pas')
        all_exist = all_exist and exists

    return all_exist


def main():
    """
    Fonction principale pour l'import des données INSEE
    """
    if check_files_exist():
        logger.info("Tous les fichiers existent déjà. Arrêt de l'import.")
        with open("skip_import", "w", encoding="utf-8") as f:
            f.write("true")
        return

    logger.info("Début de l'import des données")
    success_count = 0
    error_count = 0

    for url, file_name in urls_with_filenames.items():
        try:
            logger.info("Traitement de %s", file_name)
            upload_from_url(url, DESTINATION_FOLDER, file_name)
            success_count += 1
        except Exception as e:
            logger.error("Erreur lors du traitement de %s: %s", file_name, str(e))
            error_count += 1

    logger.info("Import terminé. Succès: %d, Erreurs: %d", success_count, error_count)

    if error_count > 0:
        raise Exception(f"L'import s'est terminé avec {error_count} erreurs")


if __name__ == "__main__":
    main()
