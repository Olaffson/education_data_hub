from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from app.auth import hash_password, verify_password, create_access_token, decode_access_token
from app.database import get_db
import pyodbc
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

security = HTTPBearer()
SECRET_KEY = os.getenv("SECRET_KEY", "dev-key")
ALGORITHM = "HS256"

router = APIRouter(prefix="/auth", tags=["Authentification"])

class UserRegister(BaseModel):
    email: str
    mot_de_passe: str
    nom: str
    prenom: str

@router.post("/register")
def register(user: UserRegister, db: pyodbc.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ?", user.email)
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="📧 Email déjà utilisé")

    hashed_pwd = hash_password(user.mot_de_passe)
    cursor.execute("""
        INSERT INTO users (nom, prenom, email, mot_de_passe)
        VALUES (?, ?, ?, ?)""", user.nom, user.prenom, user.email, hashed_pwd)
    db.commit()
    return {"message": "✅ Utilisateur enregistré avec succès"}

@router.post("/login")
def login(email: str = Form(...), mot_de_passe: str = Form(...), db: pyodbc.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT id, mot_de_passe FROM users WHERE email = ?", email)
    row = cursor.fetchone()
    if not row or not verify_password(mot_de_passe, row.mot_de_passe):
        raise HTTPException(status_code=401, detail="❌ Email ou mot de passe incorrect")

    token = create_access_token(data={"sub": email})
    return {"access_token": token, "token_type": "bearer"}

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="⚠️ Token invalide ou expiré",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        user_email: str = payload.get("sub")
        if user_email is None:
            raise credentials_exception
        return user_email
    except JWTError:
        raise credentials_exception
