import unittest
import sys
import os
from pathlib import Path

# Add backend directory to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from retrieval.vector_store import VectorStore
from retrieval.search import RetrievalService
from agents.investigation_agent import InvestigationAgent
from models.schemas import InvestigationRequest
from services.document_service import DocumentService

class TestIncidentInvestigationAgent(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Use a temporary test chroma db
        test_chroma_dir = str(BASE_DIR / "test_chroma_db")
        cls.vector_store = VectorStore(persist_dir=test_chroma_dir)
        cls.document_service = DocumentService(vector_store=cls.vector_store)
        count = cls.document_service.reindex()
        assert count >= 7, f"Expected at least 7 documents indexed, got {count}"
        cls.retrieval_service = RetrievalService(vector_store=cls.vector_store)
        cls.agent = InvestigationAgent(retrieval_service=cls.retrieval_service)

    def test_scenario_a_deployment_investigation(self):
        """Test A: Why did the Order API become slow on September 16? Check whether the deployment was related and whether we have seen this before."""
        question = "Why did the Order API become slow on September 16? Check whether the deployment was related and whether we have seen this before."
        req = InvestigationRequest(question=question)
        resp = cls_agent = self.agent.investigate(req)

        # 1. Verify INC-1042 retrieved
        doc_ids = [e.document_id for e in resp.evidence]
        self.assertIn("INC-1042", doc_ids, "INC-1042 must be retrieved")

        # 2. Verify follow-up search occurred
        step_actions = [s.action for s in resp.investigation_steps]
        self.assertIn("follow_up_search", step_actions, "Agent must perform follow-up search based on discovered facts")

        # 3. Verify DEP-882 and PM-211 retrieved via multi-hop
        self.assertIn("DEP-882", doc_ids, "DEP-882 must be discovered via deployment follow-up search")
        self.assertIn("PM-211", doc_ids, "PM-211 must be discovered via historical incident search")

        # 4. Verify date and version preserved
        self.assertIn("2026-09-16", resp.date_version_analysis)
        self.assertIn("2026-09-15", resp.date_version_analysis)
        self.assertIn("v2.8.1", resp.date_version_analysis)

        # 5. Final answer contains document IDs
        self.assertIn("[INC-1042]", resp.answer)
        self.assertIn("[DEP-882]", resp.answer)
        self.assertIn("[PM-211]", resp.answer)

        # 6. Causation is NOT falsely asserted
        ans_lower = resp.answer.lower()
        self.assertTrue(
            "not explicitly prove" in ans_lower
            or "do not prove" in ans_lower
            or "correlation only" in ans_lower
            or "correlation" in ans_lower,
            "Causation must not be asserted from temporal correlation alone"
        )

        # 7. Similar vs identical distinguishes PM-211
        if resp.similar_vs_identical:
            self.assertFalse(resp.similar_vs_identical.is_identical)
            self.assertIn("PM-211", resp.similar_vs_identical.explanation)

    def test_scenario_b_contradictory_guidance(self):
        """Test B: The service is failing after a deployment. What should the on-call engineer do first?"""
        question = "The service is failing after a deployment. What should the on-call engineer do first?"
        req = InvestigationRequest(question=question)
        resp = self.agent.investigate(req)

        doc_ids = [e.document_id for e in resp.evidence]
        self.assertIn("GUIDE-12", doc_ids, "GUIDE-12 must be retrieved")
        self.assertIn("GUIDE-41", doc_ids, "GUIDE-41 must be retrieved")

        # Contradiction detected
        self.assertTrue(len(resp.contradictions) > 0, "Contradiction must be detected")
        contra = resp.contradictions[0]
        self.assertTrue(contra.detected)
        self.assertEqual(contra.newer_doc_id, "GUIDE-41", "GUIDE-41 must be recognized as newer")

        # Older document is not hidden
        self.assertIn("[GUIDE-12]", resp.answer)
        self.assertIn("[GUIDE-41]", resp.answer)

        # Guidance checks dependency health
        self.assertIn("dependency", resp.answer.lower())

    def test_scenario_c_insufficient_evidence(self):
        """Test C: Did this exact failure happen before?"""
        question = "Did this exact failure happen before?"
        req = InvestigationRequest(question=question)
        resp = self.agent.investigate(req)

        doc_ids = [e.document_id for e in resp.evidence]
        # At least INC-300 or INC-301 retrieved
        self.assertTrue("INC-300" in doc_ids or "INC-301" in doc_ids, "INC-300 or INC-301 must be retrieved")

        # Identical incident must NOT be falsely claimed
        if resp.similar_vs_identical:
            self.assertFalse(resp.similar_vs_identical.is_identical, "Identical incident must not be falsely claimed")

        # Evidence status must become Insufficient
        self.assertEqual(resp.evidence_status, "Insufficient")

        # Must explicitly assert insufficient evidence statement
        expected_statement = "Insufficient evidence to determine this from the available documents."
        self.assertIn(expected_statement, resp.answer)
        self.assertIn(expected_statement, resp.uncertainty)

if __name__ == "__main__":
    unittest.main()
