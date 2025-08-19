from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from config.settings import settings
from api import documents, workflows, stages, reports
from services.database import DatabaseService

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting AIDEPS Backend...")
    # Initialize the singleton db_service from database module
    from services.database import db_service
    await db_service.initialize()
    yield
    # Shutdown
    print("Shutting down AIDEPS Backend...")
    await db_service.close()

app = FastAPI(
    title="AIDEPS - AI Data Preparation System",
    description="Automated survey data preparation, analysis and report generation",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(workflows.router, prefix="/api/workflows", tags=["Workflows"]) 
app.include_router(stages.router, prefix="/api/stages", tags=["Stages"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])

@app.get("/")
async def root():
    return {
        "name": "AIDEPS API",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )