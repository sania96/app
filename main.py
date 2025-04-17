# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routes import router
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Video Censorship API")

# Get the EC2 public IP from the environment variable
ec2_public_ip = os.getenv("REACT_APP_EC2_PUBLIC_IP")
frontend_ec2_origin = None
if ec2_public_ip:
    frontend_ec2_origin = f"http://{ec2_public_ip}:3000"
    allowed_origins = ["http://localhost:3000", frontend_ec2_origin]
else:
    allowed_origins = ["http://localhost:3000"]
    print("Warning: REACT_APP_EC2_PUBLIC_IP environment variable not set. Only allowing localhost origin for CORS.")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve output videos
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

# Include video upload endpoint
app.include_router(router)