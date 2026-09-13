from fastapi import FastAPI
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from streamingbackend.routes.chatbot_route import chatbot_router
from streamingbackend.routes.rag_route import rag_router

app = FastAPI(
    title="Streaming Backend",
    description="A backend for streaming data in langgraph and fastapi",
    version="1.0.0",
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Streaming Backend is running")

@app.get("/")
def read_root():
    # this return the status of health and general information about the backend
    return {
        "status": "healthy",
        "message": "Streaming Backend is running",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
    }
    
app.include_router(chatbot_router)
app.include_router(rag_router)