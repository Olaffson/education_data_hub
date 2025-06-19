import logging
from bdd_sql.sql_import import import_csv_blob_to_sql

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def main():
    logger.info("📥 Import du fichier : ecoles_effectifs.csv")
    import_csv_blob_to_sql("ecoles_effectifs.csv")

if __name__ == "__main__":
    main()
