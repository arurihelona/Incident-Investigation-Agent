import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from config import HOST, PORT, LLM_PROVIDER, LLM_MODEL, CHROMA_PERSIST_DIR
from models.schemas import InvestigationRequest, InvestigationResponse
from retrieval.vector_store import VectorStore
from retrieval.search import RetrievalService
from agents.investigation_agent import InvestigationAgent
from services.document_service import DocumentService
from services.investigation_service import InvestigationService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("main")

# Initialize Singletons
vector_store = VectorStore(persist_dir=CHROMA_PERSIST_DIR)
retrieval_service = RetrievalService(vector_store=vector_store)
investigation_agent = InvestigationAgent(retrieval_service=retrieval_service)
document_service = DocumentService(vector_store=vector_store)
investigation_service = InvestigationService(investigation_agent=investigation_agent)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure documents are loaded and indexed
    logger.info("Initializing Incident Investigation Agent vector store...")
    try:
        count = document_service.reindex()
        logger.info(f"Vector store initialized successfully with {count} documents.")
    except Exception as e:
        logger.error(f"Failed to auto-index documents on startup: {e}")
    yield
    logger.info("Shutting down Incident Investigation Agent backend...")

app = FastAPI(
    title="Incident Investigation Agent API",
    description="Backend API for evidence-driven operational incident investigation.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def get_health():
    docs = document_service.get_all()
    return {
        "status": "healthy",
        "service": "incident-investigation-agent",
        "documents_indexed": len(docs),
        "llm_provider": LLM_PROVIDER,
        "llm_model": LLM_MODEL,
        "vector_db": "ChromaDB"
    }

@app.get("/api/documents")
def get_documents():
    docs = document_service.get_all()
    return {
        "total": len(docs),
        "documents": docs
    }

@app.post("/api/reindex")
def reindex_documents():
    try:
        count = document_service.reindex()
        return {
            "status": "success",
            "message": f"Successfully re-indexed {count} documents into vector store.",
            "documents_indexed": count
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Reindexing failed: {str(e)}"
        )

@app.post("/api/investigate", response_model=InvestigationResponse)
def investigate_incident(request: InvestigationRequest):
    try:
        return investigation_service.investigate(request)
    except Exception as e:
        logger.error(f"Investigation request error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Investigation failed: {str(e)}"
        )

from fastapi.staticfiles import StaticFiles
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIST = BASE_DIR.parent / "frontend" / "dist"

if FRONTEND_DIST.exists():
    logger.info(f"Mounting static frontend build from {FRONTEND_DIST}")
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=HOST, port=PORT, reload=False)

