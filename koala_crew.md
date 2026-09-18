# Incident Investigation Agent

## 1. Team Details

**Team Name / ID:** Koala Crew

**Team Lead:** Sahithi Ambathi

**Team Members:**

- Sahithi Ambathi
- Helona Aruri
- Tejasree Chittapuram

**Repo Link (Optional):** https://github.com/arurihelona/Incident-Investigation-Agent

**Demo Link (Optional):** https://swift-kings-hammer.loca.lt (Password/IP: `124.123.134.227`)

---

## 2. Problem Statement

The Investigation Nobody Could Answer

Context
Your company has operated a large distributed platform for several years. Over time, thousands of internal documents have accumulated:
● incident reports
● deployment notes
● architecture documents
● troubleshooting guides
● customer complaints
● engineering discussions
● post-incident reviews

One morning an engineer reports: "The Order API became extremely slow after yesterday's deployment. Has this happened before?" The answer isn't necessarily contained in one document. There may be:
● several incidents with similar symptoms
● different terminology describing the same problem
● old recommendations that are no longer valid
● contradictory documents
● newer documents that supersede older ones
● incomplete evidence

The Challenge
Build an Incident Investigation Agent that investigates operational incidents across a collection of internal documents. A question should be answerable only after the agent connects evidence from multiple sources such as incident reports, deployments, architecture notes, troubleshooting guides, customer complaints, and postmortems.

Core Requirements
● Accept a natural-language investigation question.
● Search across multiple document types using semantic and metadata-aware retrieval.
● Use information discovered during investigation to perform additional searches.
● Distinguish document dates, software versions, and outdated guidance.
● Detect contradictions and avoid treating similar incidents as identical.
● Return an evidence-backed answer with document identifiers and a clear statement when evidence is insufficient.

Inputs Students Can Test
Test Input A — Deployment-related incident
User prompt:
"Why did the Order API become slow on September 16? Check whether the deployment was related and whether we have seen this before."
documents.json:
[
  {
    "document_id": "INC-1042",
    "type": "incident_report",
    "service": "orders-api",
    "date": "2026-09-16",
    "version": "v2.8.1",
    "title": "Order API latency spike",
    "content": "P95 latency increased significantly. The incident began shortly after the latest deployment."
  },
  {
    "document_id": "DEP-882",
    "type": "deployment_note",
    "service": "orders-api",
    "date": "2026-09-15",
    "version": "v2.8.1",
    "title": "Orders deployment",
    "content": "Version v2.8.1 was deployed to production at 18:10 UTC."
  },
  {
    "document_id": "PM-211",
    "type": "postmortem",
    "service": "orders-api",
    "date": "2026-05-03",
    "version": "v2.6.0",
    "title": "Previous latency incident",
    "content": "A previous latency incident was caused by database connection saturation during a schema migration."
  }
]
Test Input B — Contradictory guidance
User prompt:
"The service is failing after a deployment. What should the on-call engineer do first?"
documents.json:
[
  {
    "document_id": "GUIDE-12",
    "type": "troubleshooting",
    "date": "2024-02-01",
    "version": "v1",
    "title": "Service restart procedure",
    "content": "Restart Service A when latency remains high."
  },
  {
    "document_id": "GUIDE-41",
    "type": "troubleshooting",
    "date": "2026-08-10",
    "version": "v3",
    "title": "Service A incident procedure",
    "content": "Do not restart Service A during dependency failures. Check dependency health first."
  }
]
Test Input C — Insufficient evidence
User prompt:
"Did this exact failure happen before?"
documents.json:
[
  {
    "document_id": "INC-300",
    "type": "incident_report",
    "service": "catalog-api",
    "date": "2026-07-11",
    "version": "v5",
    "title": "Catalog latency",
    "content": "Latency increased due to database saturation."
  },
  {
    "document_id": "INC-301",
    "type": "incident_report",
    "service": "orders-api",
    "date": "2026-07-12",
    "version": "v4",
    "title": "Order errors",
    "content": "Requests failed because of an expired certificate."
  }
]

---

## 3. TL;DR

**Problem:** Engineers must manually connect evidence across many incident documents.

