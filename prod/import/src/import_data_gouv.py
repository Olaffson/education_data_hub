"""
Import des données data.gouv.fr
"""

import logging
import os
import requests

from azure_upload import upload_json_to_azure, upload_from_url, check_blob_exists, get_blob_list

# Configuration du logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Dossier dans Azure Blob
DESTINATION_FOLDER = "data_gouv"

# Liste des fichiers à télécharger
urls_with_filenames = {
    "https://www.data.gouv.fr/fr/datasets/r/27d469ff-9908-4b7e-a2e0-9439bb38a395": "ips_lycee.csv",
    "https://www.data.gouv.fr/fr/datasets/r/5e662e9b-f033-44fa-9e9a-a5b40fec2cd3": "bac_par_academie.csv",
    "https://www.data.gouv.fr/fr/datasets/r/8a0b8d35-fea2-4c8d-9af1-fb25edb16980": "ecoles_effectifs.csv",
    "https://www.data.gouv.fr/fr/datasets/r/df2cbcb3-da0a-4265-a24e-c36f2c787db2": "ips_lycee_new.csv",
    "https://www.data.gouv.fr/fr/datasets/r/7a2ad28a-0e2a-4c69-84f0-c703448b60f9": "effectifs_tg.csv",
}

TEMP_DIR = "tmp_data"
os.makedirs(TEMP_DIR, exist_ok=True)

def convert_utf8_sig_to_utf8(input_path):
    """Convertit un fichier de UTF-8-SIG à UTF-8"""
    with open(input_path, "r", encoding="utf-8-sig") as f:
        content = f.read()

    with open(input_path, "w", encoding="utf-8") as f:
        f.write(content)

    logger.info(f"✅ Conversion en UTF-8 standard effectuée pour {input_path}")

def download_and_prepare_file(url, filename):
    """Télécharge et prépare un fichier pour l'upload"""
    local_path = os.path.join(TEMP_DIR, filename)

    # Télécharger le fichier
    response = requests.get(url)
    response.raise_for_status()

    with open(local_path, "wb") as f:
        f.write(response.content)

    logger.info(f"📥 Fichier téléchargé: {local_path}")

    # Conversion de UTF-8-SIG vers UTF-8
    convert_utf8_sig_to_utf8(local_path)

    return local_path

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
    Fonction principale pour l'import des données data.gouv.fr
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
            logger.info(f"📦 Traitement de {file_name}")
            local_path = download_and_prepare_file(url, file_name)
            
            # Upload du fichier converti
            with open(local_path, "rb") as f:
                upload_file_to_azure(f.read(), DESTINATION_FOLDER, file_name)
            
            success_count += 1
        except Exception as e:
            logger.error(f"❌ Erreur sur {file_name}: {str(e)}")
            error_count += 1

    logger.info(f"✅ Import terminé. Succès: {success_count}, Erreurs: {error_count}")

    if error_count > 0:
        raise Exception(f"L'import s'est terminé avec {error_count} erreurs")

if __name__ == "__main__":
    main()
