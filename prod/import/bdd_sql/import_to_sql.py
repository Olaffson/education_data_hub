import logging
from bdd_sql.sql_import import import_csv_blob_to_sql

# Configuration du logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

CSV_BLOBS = [
    "ips_lycee.csv",
    "effectifs_tg.csv",
    "ecoles_effectifs.csv",
    "bac_par_academie.csv"
]

def main():
    logger.info("🚀 Début de l'import des fichiers CSV vers SQL")

    for blob_name in CSV_BLOBS:
        try:
            logger.info(f"🔄 Import du fichier : {blob_name}")
            import_csv_blob_to_sql(blob_name)
        except Exception as e:
            logger.error(f"❌ Échec de l'import pour {blob_name} : {e}")

    logger.info("🏁 Import terminé pour tous les fichiers")

if __name__ == "__main__":
    main()


# from bdd_sql.sql_import import import_csv_blob_to_sql

# def main():
#     import_csv_blob_to_sql("ips_lycee.csv")
#     import_csv_blob_to_sql("effectifs_tg.csv")
#     import_csv_blob_to_sql("ecoles_effectifs.csv")
#     import_csv_blob_to_sql("bac_par_academie.csv")

# if __name__ == "__main__":
#     main()
