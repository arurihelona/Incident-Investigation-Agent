import logging
from typing import Dict, Any
from models.schemas import InvestigationRequest, InvestigationResponse, InvestigationStep
from agents.investigation_agent import InvestigationAgent

logger = logging.getLogger("investigation_service")

class InvestigationService:
    def __init__(self, investigation_agent: InvestigationAgent):
        self.investigation_agent = investigation_agent

    def investigate(self, request: InvestigationRequest) -> InvestigationResponse:
        q = request.question.strip() if request and request.question else ""
        if not q:
            return InvestigationResponse(
                question="",
                answer="No investigation question provided. Please submit an operational incident question.",
                evidence=[],
                investigation_steps=[
                    InvestigationStep(
                        step=1,
                        action="validation_failed",
                        query=None,
                        description="Investigation aborted: query string was empty."
                    )
                ],
                evidence_links=[],
                date_version_analysis="N/A",
                contradictions=[],
                similar_vs_identical=None,
                evidence_status="Insufficient",
                uncertainty="Insufficient evidence to determine this from the available documents.",
                raw_summary="Empty investigation query submitted."
            )

        try:
            return self.investigation_agent.investigate(request)
        except Exception as e:
            logger.error(f"Error executing investigation: {e}", exc_info=True)
            return InvestigationResponse(
                question=q,
                answer=f"Investigation could not be completed. Reason: {str(e)}",
                evidence=[],
                investigation_steps=[
                    InvestigationStep(
                        step=1,
                        action="execution_error",
                        query=None,
                        description=f"An unexpected error occurred during execution: {str(e)}"
                    )
                ],
                evidence_links=[],
                date_version_analysis="N/A",
                contradictions=[],
                similar_vs_identical=None,
                evidence_status="Insufficient",
                uncertainty="Investigation interrupted due to a system error.",
                raw_summary=f"Execution error: {str(e)}"
            )
