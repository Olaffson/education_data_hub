import pyodbc
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

SQL_SERVER = os.getenv("SQL_SERVER")
SQL_DATABASE = os.getenv("SQL_DATABASE")
SQL_USERNAME = os.getenv("SQL_ADMIN_USERNAME")
SQL_PASSWORD = os.getenv("SQL_ADMIN_PASSWORD")
SQL_DRIVER = "{ODBC Driver 18 for SQL Server}"

CONNECTION_STRING = f"""
    DRIVER={SQL_DRIVER};
    SERVER=tcp:{SQL_SERVER}.database.windows.net,1433;
    DATABASE={SQL_DATABASE};
    UID={SQL_USERNAME};
    PWD={SQL_PASSWORD};
    Encrypt=yes;
    TrustServerCertificate=no;
    Connection Timeout=30;
"""

create_table_query = """
CREATE TABLE users (
    id INT PRIMARY KEY IDENTITY(1,1),
    nom NVARCHAR(100) NOT NULL,
    prenom NVARCHAR(100) NOT NULL,
    email NVARCHAR(255) NOT NULL UNIQUE,
    mot_de_passe NVARCHAR(255) NOT NULL,
    date_inscription DATETIME DEFAULT GETDATE()
)
"""

try:
    with pyodbc.connect(CONNECTION_STRING) as conn:
        cursor = conn.cursor()
        cursor.execute(create_table_query)
        conn.commit()
        print("✅ Table 'users' créée avec succès.")
except Exception as e:
    print("❌ Erreur lors de la création de la table :", e)
