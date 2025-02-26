import logging
import json
import os
from azure_upload import upload_from_url, get_blob_list, check_blob_exists

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Dossier dans Azure Blob
DESTINATION_FOLDER = "data_gouv"

# Liste des fichiers à télécharger
urls_with_filenames = {
    'https://www.data.gouv.fr/fr/datasets/r/27d469ff-9908-4b7e-a2e0-9439bb38a395': 'ips_lycee.csv',
    'https://www.data.gouv.fr/fr/datasets/r/5e662e9b-f033-44fa-9e9a-a5b40fec2cd3': 'bac_par_academie.csv',
    'https://www.data.gouv.fr/fr/datasets/r/8a0b8d35-fea2-4c8d-9af1-fb25edb16980': 'ecoles_effectifs.csv',
    'https://www.data.gouv.fr/fr/datasets/r/df2cbcb3-da0a-4265-a24e-c36f2c787db2': 'ips_lycee_new.csv',
    'https://www.data.gouv.fr/fr/datasets/r/7a2ad28a-0e2a-4c69-84f0-c703448b60f9': 'effectifs_tg.csv'
}

def check_files_exist():
    """
    Vérifie si tous les fichiers existent déjà dans le container.
    Retourne True si tous les fichiers existent, False sinon.
    """
    existing_blobs = get_blob_list(DESTINATION_FOLDER)
    logger.info(f"Vérification de l'existence des fichiers dans {DESTINATION_FOLDER}/")
    
    all_exist = True
    for _, file_name in urls_with_filenames.items():
        blob_path = f"{DESTINATION_FOLDER}/{file_name}"
        exists = blob_path in existing_blobs
        logger.info(f"Fichier {file_name}: {'Existe' if exists else 'N\'existe pas'}")
        all_exist = all_exist and exists
    
    return all_exist

def main():
    # Vérifier si tous les fichiers existent déjà
    if check_files_exist():
        logger.info("Tous les fichiers existent déjà. Arrêt de l'import.")
        # Créer un fichier pour indiquer qu'aucune action n'était nécessaire
        with open('skip_import', 'w') as f:
            f.write('true')
        return

    logger.info("Début de l'import des données")
    success_count = 0
    error_count = 0

    for url, file_name in urls_with_filenames.items():
        try:
            logger.info(f"Traitement de {file_name}")
            upload_from_url(url, DESTINATION_FOLDER, file_name)
            success_count += 1
        except Exception as e:
            logger.error(f"Erreur lors du traitement de {file_name}: {str(e)}")
            error_count += 1

    logger.info(f"Import terminé. Succès: {success_count}, Erreurs: {error_count}")
    
    if error_count > 0:
        raise Exception(f"L'import s'est terminé avec {error_count} erreurs")

if __name__ == "__main__":
    main()
