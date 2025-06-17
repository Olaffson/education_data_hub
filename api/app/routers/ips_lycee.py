
from fastapi import APIRouter, Depends, HTTPException
from app.database import get_db
from app.crud import fetch_all_lycees, fetch_lycee_by_code
from app.routers.auth import get_current_user
from typing import List, Dict, Optional
import pyodbc

router = APIRouter()

@router.get("/", response_model=List[Dict], summary="Lister tous les lycées")
def list_lycees(
    db: pyodbc.Connection = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    return fetch_all_lycees(db)

@router.get("/{code_etablissement}", response_model=Optional[Dict], summary="Récupérer un lycée par son code établissement")
def get_lycee_by_code(
    code_etablissement: str,
    db: pyodbc.Connection = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    result = fetch_lycee_by_code(db, code_etablissement)
    if result is None:
        raise HTTPException(status_code=404, detail="Lycée non trouvé")
    return result
