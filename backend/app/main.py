import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from .database import Base, engine
from .routers import auth, cards, documents, interns, certificates, security_letters

load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI(title="PIA Intern ID System")

cors_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(interns.router)
app.include_router(cards.router)
app.include_router(documents.router)
app.include_router(certificates.router)
app.include_router(security_letters.router)



@app.get("/")
def root():
    return {"status": "ok", "service": "PIA Intern ID System"}
