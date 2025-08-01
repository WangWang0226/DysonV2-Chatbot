from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from app.routers import chat

load_dotenv()

app = FastAPI(title="DysonV2 Chatbot API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "DysonV2 Chatbot API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}