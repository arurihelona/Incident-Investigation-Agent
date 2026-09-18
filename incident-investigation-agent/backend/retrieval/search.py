from typing import List, Dict, Any, Optional
from retrieval.vector_store import VectorStore
from retrieval.metadata_filter import MetadataFilter

class RetrievalService:
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store

    def search(
        self,
        query: str,
        limit: int = 5,
        service: Optional[str] = None,
        doc_type: Optional[str] = None,
        version: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Performs semantic search with optional metadata filtering."""
        where_filter = MetadataFilter.build_filter(
            service=service,
            doc_type=doc_type,
            version=version
        )
        results = self.vector_store.query_semantic(
            query=query,
            n_results=limit,
            where_filter=where_filter
        )
        return results

    def get_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        return self.vector_store.get_document_by_id(doc_id)

    def list_all(self) -> List[Dict[str, Any]]:
        return self.vector_store.get_all_documents()
