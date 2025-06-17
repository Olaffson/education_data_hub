# database.py

import os
import logging
import pyodbc
from typing import Generator, List, Dict
from dotenv import load_dotenv

# Charger les variables d'environnement à partir du fichier .env
load_dotenv()

# Configuration du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Informations de connexion SQL
SQL_SERVER = os.getenv("SQL_SERVER")
SQL_DATABASE = os.getenv("SQL_DATABASE")
SQL_USERNAME = os.getenv("SQL_ADMIN_USERNAME")
SQL_PASSWORD = os.getenv("SQL_ADMIN_PASSWORD")
SQL_DRIVER = "{ODBC Driver 18 for SQL Server}"

CONNECTION_STRING = (
    f"Driver={SQL_DRIVER};"
    f"Server=tcp:{SQL_SERVER}.database.windows.net,1433;"
    f"Database={SQL_DATABASE};"
    f"Uid={SQL_USERNAME};"
    f"Pwd={SQL_PASSWORD};"
    f"Encrypt=yes;"
    f"TrustServerCertificate=no;"
    f"Connection Timeout=30;"
)

def get_db() -> Generator[pyodbc.Connection, None, None]:
    """Dépendance FastAPI pour gérer la connexion SQL dans les endpoints."""
    conn = None
    try:
        conn = pyodbc.connect(CONNECTION_STRING)
        logger.info("✅ Connexion à la base SQL réussie (FastAPI get_db).")
        yield conn
    except Exception as e:
        logger.error(f"❌ Erreur de connexion SQL : {e}")
        raise
    finally:
        if conn:
            conn.close()

def fetch_all_ips_lycee(conn) -> List[Dict]:
    """Récupère toutes les lignes de la table ips_lycee avec une connexion existante."""
    try:
        cursor = conn.cursor()
        query = "SELECT * FROM ips_lycee"
        cursor.execute(query)
        columns = [column[0] for column in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        logger.info(f"✅ {len(results)} lignes récupérées depuis la table.")
        return results
    except Exception as e:
        logger.error(f"❌ Erreur lors de la récupération des données : {e}")
        raise
