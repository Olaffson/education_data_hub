import logging
from bdd_sql.sql_import import import_csv_blob_to_sql

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def main():
    logger.info("📥 Import du fichier : effectifs_tg.csv")
    import_csv_blob_to_sql("effectifs_tg.csv")

if __name__ == "__main__":
    main()
