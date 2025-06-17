
import logging
from typing import List, Dict, Optional
import pyodbc

logger = logging.getLogger(__name__)

def fetch_all_lycees(conn: pyodbc.Connection) -> List[Dict]:
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ips_lycee")
        columns = [column[0] for column in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return results
    except Exception as e:
        logger.error(f"❌ Erreur lors de la récupération des données: {e}")
        raise

def fetch_lycee_by_code(conn: pyodbc.Connection, code_etablissement: str) -> Optional[Dict]:
    try:
        cursor = conn.cursor()
        query = "SELECT * FROM ips_lycee WHERE code_etablissement = ?"
        cursor.execute(query, (code_etablissement,))
        row = cursor.fetchone()
        if row:
            columns = [column[0] for column in cursor.description]
            return dict(zip(columns, row))
        return None
    except Exception as e:
        logger.error(f"❌ Erreur lors de la récupération du lycée : {e}")
        raise
