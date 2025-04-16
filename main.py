# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routes import router

app = FastAPI(title="Video Censorship API")

# CORS for local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve output videos
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

# Include video upload endpoint
app.include_router(router)