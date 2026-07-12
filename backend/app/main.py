from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routers import auth, interns

Base.metadata.create_all(bind=engine)

app = FastAPI(title="PIA Intern ID System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(interns.router)


@app.get("/")
def root():
    return {"status": "ok", "service": "PIA Intern ID System"}
