# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import ips_lycee, auth

app = FastAPI(
    title="Education Data API",
    description="API pour accéder aux données des lycées",
    version="1.0.0"
)

# Middleware CORS pour autoriser les requêtes depuis d'autres domaines (ex. front-end)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # à restreindre en prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routes
app.include_router(auth.router, prefix="/api/auth", tags=["Authentification"])
app.include_router(ips_lycee.router, prefix="/api/ips_lycee", tags=["IPS Lycée"])

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API Education Data 🎓"}
