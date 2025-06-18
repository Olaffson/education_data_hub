import os
import pandas as pd
import io
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient

# Configuration Azure à partir des secrets GitHub
AZURE_CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
AZURE_CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")
AZURE_TENANT_ID = os.getenv("AZURE_TENANT_ID")
AZURE_STORAGE_ACCOUNT = os.getenv("AZURE_STORAGE_ACCOUNT")

# Authentification
credential = DefaultAzureCredential(additionally_allowed_tenants=["*"])


# Clients Azure Storage
blob_service_client = BlobServiceClient(
    f"https://{AZURE_STORAGE_ACCOUNT}.blob.core.windows.net",
    credential=credential
)

CONTAINER_RAW = "raw"
CONTAINER_CLEANED = "cleaned"
SUBFOLDER = "data_gouv"

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Nettoie les données : en-têtes + suppression des lignes vides"""
    df.columns = [
        col.strip()
           .lower()
           .replace(" ", "_")
           .replace("'", "_")
           .replace("’", "_")
           .replace('"', "")
        for col in df.columns
    ]
    return df.dropna(how='all')

def move_and_clean_files():
    raw_container = blob_service_client.get_container_client(CONTAINER_RAW)
    cleaned_container = blob_service_client.get_container_client(CONTAINER_CLEANED)

    blobs_list = raw_container.list_blobs(name_starts_with=f"{SUBFOLDER}/")

    for blob in blobs_list:
        if not blob.name.endswith(".csv"):
            continue  # Ignorer les fichiers non-CSV

        print(f"Traitement du fichier : {blob.name}")

        # Lecture du fichier depuis le conteneur 'raw'
        blob_client = raw_container.get_blob_client(blob.name)
        raw_bytes = blob_client.download_blob().readall()

        try:
            df = pd.read_csv(io.BytesIO(raw_bytes), encoding="utf-8", sep=None, engine="python")
        except Exception as e:
            print(f"Erreur de lecture de {blob.name} : {e}")
            continue

        # Nettoyage du DataFrame
        df_cleaned = clean_dataframe(df)

        # Export dans le conteneur 'cleaned' en conservant le chemin
        cleaned_blob_client = cleaned_container.get_blob_client(blob.name)
        output_stream = io.BytesIO()
        df_cleaned.to_csv(output_stream, index=False, encoding="utf-8")
        output_stream.seek(0)

        cleaned_blob_client.upload_blob(output_stream, overwrite=True)
        print(f"Fichier nettoyé et déplacé dans {CONTAINER_CLEANED}/{blob.name}")

        # Optionnel : suppression du fichier source
        # blob_client.delete_blob()

if __name__ == "__main__":
    move_and_clean_files()
