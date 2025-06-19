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

class EcoleEffectifOut(BaseModel):
    rentree_scolaire: Optional[int]
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
