from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.database.database import init_db
from src.api.routes import router
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="InsightX - Conversational AI for Payment Analytics",
    description="Natural language interface for querying transaction data",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
@app.on_event("startup")
async def startup_event():
    """Initialize database and load data if needed"""
    try:
        init_db()
        print("✓ Database initialized successfully")
        
        # Check if database has data, if not load sample data
        from src.database.database import SessionLocal
        from src.database.models import Transaction
        
        db = SessionLocal()
        transaction_count = db.query(Transaction).count()
        db.close()
        
        if transaction_count == 0:
            print("📦 Database is empty. Loading sample transactions...")
            from src.database.data_loader import DataLoader
            loader = DataLoader()
            loader.load_and_populate(num_synthetic=250000)
            print("✓ Sample data loaded successfully")
    except Exception as e:
        print(f"✗ Startup error: {e}")
        # Don't crash, continue with empty database if needed

# Include routes
app.include_router(router, prefix="/api", tags=["queries"])

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": "InsightX Conversational AI",
        "description": "Natural language interface for digital payment analytics",
        "version": "1.0.0",
        "endpoints": {
            "query": "/api/query (POST)",
            "health": "/api/health (GET)",
            "supported_entities": "/api/supported-entities (GET)",
            "example_queries": "/api/example-queries (GET)"
        },
        "documentation": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    # Railway sets PORT env var, fallback to 8000 for local
    port = int(os.getenv("PORT", os.getenv("FASTAPI_PORT", 8000)))
    host = os.getenv("FASTAPI_HOST", "0.0.0.0")
    
    print(f"🚀 Starting server on {host}:{port}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=False
    )
