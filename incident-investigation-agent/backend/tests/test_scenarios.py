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

    def test_stop_on_no_new_evidence(self):
        """Test: Investigation path cleanly stops when follow-up search finds no new evidence."""
        with self.assertLogs("investigation_agent", level="INFO") as cm:
            question = "Why did the Order API become slow on September 16? Check whether the deployment was related and whether we have seen this before."
            req = InvestigationRequest(question=question)
            resp = self.agent.investigate(req)

        # Verify required log message is emitted
        self.assertTrue(
            any("Stopping investigation: no new evidence found." in msg for msg in cm.output),
            "Log 'Stopping investigation: no new evidence found.' must be recorded."
        )

        # Verify investigation step action is recorded
        step_actions = [s.action for s in resp.investigation_steps]
        self.assertIn("path_stopped_no_new_evidence", step_actions, "Step action 'path_stopped_no_new_evidence' must be recorded.")

        # Verify evidence review and completion
        self.assertEqual(resp.evidence_status, "Sufficient")
        self.assertTrue(
            any("Investigation completed: sufficient evidence." in msg for msg in cm.output),
            "Log 'Investigation completed: sufficient evidence.' must be recorded."
        )

    def test_circular_investigation_prevention(self):
        """Test: Circular multi-hop path (e.g. INC-1042 -> DEP-882 -> INC-1042) is stopped and evidence is deduplicated."""
        with self.assertLogs("investigation_agent", level="INFO") as cm:
            question = "Why did the Order API become slow on September 16? Check whether the deployment was related and whether we have seen this before."
            req = InvestigationRequest(question=question)
            resp = self.agent.investigate(req)

        # Verify circular stop log message is emitted
        self.assertTrue(
            any("Stopping investigation path: document already visited." in msg for msg in cm.output),
            "Log 'Stopping investigation path: document already visited.' must be recorded."
        )

        # Verify step action is recorded
        step_actions = [s.action for s in resp.investigation_steps]
        self.assertIn("path_stopped_already_visited", step_actions, "Step action 'path_stopped_already_visited' must be recorded.")

        # Verify each document appears only once (strictly deduplicated)
        doc_ids = [e.document_id for e in resp.evidence]
        self.assertEqual(len(doc_ids), len(set(doc_ids)), "Each document must appear only once in collected evidence.")

    def test_temporal_validation_future_date(self):
        """Test: Temporal validation rejects answering 2027 question using unrelated 2026 data."""
        question = "Why did the Order API become slow on September 17, 2027?"
        req = InvestigationRequest(question=question)
        resp = self.agent.investigate(req)

        # Status must be Insufficient
        self.assertEqual(resp.evidence_status, "Insufficient")

        # Must explicitly state lack of evidence for requested date
        expected_statement = "I found related Order API information, but I found no evidence for September 17, 2027. I cannot determine the cause from the available documents."
        self.assertIn(expected_statement, resp.answer)

        # Evidence gap must note the missing date
        self.assertTrue(len(resp.evidence_gap) > 0, "Evidence gap must be identified")
        self.assertTrue(any("September 17, 2027" in gap for gap in resp.evidence_gap))

        # Stop reason must indicate completion
        self.assertEqual(resp.stop_reason, "Investigation completed: insufficient evidence.")

    def test_investigation_metrics_and_hop_limits(self):
        """Test: Investigation metrics are populated and max hop limit is enforced."""
        question = "Why did the Order API become slow on September 16? Check whether the deployment was related and whether we have seen this before."
        req = InvestigationRequest(question=question)
        resp = self.agent.investigate(req)

        # Metrics verification
        self.assertIsNotNone(resp.metrics)
        self.assertEqual(resp.metrics.initial_searches, 1)
        self.assertGreaterEqual(resp.metrics.follow_up_searches, 1)
        self.assertGreaterEqual(resp.metrics.total_retrieval_calls, 2)
        self.assertLessEqual(resp.metrics.investigation_hops, resp.metrics.max_hop_limit)
        self.assertEqual(resp.metrics.max_hop_limit, 3)
        self.assertGreaterEqual(resp.metrics.cycles_detected, 1)
        self.assertEqual(resp.metrics.investigation_status, "Completed")
        self.assertIn("Investigation completed", resp.metrics.stop_reason)

    def test_timeline_question_returns_chronological_events(self):
        """Test A: Timeline question returns chronological events."""
        question = "Since when did the deployment start failing?"
        req = InvestigationRequest(question=question)
        resp = self.agent.investigate(req)

        # Timeline detection
        self.assertTrue(resp.is_timeline_query, "Question should be detected as a timeline query")
        self.assertGreaterEqual(len(resp.timeline), 2, "Timeline should extract multiple dated events")

        # Verify step action
        step_actions = [s.action for s in resp.investigation_steps]
        self.assertIn("timeline_constructed", step_actions, "Step action 'timeline_constructed' must be present")

        # Chronological ordering (earliest to latest)
        for i in range(len(resp.timeline) - 1):
            t_curr = resp.timeline[i]
            t_next = resp.timeline[i + 1]
            self.assertLessEqual(t_curr.date, t_next.date, "Timeline events must be in chronological order")

    def test_since_when_distinguishes_deployment_from_failure(self):
        """Test B: 'Since when' distinguishes deployment date from failure date."""
        question = "Since when did the deployment start failing?"
        req = InvestigationRequest(question=question)
        resp = self.agent.investigate(req)

        # Answer must distinguish deployment (2026-09-15) from failure (2026-09-16)
        self.assertIn("2026-09-16", resp.answer, "Must identify first documented failure date as 2026-09-16")
        self.assertIn("2026-09-15", resp.answer, "Must identify deployment date as 2026-09-15")
        self.assertIn("[INC-1042]", resp.answer)
        self.assertIn("[DEP-882]", resp.answer)

        # Must explicitly clarify not to confuse deployment date with failure date
        ans_lower = resp.answer.lower()
        self.assertTrue(
            "not be confused" in ans_lower or "distinguish" in ans_lower or "first documented" in ans_lower,
            "Must explicitly note that deployment date should not be confused with failure start date."
        )

    def test_unknown_start_time_graceful_handling(self):
        """Test C: Unknown start time is handled gracefully."""
        from models.schemas import TimelineEvent
        # Test review agent directly with documents that only have deployment
        only_deployment = [
            TimelineEvent(
                date="2026-09-15",
                time="18:10 UTC",
                event="Orders deployment version v2.8.1 deployed to production",
                document_id="DEP-882",
                service="orders-api",
                version="v2.8.1",
                event_type="deployment_note"
            )
        ]
        analysis = self.agent.review_agent.get_timeline_analysis(only_deployment, "When did the failure start?")
        self.assertIn(
            "Based on the available documents, the exact start time of the failure cannot be determined",
            analysis["narrative"]
        )

        # Empty timeline test
        empty_analysis = self.agent.review_agent.get_timeline_analysis([], "When did it fail?")
        self.assertEqual(
            empty_analysis["narrative"],
            "Based on the available documents, the exact start time of the failure cannot be determined."
        )

    def test_timeline_events_sorted_chronologically(self):
        """Test D: Events are sorted chronologically (earliest first)."""
        docs = [
            {
                "document_id": "INC-1042",
                "content": "Order API latency spike on 2026-09-16. Latency began shortly after the latest deployment.",
                "metadata": {"date": "2026-09-16", "title": "Order API Latency Spike", "service": "orders-api", "version": "v2.8.1", "type": "incident_report"}
            },
            {
                "document_id": "PM-211",
                "content": "Postmortem on 2026-05-03: Latency incident due to database saturation.",
                "metadata": {"date": "2026-05-03", "title": "Database Saturation Postmortem", "service": "orders-api", "version": "v2.6.0", "type": "postmortem"}
            },
            {
                "document_id": "DEP-882",
                "content": "Production deployment on 2026-09-15 at 18:10 UTC for version v2.8.1.",
                "metadata": {"date": "2026-09-15", "title": "Orders API v2.8.1 Deployment", "service": "orders-api", "version": "v2.8.1", "type": "deployment_note"}
            }
        ]
        timeline = self.agent.review_agent.extract_timeline(docs)
        self.assertEqual(len(timeline), 3)
        self.assertEqual(timeline[0].document_id, "PM-211", "Earliest event (2026-05-03) must come first")
        self.assertEqual(timeline[1].document_id, "DEP-882", "Middle event (2026-09-15) must come second")
        self.assertEqual(timeline[2].document_id, "INC-1042", "Latest event (2026-09-16) must come third")
        self.assertEqual(timeline[1].time, "18:10 UTC", "Time must be extracted properly")

if __name__ == "__main__":
    unittest.main()


