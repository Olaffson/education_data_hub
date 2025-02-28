import pandas as pd
import io
import logging

logger = logging.getLogger(__name__)

def clean_csv_data(csv_data: bytes) -> bytes:
    """
    Nettoie un fichier CSV (suppression des lignes vides, doublons, normalisation des colonnes).
    """
    try:
        df = pd.read_csv(io.BytesIO(csv_data))
        df.dropna(inplace=True)
        df.drop_duplicates(inplace=True)
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

        output = io.BytesIO()
        df.to_csv(output, index=False)
        return output.getvalue()
    except Exception as e:
        logger.error("Erreur lors du nettoyage du CSV: %s", e)
        raise

def clean_json_data(json_data: bytes) -> bytes:
    """
    Nettoie un fichier JSON (suppression des clés vides, formatage correct).
    """
    try:
        df = pd.read_json(io.BytesIO(json_data))
        df.dropna(inplace=True)
        df.drop_duplicates(inplace=True)

        output = io.BytesIO()
        df.to_json(output, orient="records", indent=4)
        return output.getvalue()
    except Exception as e:
        logger.error("Erreur lors du nettoyage du JSON: %s", e)
        raise

def clean_excel_data(excel_data: bytes) -> bytes:
    """
    Nettoie un fichier Excel (suppression des lignes vides, doublons).
    """
    try:
        df = pd.read_excel(io.BytesIO(excel_data))
        df.dropna(inplace=True)
        df.drop_duplicates(inplace=True)

        output = io.BytesIO()
        df.to_excel(output, index=False, engine='xlsxwriter')
        return output.getvalue()
    except Exception as e:
        logger.error("Erreur lors du nettoyage de l'Excel: %s", e)
        raise
