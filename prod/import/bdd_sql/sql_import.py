# import pandas as pd
# import logging
# from azure.storage.blob import BlobServiceClient
# from io import StringIO
# from bdd_sql.sql_connection import get_sql_connection, close_sql_connection

# # Configuration du logging
# logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
# logger = logging.getLogger(__name__)

# # Configuration Azure Storage
# STORAGE_ACCOUNT_NAME = "sadatalakeokotwicaprod"
# CONTAINER_NAME = "cleaned"

# def import_ips_lycee_to_sql():
#     """
#     Importe les données IPS lycée depuis le conteneur cleaned vers SQL
#     """
#     conn = None
#     try:
#         # Connexion au Blob Storage
#         connection_string = f"DefaultEndpointsProtocol=https;AccountName={STORAGE_ACCOUNT_NAME};EndpointSuffix=core.windows.net"
#         blob_service_client = BlobServiceClient.from_connection_string(connection_string)
#         container_client = blob_service_client.get_container_client(CONTAINER_NAME)
        
#         # Lecture du blob
#         blob_client = container_client.get_blob_client("data_gouv/ips_lycee_new.csv")
#         blob_data = blob_client.download_blob()
#         content = blob_data.content_as_text()
        
#         # Conversion en DataFrame
#         df = pd.read_csv(StringIO(content), encoding='utf-8')
        
#         # Nettoyage des noms de colonnes
#         df.columns = [col.strip().lower().replace(' ', '_').replace('-', '_') for col in df.columns]
        
#         # Obtention de la connexion SQL
#         conn = get_sql_connection()
        
#         # Import dans SQL
#         df.to_sql(
#             name='ips_lycee',
#             con=conn,
#             if_exists='replace',
#             index=False,
#             schema='dbo'
#         )
        
#         logger.info("✅ Données IPS lycée importées avec succès dans la base SQL")
        
#     except Exception as e:
#         logger.error(f"❌ Erreur lors de l'import des données IPS lycée: {str(e)}")
#         raise
        
#     finally:
#         if conn:
#             close_sql_connection(conn)

# def import_csv_to_sql(csv_file_path, table_name):
#     """
#     Importe un fichier CSV dans une table SQL
    
#     Args:
#         csv_file_path (str): Chemin vers le fichier CSV
#         table_name (str): Nom de la table SQL
#     """
#     conn = None
#     try:
#         # Lecture du CSV avec pandas
#         df = pd.read_csv(csv_file_path, encoding='utf-8')
        
#         # Nettoyage des noms de colonnes
#         df.columns = [col.strip().lower().replace(' ', '_').replace('-', '_') for col in df.columns]
        
#         # Obtention de la connexion
#         conn = get_sql_connection()
        
#         # Import dans SQL
#         df.to_sql(
#             name=table_name,
#             con=conn,
#             if_exists='replace',
#             index=False,
#             schema='dbo'
#         )
        
#         logger.info(f"✅ Données importées avec succès dans la table {table_name}")
        
#     except Exception as e:
#         logger.error(f"❌ Erreur lors de l'import des données dans {table_name}: {str(e)}")
#         raise
        
#     finally:
#         if conn:
#             close_sql_connection(conn)

# def execute_sql_query(query):
#     """
#     Exécute une requête SQL
    
#     Args:
#         query (str): Requête SQL à exécuter
#     """
#     conn = None
#     try:
#         conn = get_sql_connection()
#         cursor = conn.cursor()
#         cursor.execute(query)
#         conn.commit()
#         logger.info("✅ Requête SQL exécutée avec succès")
        
#     except Exception as e:
#         logger.error(f"❌ Erreur lors de l'exécution de la requête SQL: {str(e)}")
#         raise
        
#     finally:
#         if conn:
#             close_sql_connection(conn)


import os
import io
import unidecode
import logging
import pandas as pd
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from bdd_sql.sql_connection import get_sql_connection, close_sql_connection

# Configuration du logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Informations sur le blob
BLOB_ACCOUNT_URL = "https://sadatalakeokotwicaprod.blob.core.windows.net"
CONTAINER_NAME = "cleaned"
BLOB_NAME = "ips_lycee_new.csv"

def import_ips_lycee_to_sql():
    logger.info("📥 Début import des données IPS lycée")

    try:
        # Authentification Azure
        credential = DefaultAzureCredential()
        blob_service_client = BlobServiceClient(account_url=BLOB_ACCOUNT_URL, credential=credential)
        blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=BLOB_NAME)
        blob_data = blob_client.download_blob()
        logger.info("✅ Blob téléchargé avec succès depuis Azure Storage")

        # Lecture du CSV
        csv_string = blob_data.readall().decode("utf-8-sig")
        df = pd.read_csv(io.StringIO(csv_string), sep=";")

        logger.info(f"🧾 Colonnes détectées : {list(df.columns)}")
        logger.info(f"✅ {len(df)} lignes chargées depuis le fichier CSV")

        # Connexion SQL
        conn = get_sql_connection()
        cursor = conn.cursor()

        # Création de la table si elle n'existe pas
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='ips_lycee' AND xtype='U')
            CREATE TABLE ips_lycee (
                rentree_scolaire NVARCHAR(20),
                academie NVARCHAR(100),
                code_departement NVARCHAR(10),
                departement NVARCHAR(100),
                code_etablissement VARCHAR(20),
                nom_etablissement NVARCHAR(255),
                code_insee_commune NVARCHAR(10),
                commune NVARCHAR(100),
                secteur NVARCHAR(50),
                type_lycee NVARCHAR(50),
                ips_voie_gt FLOAT,
                ips_voie_pro FLOAT,
                ips_ensemble_gt_pro FLOAT,
                ecart_type_ips_voie_gt FLOAT,
                ecart_type_ips_voie_pro FLOAT
            )
        """)
        conn.commit()

        # Insertion
        for _, row in df.iterrows():
            cursor.execute("""
                INSERT INTO ips_lycee (
                    rentree_scolaire, academie, code_departement, departement,
                    code_etablissement, nom_etablissement, code_insee_commune, commune,
                    secteur, type_lycee, ips_voie_gt, ips_voie_pro,
                    ips_ensemble_gt_pro, ecart_type_ips_voie_gt, ecart_type_ips_voie_pro
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, tuple(row[col] if pd.notnull(row[col]) else None for col in df.columns))

        conn.commit()
        logger.info("✅ Données insérées dans la base SQL avec succès")

    except Exception as e:
        logger.error(f"❌ Erreur lors de l'import des données IPS lycée: {str(e)}")
        raise

    finally:
        try:
            close_sql_connection(conn)
        except:
            pass

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
