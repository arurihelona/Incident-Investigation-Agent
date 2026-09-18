import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.utils import embedding_functions

from config import CHROMA_PERSIST_DIR, DATA_PATH
from models.schemas import Document

logger = logging.getLogger("vector_store")

class VectorStore:
    def __init__(self, persist_dir: str = CHROMA_PERSIST_DIR):
        self.persist_dir = persist_dir
        Path(self.persist_dir).mkdir(parents=True, exist_ok=True)
        # Persistent client so data survives restarts
        self.client = chromadb.PersistentClient(path=self.persist_dir)
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        self.collection_name = "incident_documents"
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"}
        )

    def index_documents(self, documents: List[Document]) -> int:
        """Indexes documents with rich searchable text and metadata."""
        if not documents:
            return 0

        # We can clear existing to ensure a clean sync
        try:
            existing = self.collection.get()
            if existing and existing.get("ids"):
                self.collection.delete(ids=existing["ids"])
        except Exception as e:
            logger.warning(f"Notice while clearing collection: {e}")

        ids = []
        texts = []
        metadatas = []

        for doc in documents:
            ids.append(doc.document_id)
            # Create a rich composite chunk text for maximum semantic retrieval
            content_chunk = (
                f"Document ID: {doc.document_id}\n"
                f"Title: {doc.title}\n"
                f"Type: {doc.type}\n"
                f"Service: {doc.service or 'general'}\n"
                f"Date: {doc.date}\n"
                f"Version: {doc.version}\n"
                f"Content: {doc.content}"
            )
            texts.append(content_chunk)
            metadatas.append({
                "document_id": doc.document_id,
                "type": doc.type,
                "service": doc.service or "",
                "date": doc.date,
                "version": doc.version,
                "title": doc.title,
                "content": doc.content
            })

        self.collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas
        )
        logger.info(f"Indexed {len(ids)} documents into ChromaDB collection '{self.collection_name}'")
        return len(ids)

    def load_and_index_from_file(self, file_path: str = DATA_PATH) -> int:
        """Loads documents from JSON file and indexes them."""
        p = Path(file_path)
        if not p.exists():
            raise FileNotFoundError(f"Documents file not found: {file_path}")
        with open(p, "r", encoding="utf-8") as f:
            raw_docs = json.load(f)
        docs = [Document(**d) for d in raw_docs]
        return self.index_documents(docs)

    def query_semantic(
        self,
        query: str,
        n_results: int = 5,
        where_filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Queries documents using semantic similarity with optional metadata filtering."""
        count = self.collection.count()
        if count == 0:
            return []

        actual_n = min(n_results, count)
        kwargs = {
            "query_texts": [query],
            "n_results": actual_n
        }
        if where_filter:
            kwargs["where"] = where_filter

        try:
            results = self.collection.query(**kwargs)
        except Exception as e:
            logger.error(f"Error querying ChromaDB: {e}")
            # Fallback without where filter if filter was malformed or empty
            results = self.collection.query(query_texts=[query], n_results=actual_n)

        out = []
        if not results or not results.get("ids") or not results["ids"][0]:
            return []

        ids = results["ids"][0]
        metadatas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(ids)
        distances = results["distances"][0] if results.get("distances") else [0.0] * len(ids)

        for doc_id, meta, dist in zip(ids, metadatas, distances):
            # Cosine distance ranges from 0 (identical) to 2 (opposite)
            # Normalize to 0.0 - 1.0 similarity score
            score = max(0.0, min(1.0, 1.0 - (dist / 2.0)))
            out.append({
                "document_id": doc_id,
                "score": round(score, 3),
                "metadata": {
                    "type": meta.get("type", ""),
                    "service": meta.get("service", ""),
                    "date": meta.get("date", ""),
                    "version": meta.get("version", ""),
                    "title": meta.get("title", "")
                },
                "content": meta.get("content", "")
            })

        return out

    def get_document_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a single document by its ID."""
        try:
            res = self.collection.get(ids=[doc_id])
            if res and res.get("ids") and len(res["ids"]) > 0:
                meta = res["metadatas"][0]
                return {
                    "document_id": res["ids"][0],
                    "metadata": {
                        "type": meta.get("type", ""),
                        "service": meta.get("service", ""),
                        "date": meta.get("date", ""),
                        "version": meta.get("version", ""),
                        "title": meta.get("title", "")
                    },
                    "content": meta.get("content", "")
                }
        except Exception as e:
            logger.error(f"Error getting document {doc_id}: {e}")
        return None

    def get_all_documents(self) -> List[Dict[str, Any]]:
        """Returns all documents stored in the vector store."""
        try:
            res = self.collection.get()
            if not res or not res.get("ids"):
                return []
            docs = []
            for doc_id, meta in zip(res["ids"], res["metadatas"]):
                docs.append({
                    "document_id": doc_id,
                    "type": meta.get("type", ""),
                    "service": meta.get("service", ""),
                    "date": meta.get("date", ""),
                    "version": meta.get("version", ""),
                    "title": meta.get("title", ""),
                    "content": meta.get("content", "")
                })
            return docs
        except Exception as e:
            logger.error(f"Error fetching all documents: {e}")
            return []
