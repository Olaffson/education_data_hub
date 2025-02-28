import pandas as pd
import io
import logging
from azure.storage.blob import BlobServiceClient

logger = logging.getLogger(__name__)

# Configuration Azure
AZURE_CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=xxx;AccountKey=xxx;EndpointSuffix=core.windows.net"
CONTAINER_RAW = "raw"
CONTAINER_CLEANED = "cleaned"

blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)

def clean_csv_data(csv_data: bytes) -> bytes:
    """
    Nettoie un fichier CSV (suppression des lignes vides, doublons, normalisation des colonnes).
    """
    try:
        df = pd.read_csv(io.BytesIO(csv_data))
        df.dropna(inplace=True)
        df.drop_duplicates(inplace=True)
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

        output = io.BytesIO()
        df.to_csv(output, index=False)
        return output.getvalue()
    except Exception as e:
        logger.error("Erreur lors du nettoyage du CSV: %s", e)
        raise

def clean_json_data(json_data: bytes) -> bytes:
    """
    Nettoie un fichier JSON (suppression des clés vides, formatage correct).
    """
    try:
        df = pd.read_json(io.BytesIO(json_data))
        df.dropna(inplace=True)
        df.drop_duplicates(inplace=True)

        output = io.BytesIO()
        df.to_json(output, orient="records", indent=4)
        return output.getvalue()
    except Exception as e:
        logger.error("Erreur lors du nettoyage du JSON: %s", e)
        raise

def clean_excel_data(excel_data: bytes) -> bytes:
    """
    Nettoie un fichier Excel (suppression des lignes vides, doublons).
    """
    try:
        df = pd.read_excel(io.BytesIO(excel_data))
        df.dropna(inplace=True)
        df.drop_duplicates(inplace=True)

        output = io.BytesIO()
        df.to_excel(output, index=False, engine='xlsxwriter')
        return output.getvalue()
    except Exception as e:
        logger.error("Erreur lors du nettoyage de l'Excel: %s", e)
        raise

def process_files():
    """
    Récupère les fichiers du conteneur `raw`, applique un nettoyage et les déplace vers `cleaned`.
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
            
            # Upload du fichier nettoyé en conservant la structure
            cleaned_blob_client = cleaned_container.get_blob_client(blob.name)
            cleaned_blob_client.upload_blob(cleaned_data, overwrite=True)

            logger.info(f"Fichier {blob.name} nettoyé et déplacé avec succès vers {CONTAINER_CLEANED}/")
        except Exception as e:
            logger.error(f"Erreur lors du traitement de {blob.name}: {e}")

if __name__ == "__main__":
    process_files()