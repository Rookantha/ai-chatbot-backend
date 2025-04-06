# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.chat import router  # <-- Import the router correctly
from app.logger import logger

app = FastAPI()

# Configure CORS to allow requests from your frontend (adjust origin as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the router for chat API
app.include_router(router)  # <-- Include the router instead of chat_router

# Log that the app is running
logger.info("FastAPI app is running")
