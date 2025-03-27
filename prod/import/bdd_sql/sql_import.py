import pandas as pd
import logging
from .sql_connection import get_sql_connection, close_sql_connection

# Configuration du logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

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
            if_exists='replace',  # ou 'append' selon vos besoins
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
