# src/api/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.endpoints import goride,gofood,gopay

app = FastAPI(
    title="Gojek Enterprise OLAP API",
    description="Backend FastAPI penyuplai data analitik untuk Dashboard Next.js",
    version="1.0.0"
)

# Konfigurasi CORS (Wajib agar Next.js di port 3000 bisa mengambil data)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(goride.router)
app.include_router(gofood.router)
app.include_router(gopay.router)

@app.get("/")
def root_check():
    return {
        "status": "OK", 
        "message": "Gojek OLAP API Server berjalan normal!",
        "docs": "Kunjungi /docs untuk melihat Swagger UI"
    }