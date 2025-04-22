import pandas as pd
import logging
from azure.storage.blob import BlobServiceClient
from io import StringIO
from bdd_sql.sql_connection import get_sql_connection, close_sql_connection

# Configuration du logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Configuration Azure Storage
STORAGE_ACCOUNT_NAME = "sadatalakeokotwicaprod"
CONTAINER_NAME = "cleaned"

def import_ips_lycee_to_sql():
    """
    Importe les données IPS lycée depuis le conteneur cleaned vers SQL
    """
    conn = None
    try:
        # Connexion au Blob Storage
        connection_string = f"DefaultEndpointsProtocol=https;AccountName={STORAGE_ACCOUNT_NAME};EndpointSuffix=core.windows.net"
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client(CONTAINER_NAME)
        
        # Lecture du blob
        blob_client = container_client.get_blob_client("data_gouv/ips_lycee_new.csv")
        blob_data = blob_client.download_blob()
        content = blob_data.content_as_text()
        
        # Conversion en DataFrame
        df = pd.read_csv(StringIO(content), encoding='utf-8')
        
        # Nettoyage des noms de colonnes
        df.columns = [col.strip().lower().replace(' ', '_').replace('-', '_') for col in df.columns]
        
        # Obtention de la connexion SQL
        conn = get_sql_connection()
        
        # Import dans SQL
        df.to_sql(
            name='ips_lycee',
            con=conn,
            if_exists='replace',
            index=False,
            schema='dbo'
        )
        
        logger.info("✅ Données IPS lycée importées avec succès dans la base SQL")
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'import des données IPS lycée: {str(e)}")
        raise
        
    finally:
        if conn:
            close_sql_connection(conn)

def import_csv_to_sql(csv_file_path, table_name):
    """
    Importe un fichier CSV dans une table SQL
    
    Args:
        csv_file_path (str): Chemin vers le fichier CSV
        table_name (str): Nom de la table SQL
    """
    conn = None
    try:
        # Lecture du CSV avec pandas
        df = pd.read_csv(csv_file_path, encoding='utf-8')
        
        # Nettoyage des noms de colonnes
        df.columns = [col.strip().lower().replace(' ', '_').replace('-', '_') for col in df.columns]
        
        # Obtention de la connexion
        conn = get_sql_connection()
        
        # Import dans SQL
        df.to_sql(
            name=table_name,
            con=conn,
            if_exists='replace',
            index=False,
            schema='dbo'
        )
        
        logger.info(f"✅ Données importées avec succès dans la table {table_name}")
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'import des données dans {table_name}: {str(e)}")
        raise
        
    finally:
        if conn:
            close_sql_connection(conn)

def execute_sql_query(query):
    """
    Exécute une requête SQL
    
    Args:
        query (str): Requête SQL à exécuter
    """
    conn = None
    try:
        conn = get_sql_connection()
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        logger.info("✅ Requête SQL exécutée avec succès")
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'exécution de la requête SQL: {str(e)}")
        raise
        
    finally:
        if conn:
            close_sql_connection(conn)
