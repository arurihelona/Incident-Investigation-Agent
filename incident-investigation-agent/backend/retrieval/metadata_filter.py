from typing import Optional, Dict, Any, List

class MetadataFilter:
    """Helper to construct ChromaDB compatible metadata queries."""

    @staticmethod
    def build_filter(
        service: Optional[str] = None,
        doc_type: Optional[str] = None,
        version: Optional[str] = None,
        date: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        conditions = []
        if service:
            conditions.append({"service": service})
        if doc_type:
            conditions.append({"type": doc_type})
        if version:
            conditions.append({"version": version})
        if date:
            conditions.append({"date": date})

        if not conditions:
            return None
        if len(conditions) == 1:
            return conditions[0]
        return {"$and": conditions}

    @staticmethod
    def filter_documents_in_memory(
        documents: List[Dict[str, Any]],
        service: Optional[str] = None,
        doc_type: Optional[str] = None,
        version: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """In-memory metadata filtering fallback or secondary refinement."""
        filtered = []
        for doc in documents:
            meta = doc.get("metadata", doc)
            if service and meta.get("service") != service:
                continue
            if doc_type and meta.get("type") != doc_type:
                continue
            if version and meta.get("version") != version:
                continue
            filtered.append(doc)
        return filtered
