import logging
from azure.storage.blob import BlobServiceClient
import io
from src.data_cleaning import clean_csv_data, clean_json_data, clean_excel_data

# Configuration Azure
AZURE_CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=xxx;AccountKey=xxx;EndpointSuffix=core.windows.net"
CONTAINER_RAW = "raw"
CONTAINER_CLEANED = "cleaned"

logger = logging.getLogger(__name__)

blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)

def move_cleaned_files():
    """
    Récupère les fichiers du conteneur `raw`, applique un nettoyage et les déplace vers `cleaned`,
    tout en conservant la structure des dossiers.
    """
    raw_container = blob_service_client.get_container_client(CONTAINER_RAW)
    cleaned_container = blob_service_client.get_container_client(CONTAINER_CLEANED)

    blobs = raw_container.list_blobs()

    for blob in blobs:
        try:
            logger.info(f"Traitement du fichier: {blob.name}")
            
            blob_client = raw_container.get_blob_client(blob.name)
            blob_data = blob_client.download_blob().readall()
            
            # Déterminer le type de fichier
            if blob.name.endswith(".csv"):
                cleaned_data = clean_csv_data(blob_data)
            elif blob.name.endswith(".json"):
                cleaned_data = clean_json_data(blob_data)
            elif blob.name.endswith(".xlsx"):
                cleaned_data = clean_excel_data(blob_data)
            else:
                logger.warning(f"Type de fichier non supporté : {blob.name}")
                continue
            
            # Déterminer le dossier (ex: data_gouv/, insee/, opendatasoft/)
            subfolder = "/".join(blob.name.split("/")[:-1])  # Récupère le chemin du dossier
            
            # Upload du fichier nettoyé en conservant la structure
            cleaned_blob_client = cleaned_container.get_blob_client(blob.name)
            cleaned_blob_client.upload_blob(cleaned_data, overwrite=True)

            # Suppression du fichier original
            blob_client.delete_blob()
            logger.info(f"Fichier {blob.name} nettoyé et déplacé avec succès vers {subfolder}/")
        except Exception as e:
            logger.error(f"Erreur lors du traitement de {blob.name}: {e}")

if __name__ == "__main__":
    move_cleaned_files()