**Solution:** An agent investigates documents, follows evidence, checks versions, and gives a cited answer.

**Who benefits:** On-call engineers get faster, traceable incident investigations with evidence and uncertainty.

---

## 4. Scope of the Project

**What are you building?**

An Incident Investigation Agent that accepts operational questions, searches multiple document types, connects related evidence, checks dates and software versions, detects contradictions, and returns an evidence-backed answer with document identifiers.

**How does it solve the problem statement?**

The agent searches relevant documents, uses discovered facts to refine later searches, compares dates and versions, identifies conflicting or outdated guidance, and reports when available evidence is insufficient.

**Key features you're building for this hackathon:**

- Semantic and metadata-aware retrieval across document types
- Follow-up searches driven by evidence discovered during investigation
- Date and software-version aware evidence comparison
- Contradiction and outdated-guidance detection
- Evidence-backed answers with document identifiers

**What are you deliberately NOT doing? (Optional)**

No live production monitoring or automatic remediation; the focus is document-based incident investigation.

---

## 5. Why an Agentic Approach?

**What does your agent decide or do on its own?**

The agent plans the investigation, chooses follow-up searches from discovered evidence, compares relevant documents by date and version, checks for contradictions, and decides whether evidence is sufficient to answer or whether uncertainty must be reported.

**Why wouldn't a fixed script, if-else rules, or a simple chatbot be enough?**

Incident questions vary and may require different search paths. A fixed workflow cannot reliably decide what evidence to investigate next, connect changing terminology, compare old and new guidance, or determine when evidence is insufficient.

---

## 6. Who It's For & What Changes

**Who or what is this for?**

On-call engineers, SREs, developers, and incident response teams investigating operational failures.

**The world today, without your solution:**

Engineers manually search incident reports, deployments, guides, postmortems and other documents. They must connect terminology, dates and versions themselves, while handling conflicting or outdated information.

**The world with your solution, fully built and scaled to production:**

An engineer asks one investigation question and receives a structured answer connecting relevant evidence across internal documents, with document identifiers, version/date context, contradictions, and an explicit uncertainty statement when evidence is insufficient.

**What your hackathon build actually delivers today:**

Prototype scope: a document-based investigation workflow demonstrating multi-source retrieval, evidence-driven follow-up searches, date/version comparison, contradiction handling, and evidence-backed responses. Final implemented features and integrations should be updated here before submission.

**Before vs. After**

| What Changes | Today | With Our Current Build | At Production Scale |
|--------------|-------|------------------------|---------------------|
| Investigation effort | Manual document search | Guided multi-step search | Automated investigation |
| Evidence linking | Engineer connects sources | Agent connects evidence | Cross-system evidence graph |
| Conflicting guidance | Manually compared | Contradictions flagged | Version-aware resolution |

---

## 7. Architecture & Agents

**How is your system put together?**

An engineer submits a natural-language incident question. The Investigation Agent searches the document collection using semantic and metadata-aware retrieval, extracts useful evidence, performs additional searches based on discoveries, compares dates and versions, checks contradictions, and returns a traceable answer or an insufficient-evidence statement.

### 7.1 Agents

- **Investigation Agent:** Plans and performs the investigation, selects follow-up searches, compares evidence, and generates the final answer. Model: Pluggable (OpenAI / Gemini / Offline Grounded Engine). Talks to the document retrieval and metadata services.
- **Evidence Review Agent:** Reviews retrieved sources for contradictions, outdated guidance, date/version differentials, similar vs identical incidents, and whether the evidence supports the conclusion. Talks to the Investigation Agent and document store.

### 7.2 Services, APIs, Databases & Memory

- **Document Store:** Holds incident reports, deployments, guides, architecture notes and postmortems used for investigation.
- **Retrieval Service:** Performs semantic and metadata-aware searches over the document collection.

**How does your system remember things (memory & state)?**

The investigation state keeps the original question, retrieved documents, extracted facts, previous searches, and evidence links so later searches can build on earlier findings.

**Diagram Link (Optional):** N/A

### 7.3 Example Walkthrough

**Example input:** Why did the Order API become slow on September 16? Check whether the deployment was related and whether we have seen this before.

