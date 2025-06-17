# models.py

from pydantic import BaseModel
from typing import Optional


class IpsLyceeOut(BaseModel):
    rentree_scolaire: Optional[str]
    academie: Optional[str]
    code_departement: Optional[str]
    departement: Optional[str]
    code_etablissement: Optional[str]
    nom_etablissement: Optional[str]
    code_insee_commune: Optional[str]
    commune: Optional[str]
    secteur: Optional[str]
    type_lycee: Optional[str]
    effectifs_voie_gt: Optional[float]
    effectifs_voie_pro: Optional[float]
    effectifs_ensemble_gt_pro: Optional[float]
    ips_voie_gt: Optional[float]
    ips_voie_pro: Optional[float]
    ips_ensemble_gt_pro: Optional[float]
    ecart_type_ips_voie_gt: Optional[float]
    ecart_type_ips_voie_pro: Optional[float]

    class Config:
        orm_mode = True
