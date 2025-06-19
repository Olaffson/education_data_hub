import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

class Settings:
    PROJECT_NAME: str = "EducationDataHub API"
    PROJECT_VERSION: str = "1.0.0"
    
    SQL_SERVER: str = os.getenv("SQL_SERVER")
    SQL_DATABASE: str = os.getenv("SQL_DATABASE")
    SQL_USERNAME: str = os.getenv("SQL_USERNAME")
    SQL_PASSWORD: str = os.getenv("SQL_PASSWORD")
    SQL_DRIVER: str = "ODBC Driver 18 for SQL Server"

    DATABASE_URL: str = (
        f"mssql+pyodbc://{SQL_USERNAME}:{SQL_PASSWORD}" 
        f"@{SQL_SERVER}.database.windows.net:1433/{SQL_DATABASE}"
        f"?driver={SQL_DRIVER.replace(' ', '+')}"
    )

    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "secret")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

settings = Settings()

# Pydantic model pour les données IPS lycée
class IpsLycee(BaseModel):
    rentree_scolaire: str
    academie: str
    code_departement: str
    departement: str
    code_etablissement: str
    nom_etablissement: str
    code_insee_commune: str
    commune: str
    secteur: str
    type_lycee: str
    effectifs_voie_gt: Optional[float] = None
    effectifs_voie_pro: Optional[float] = None
    effectifs_ensemble_gt_pro: Optional[float] = None
    ips_voie_gt: Optional[float] = None
    ips_voie_pro: Optional[float] = None
    ips_ensemble_gt_pro: Optional[float] = None
    ecart_type_ips_voie_gt: Optional[float] = None
    ecart_type_ips_voie_pro: Optional[float] = None

class EcolesEffectifs(BaseModel):
    rentree_scolaire: int
    region_academique: Optional[str]
    academie: Optional[str]
    departement: Optional[str]
    commune: Optional[str]
    numero_de_l_ecole: Optional[str]
    denomination_principale: Optional[str]
    patronyme: Optional[str]
    secteur: Optional[str]
    rep: Optional[int]
    rep_plus: Optional[int]
    nombre_total_de_classes: Optional[int]
    nombre_total_d_eleves: Optional[int]
    nombre_d_eleves_en_pre_elementaire_hors_ulis: Optional[int]
    nombre_d_eleves_en_elementaire_hors_ulis: Optional[int]
    nombre_d_eleves_en_ulis: Optional[int]
    nombre_d_eleves_en_cp_hors_ulis: Optional[int]
    nombre_d_eleves_en_ce1_hors_ulis: Optional[int]
    nombre_d_eleves_en_ce2_hors_ulis: Optional[int]
    nombre_d_eleves_en_cm1_hors_ulis: Optional[int]
    nombre_d_eleves_en_cm2_hors_ulis: Optional[int]
    tri: Optional[str]
    code_postal: Optional[int]
