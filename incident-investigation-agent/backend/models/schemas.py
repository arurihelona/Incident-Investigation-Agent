from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class Document(BaseModel):
    document_id: str
    type: str
    service: Optional[str] = None
    date: str
    version: str
    title: str
    content: str

class EvidenceItem(BaseModel):
    document_id: str
    type: str
    service: Optional[str] = None
    date: str
    version: str
    title: str
    content: str
    relevance_score: float = Field(default=1.0, description="Relevance similarity score (0.0 to 1.0)")

class InvestigationStep(BaseModel):
    step: int
    action: str
    query: Optional[str] = None
    description: str
    details: Optional[Dict[str, Any]] = None

class EvidenceLink(BaseModel):
    source_id: str
    target_id: str
    relationship: str
    description: str

class ContradictionDocInfo(BaseModel):
    document_id: str
    date: str
    version: str
    title: str
    guidance: str

class ContradictionItem(BaseModel):
    detected: bool
    doc_a: ContradictionDocInfo
    doc_b: ContradictionDocInfo
    newer_doc_id: str
    explanation: str

class InvestigationMetrics(BaseModel):
    initial_searches: int = 1
    follow_up_searches: int = 0
    total_retrieval_calls: int = 0
    investigation_hops: int = 0
    unique_documents_retrieved: int = 0
    cycles_detected: int = 0
    max_hop_limit: int = 3
    investigation_status: str = "Completed"
    stop_reason: str = "Investigation completed: evidence sufficient."

class SimilarVsIdentical(BaseModel):
    is_identical: bool
    service_match: bool
    failure_mechanism_match: bool
    current_context: str
    previous_context: str
    explanation: str

class InvestigationRequest(BaseModel):
    question: str

class InvestigationResponse(BaseModel):
    question: str
    answer: str
    evidence: List[EvidenceItem]
    investigation_steps: List[InvestigationStep]
    evidence_links: List[EvidenceLink]
    date_version_analysis: str
    contradictions: List[ContradictionItem]
    similar_vs_identical: Optional[SimilarVsIdentical] = None
    evidence_status: str  # "Sufficient" | "Insufficient"
    uncertainty: str
    evidence_gap: List[str] = Field(default_factory=list)
    stop_reason: Optional[str] = None
    metrics: Optional[InvestigationMetrics] = None
    raw_summary: Optional[str] = None