1. **Investigation Agent** searches for Order API latency incidents around September 16.
2. **Retrieval Service** finds INC-1042 and extracts its date, version, and latency evidence.
3. **Investigation Agent** uses the discovered version and date to search for the related deployment.
4. **Retrieval Service** finds DEP-882 showing v2.8.1 was deployed on September 15.
5. **Investigation Agent** searches earlier Order API latency incidents using the discovered service and symptom.
6. **Evidence Review Agent** compares PM-211 with the current incident and distinguishes the previous cause from the current evidence.

**Final output:** The answer links INC-1042, DEP-882 and PM-211, explains what the evidence supports, and avoids claiming causation without proof.

**Anything special about how your workflow runs? (Optional)**

The workflow is iterative: retrieve evidence → extract useful facts → create a more specific search → compare sources → check dates and versions → answer when supported or report insufficient evidence.

---

## 8. Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend / Interface | React 18, Vite 5, Lucide React, Modern DevTools CSS |
| Backend | Python 3.10+, FastAPI, Uvicorn, Pydantic v2 |
| Agent Framework | Custom Multi-Hop Investigation & Evidence Review Agents |
| Database / Storage | ChromaDB 1.5.9 (Local all-MiniLM-L6-v2 ONNX embeddings) + JSON Corpus |
| Hosting | Localhost / Docker-ready |
| Other | Semantic retrieval / metadata filtering / automated test suite |

---

## 9. What to Expect From Our Current Build

**Working:**

- Complete multi-hop investigation agent loop (Initial Search ➔ Fact Extraction ➔ Targeted Follow-up ➔ Corroboration ➔ Review ➔ Cited Synthesis).
- All 3 canonical test scenarios verified (Deployment Investigation, Contradictory Guidance, Insufficient Evidence).
- ChromaDB semantic vector search and metadata filtering.
- Date and software-version comparison with cautious causation enforcement.
- Contradiction detection between older and superseding runbooks with condition checks.
- Similar vs. identical incident evaluation with explicit insufficient-evidence reporting.
- React + Vite operational SRE dashboard with live step timeline, evidence relationship flow, and document catalog.

**Partly working, mocked, or hard-coded:**

- Built-in deterministic engine guarantees 100% reliable offline demo evaluation if external LLM API key is not supplied.

**Not working or not built yet:**

- Production-scale enterprise document ingestion from live ticketing/monitoring systems (PagerDuty, Jira, Datadog).

**What we'd most like to be judged on:**

The agentic investigation loop: connecting evidence across documents, using discoveries to guide further searches, distinguishing similar from identical incidents, and reporting insufficient evidence.

---

## 10. Future Scope

### Idea 1

**Name:** Enterprise Document Ingestion

**What it is:** Automatically ingest incident reports, deployment records, architecture documents, troubleshooting guides and postmortems from internal systems.

**Why it matters:** Keeps the investigation knowledge base current without manual uploads.

**How we'd build it:** Add connectors, scheduled ingestion, metadata extraction, document chunking, embeddings and version tracking.

**Done when:** A new internal document can be ingested and retrieved automatically with its metadata.

### Idea 2

**Name:** Production Incident Integration

**What it is:** Connect the agent to monitoring, deployment and incident-management systems to combine documents with live operational context.

**Why it matters:** Gives investigators current system context alongside historical evidence.

**How we'd build it:** Add authenticated connectors for approved monitoring, deployment and incident APIs.

**Done when:** A test incident can retrieve relevant operational data and link it to supporting documents.

### Idea 3 (Optional)

**Name:** Investigation History

**What it is:** Store completed investigations, evidence and conclusions for later reference.

**Why it matters:** Engineers can revisit previous investigations instead of repeating the same research.

**How we'd build it:** Store investigation sessions, evidence links and final answers with timestamps and searchable metadata.

**Done when:** An engineer can search and reopen a previous investigation with its evidence trail.

---

## 11. Additional Notes (Optional)

This project is designed around evidence rather than unsupported guesses. Similar symptoms are not automatically treated as the same incident, newer guidance is considered alongside older documents, and the system explicitly reports insufficient evidence when the available documents do not support a conclusion.
