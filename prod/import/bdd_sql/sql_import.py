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

def import_csv_blob_to_sql(blob_name: str):
    """
    Importe un fichier CSV depuis Azure Blob Storage dans une table SQL.
    Le nom de la table sera dérivé du nom du fichier sans extension.
    """
    table_name = os.path.splitext(blob_name)[0]
    logger.info(f"📥 Début import des données dans la table '{table_name}' depuis le blob '{blob_name}'")

    try:
        # Authentification Azure
        credential = DefaultAzureCredential()
        blob_service_client = BlobServiceClient(account_url=BLOB_ACCOUNT_URL, credential=credential)
        blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=blob_name)
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

        # Suppression de la table si elle existe
        cursor.execute(f"IF OBJECT_ID('{table_name}', 'U') IS NOT NULL DROP TABLE {table_name}")
        conn.commit()

        # Création dynamique de la table
        col_defs = []
        for col in df.columns:
            dtype = df[col].dtype
            if pd.api.types.is_integer_dtype(dtype):
                sql_type = "INT"
            elif pd.api.types.is_float_dtype(dtype):
                sql_type = "FLOAT"
            else:
                sql_type = "NVARCHAR(MAX)"
            col_defs.append(f"[{col}] {sql_type}")

        create_sql = f"CREATE TABLE {table_name} ({', '.join(col_defs)})"
        cursor.execute(create_sql)
        conn.commit()

        # Insertion des données
        placeholders = ", ".join(["?"] * len(df.columns))
        insert_sql = f"""
            INSERT INTO {table_name} ({', '.join(f'[{col}]' for col in df.columns)})
            VALUES ({placeholders})
        """
        for _, row in df.iterrows():
            values = [row[col] if pd.notnull(row[col]) else None for col in df.columns]
            cursor.execute(insert_sql, values)

        conn.commit()
        logger.info(f"✅ Données insérées dans la table {table_name} avec succès")

    except Exception as e:
        logger.error(f"❌ Erreur lors de l'import des données dans la table {table_name}: {str(e)}")
        raise

    finally:
        try:
            close_sql_connection(conn)
        except:
            pass

# remplacer par import_csv_blob_to_sql
def import_ips_lycee_to_sql():
    logger.info("📥 Début import des données IPS lycée")

    BLOB_NAME = "ips_lycee.csv"

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

        # Création de la table avec les 18 colonnes actuelles
        cursor.execute("""
            IF OBJECT_ID('ips_lycee', 'U') IS NULL
            CREATE TABLE ips_lycee (
                rentree_scolaire NVARCHAR(20),
                academie NVARCHAR(100),
                code_du_departement NVARCHAR(10),
                departement NVARCHAR(100),
                uai VARCHAR(20),
                nom_de_l_etablissment NVARCHAR(255),
                code_insee_de_la_commune NVARCHAR(10),
                nom_de_la_commune NVARCHAR(100),
                secteur NVARCHAR(50),
                type_de_lycee NVARCHAR(50),
                ips_voie_gt FLOAT,
                ips_voie_pro FLOAT,
                ips_ensemble_gt_pro FLOAT,
                ecart_type_de_l_ips_voie_gt FLOAT,
                ecart_type_de_l_ips_voie_pro FLOAT,
                effectifs_voie_gt INT,
                effectifs_voie_pro INT,
                effectifs_ensemble_gt_pro INT
            )
        """)
        conn.commit()

        # Insertion
        for _, row in df.iterrows():
            cursor.execute("""
                INSERT INTO ips_lycee (
                    rentree_scolaire, academie, code_du_departement, departement,
                    uai, nom_de_l_etablissment, code_insee_de_la_commune, nom_de_la_commune,
                    secteur, type_de_lycee, ips_voie_gt, ips_voie_pro,
                    ips_ensemble_gt_pro, ecart_type_de_l_ips_voie_gt, ecart_type_de_l_ips_voie_pro,
                    effectifs_voie_gt, effectifs_voie_pro, effectifs_ensemble_gt_pro
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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

# remplacer par import_csv_blob_to_sql
def import_effectifs_tg_to_sql():
    logger.info("📥 Début import des données Effectifs TG")

    BLOB_NAME = "effectifs_tg.csv"

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

        # Création dynamique de la table
        col_defs = []
        for col in df.columns:
            dtype = df[col].dtype
            if pd.api.types.is_integer_dtype(dtype):
                sql_type = "INT"
            elif pd.api.types.is_float_dtype(dtype):
                sql_type = "FLOAT"
            else:
                sql_type = "NVARCHAR(MAX)"
            col_defs.append(f"[{col}] {sql_type}")

        create_table_sql = f"""
            IF OBJECT_ID('effectifs_tg', 'U') IS NULL
            CREATE TABLE effectifs_tg (
                {', '.join(col_defs)}
            )
        """
        cursor.execute(create_table_sql)
        conn.commit()

        # Insertion dynamique
        placeholders = ", ".join(["?"] * len(df.columns))
        insert_sql = f"""
            INSERT INTO effectifs_tg ({', '.join(f'[{col}]' for col in df.columns)})
            VALUES ({placeholders})
        """

        for _, row in df.iterrows():
            values = [row[col] if pd.notnull(row[col]) else None for col in df.columns]
            cursor.execute(insert_sql, values)

        conn.commit()
        logger.info("✅ Données insérées dans la base SQL avec succès")

    except Exception as e:
        logger.error(f"❌ Erreur lors de l'import des données Effectifs TG : {str(e)}")
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
