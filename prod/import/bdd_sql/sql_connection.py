import os
import logging
import pyodbc

# Configuration du logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Configuration Azure SQL
SQL_SERVER_NAME = "sqlserver-okotwica-prod"
SQL_DATABASE_NAME = "EducationData"
SQL_USERNAME = os.environ.get("SQL_ADMIN_USERNAME")
SQL_PASSWORD = os.environ.get("SQL_ADMIN_PASSWORD")
SQL_DRIVER = "{ODBC Driver 18 for SQL Server}"
SQL_CONNECTION_STRING = f"Driver={SQL_DRIVER};Server=tcp:{SQL_SERVER_NAME}.database.windows.net,1433;Database={SQL_DATABASE_NAME};Uid={SQL_USERNAME};Pwd={SQL_PASSWORD};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"

def get_sql_connection():
    """Établit et retourne une connexion à la base de données SQL"""
    try:
        conn = pyodbc.connect(SQL_CONNECTION_STRING)
        logger.info("✅ Connexion à la base de données SQL établie")
        return conn
    except Exception as e:
        logger.error(f"❌ Erreur de connexion à la base de données SQL: {str(e)}")
        raise

def close_sql_connection(conn):
    """Ferme la connexion à la base de données SQL"""
    try:
        if conn:
            conn.close()
            logger.info("✅ Connexion à la base de données SQL fermée")
    except Exception as e:
        logger.error(f"❌ Erreur lors de la fermeture de la connexion SQL: {str(e)}")
        raise
