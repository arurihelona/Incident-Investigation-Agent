import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from config import DATA_PATH
from retrieval.vector_store import VectorStore
from models.schemas import Document

logger = logging.getLogger("document_service")

class DocumentService:
    def __init__(self, vector_store: VectorStore, data_path: str = DATA_PATH):
        self.vector_store = vector_store
        self.data_path = Path(data_path)

    def load_documents_from_json(self) -> List[Document]:
        if not self.data_path.exists():
            raise FileNotFoundError(f"Documents file does not exist at {self.data_path}")
        with open(self.data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [Document(**d) for d in data]

    def reindex(self) -> int:
        docs = self.load_documents_from_json()
        count = self.vector_store.index_documents(docs)
        logger.info(f"Re-indexed {count} documents into ChromaDB vector store.")
        return count

    def get_all(self) -> List[Dict[str, Any]]:
        # Prefer vector store contents, fallback to json if empty
        docs = self.vector_store.get_all_documents()
        if not docs and self.data_path.exists():
            with open(self.data_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return docs

    def get_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        return self.vector_store.get_document_by_id(doc_id)
