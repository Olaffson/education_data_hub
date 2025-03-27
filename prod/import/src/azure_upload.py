"""
Module principal pour l'interaction avec Azure Blob Storage
"""

import json
import logging
import os

import requests
from azure.core.exceptions import AzureError
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

# Configuration du logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Configuration Azure Storage
STORAGE_ACCOUNT_NAME = "sadatalakeokotwicaprod"
CONTAINER_NAME = "raw"

# Utilisation des credentials du Service Principal
try:
    credential = DefaultAzureCredential()
    blob_service_client = BlobServiceClient(
        f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net/", credential=credential
    )
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)
except AzureError as error:
    logger.error("Erreur d'initialisation Azure: %s", str(error))
    raise


def upload_file_to_azure(content_bytes, container_name, blob_name):
    """
    Upload binaire (ex: CSV) vers Azure Blob
    """
    try:
        blob_service_client = get_blob_service_client()
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

        blob_client.upload_blob(content_bytes, overwrite=True)
        logger.info(f"✅ Upload réussi vers {container_name}/{blob_name}")
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'upload: {str(e)}")
        raise


def upload_json_to_azure(json_data, destination_folder, file_name):
    """
    Upload un JSON directement sur Azure Blob Storage depuis un objet Python.
    """
    try:
        logger.info("Préparation du JSON pour upload vers %s/%s", destination_folder, file_name)
        json_content = json.dumps(json_data, ensure_ascii=False, indent=4).encode("utf-8")

        blob_name = f"{destination_folder}/{file_name}"
        blob_client = container_client.get_blob_client(blob_name)

        logger.info("Upload vers %s", blob_name)
        blob_client.upload_blob(json_content, overwrite=True)
        logger.info("✅ JSON uploadé avec succès: %s", blob_name)

    except AzureError as error:
        logger.error("❌ Erreur Azure lors de l'upload: %s", str(error))
        raise
    except Exception as error:
        logger.error("❌ Erreur inattendue lors de l'upload: %s", str(error))
        raise


def upload_from_url(file_url, destination_folder, file_name):
    """
    Télécharge un fichier depuis une URL, le convertit en UTF-8 si CSV, puis l'upload dans Azure Blob Storage.
    """
    try:
        logger.info(f"📥 Téléchargement depuis {file_url}")
        response = requests.get(file_url)
        response.raise_for_status()

        # Chemin complet du blob
        blob_path = f"{destination_folder}/{file_name}"
        tmp_path = os.path.join("tmp_data", file_name)

        # Création du dossier temporaire si nécessaire
        os.makedirs(os.path.dirname(tmp_path), exist_ok=True)

        # Traitement des fichiers CSV : conversion en UTF-8
        if file_name.lower().endswith(".csv"):
            with open(tmp_path, "w", encoding="utf-8", newline="") as f_out:
                text = response.content.decode("utf-8-sig")
                f_out.write(text)
            logger.info(f"✅ Conversion en UTF-8 standard effectuée pour {tmp_path}")
        else:
            with open(tmp_path, "wb") as f_out:
                f_out.write(response.content)

        # Upload vers Azure
        blob_client = container_client.get_blob_client(blob_path)
        with open(tmp_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)

        logger.info(f"✅ Fichier uploadé avec succès: {blob_path}")

    except Exception as e:
        logger.error(f"❌ Erreur sur {file_name}: {str(e)}")
        raise


def check_blob_exists(destination_folder, file_name):
    """
    Vérifie si un blob existe déjà dans le container.
    """
    try:
        blob_name = f"{destination_folder}/{file_name}"
        blob_client = container_client.get_blob_client(blob_name)
        return blob_client.exists()
    except AzureError as e:
        logger.error(f"Erreur lors de la vérification du blob {blob_name}: {str(e)}")
        raise


def get_blob_list(prefix):
    """
    Retourne la liste des blobs dans un dossier spécifique.
    """
    try:
        return [blob.name for blob in container_client.list_blobs(name_starts_with=prefix)]
    except AzureError as e:
        logger.error(f"Erreur lors de la récupération de la liste des blobs: {str(e)}")
        raise
