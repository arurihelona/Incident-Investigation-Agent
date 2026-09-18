# Incident Investigation Agent
*Evidence-Driven Operational Incident Analysis*

A clean, reliable hackathon prototype demonstrating an autonomous, multi-hop investigation agent for software engineering incidents. Rather than simply summarizing the top retrieved documents or hallucinating causal assumptions, the agent:
1. Plans an investigation path and derives targeted queries.
2. Extracts discovered operational facts (services, software versions, incident dates).
3. Performs targeted follow-up searches across deployment notes and postmortems based on discoveries.
4. Compares dates and software versions to avoid conflating past incidents with current ones.
5. Detects contradictory and outdated operational guidance without hiding older context.
6. Strictly evaluates similar vs. identical incidents to avoid false equivalencies.
7. Explicitly reports when evidence is insufficient: `"Insufficient evidence to determine this from the available documents."`
> **Live Demo URL:** [https://instrument-alternatively-actors-intl.trycloudflare.com](https://instrument-alternatively-actors-intl.trycloudflare.com)
> *(Active public link powered by Cloudflare Edge — opens directly with zero password or signup)*

---

## 1. Core Problem

When major outages occur, engineers must manually search through hundreds of internal documents across disparate systems: incident reports, deployment logs, postmortems, and troubleshooting runbooks.

A single incident question often requires connecting information across multiple sources:
- **Deployment Correlation:** Determining if a recent release is temporally and version-correlated without jumping to unproven causal conclusions.
- **Contradictory Guidance:** Reconciling outdated runbooks with newer emergency procedures.
- **Similar vs. Identical:** Distinguishing incidents that share similar symptoms (e.g., latency) but stem from completely different services or failure mechanisms (e.g., DB schema migrations vs. expired TLS certificates).
- **Evidence Gaps:** Knowing when available documents simply do not contain sufficient evidence to answer a question.

---

## 2. Solution: Autonomous Multi-Hop Agent

The **Incident Investigation Agent** solves this through an explicit, auditable agentic workflow:

```text
                  User
                   │
                   ▼
            React Frontend
                   │
                   ▼
             FastAPI Backend
                   │
                   ▼
        Investigation Agent
             │          │
             │          ▼
             │    Evidence Review
             │       Agent
             │
             ▼
       Retrieval Service
             │
       ┌─────┴─────┐
       ▼           ▼
 Vector Search   Metadata
       │           │
       └─────┬─────┘
             ▼
        Document Store
```

### Why an Agentic Approach?
A standard semantic search or simple RAG pipeline retrieves the top-$K$ most similar documents and asks an LLM to summarize them. This fails in real operational troubleshooting because:
- The initial question may not mention deployment IDs or previous postmortem document keys.
- Search queries must be formulated dynamically from entities discovered in earlier hops.
- Date and version relationships require logical temporal reasoning, not just keyword matching.
- An evidence review agent must audit findings to prevent unsubstantiated causal claims and explicitly state when evidence is insufficient.

---

## 3. Architecture & Key Modules

```text
incident-investigation-agent/
│
├── frontend/                     # React + Vite SRE Dashboard
│   ├── src/
│   │   ├── components/           # UI cards, timeline, contradiction panels
│   │   ├── services/api.js       # API client with proxy
│   │   ├── App.jsx               # Main dashboard
│   │   └── index.css             # Dark/light devtools styling
│   ├── package.json
│   └── vite.config.js
│
├── backend/
│   ├── main.py                   # FastAPI REST API & lifecycle
│   ├── config.py                 # Configuration & environment variables
│   ├── models/schemas.py         # Pydantic schemas for domain entities
│   ├── retrieval/
│   │   ├── vector_store.py       # ChromaDB persistent collection & embeddings
│   │   ├── search.py             # Semantic search service
│   │   └── metadata_filter.py    # Service, type, version, date filters
│   ├── agents/
│   │   ├── llm_client.py         # Provider-agnostic client (OpenAI/Gemini/Offline)
│   │   ├── investigation_agent.py# Multi-hop orchestration & state machine
│   │   └── evidence_review_agent.py # Date/version, contradiction, identical check
│   ├── services/
│   │   ├── document_service.py   # Ingestion, reindexing & catalog
│   │   └── investigation_service.py # Request execution & error boundary
│   ├── data/documents.json       # Canonical incident, deployment & guide corpus
│   ├── tests/test_scenarios.py   # Automated tests for Scenarios A, B, and C
│   └── requirements.txt
│
├── README.md
└── .env.example
```

---

## 4. Tech Stack

- **Frontend:** React 18, Vite 5, Lucide React, Modern CSS (Devtools theme).
- **Backend:** Python 3.10+, FastAPI, Uvicorn, Pydantic v2.
- **Vector Database:** ChromaDB 1.5.9 (`all-MiniLM-L6-v2` ONNX embeddings running 100% locally).
- **LLM Layer:** Pluggable adapter supporting OpenAI, Gemini, local models, or the built-in deterministic heuristic reasoning engine for 100% offline, zero-dependency hackathon evaluation.

---

## 5. Setup & Running Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Run the FastAPI backend
python main.py
```
*The backend starts at `http://localhost:8000`. On boot, it automatically creates the ChromaDB vector store and indexes all documents.*

### 2. Frontend Setup (Development Mode)

```bash
# Navigate to frontend directory
cd ../frontend

# Install dependencies
npm install

# Start Vite dev server
npm run dev
```
*The frontend dev server opens at `http://localhost:5173`.*

### 3. Unified Production Deployment (Single Process)

You can build the React frontend and run both the UI and API from the single FastAPI process on port 8000:

```bash
# Build frontend
cd frontend
npm run build

# Start FastAPI backend (automatically serves frontend/dist at /)
cd ../backend
python main.py
```
*Open `http://localhost:8000` directly in your browser!*

### 4. Docker Deployment

Deploy with a single command via Docker Compose:

```bash
docker compose up --build
```
*Or build the container manually:*
```bash
docker build -t incident-investigation-agent .
docker run -p 8000:8000 incident-investigation-agent
```

### 5. Deploy to Cloud (Render / Railway / Fly.io)

- **Render:** Connect the repo as a "Web Service", select Docker runtime, set port to `8000`.
- **Railway:** Deploy directly from Dockerfile. Railway automatically detects port 8000.
- **Fly.io:** Run `fly launch` in the project root; it will deploy using the included multi-stage Dockerfile.

---

## 6. Environment Variables

Create a `.env` file in the root or `backend/` directory (see `.env.example`):

```bash
# LLM Provider: "auto", "openai", "gemini", "anthropic", "local", "heuristic"
# If no key is set, system runs cleanly offline using the built-in deterministic engine!
LLM_PROVIDER=auto

# Optional API keys
LLM_API_KEY=
OPENAI_API_KEY=
GEMINI_API_KEY=

# Model configuration
LLM_MODEL=gpt-4o-mini
LLM_BASE_URL=

# Server & DB Settings
HOST=0.0.0.0
PORT=8000
CHROMA_PERSIST_DIR=./chroma_db
DATA_PATH=./data/documents.json
```

---

## 7. Demo Scenarios & Test Suite

The prototype natively implements and demonstrates all three hackathon test scenarios:

### Demo 1 — Deployment Investigation (Test A)
- **Question:**
  `Why did the Order API become slow on September 16? Check whether the deployment was related and whether we have seen this before.`
- **Agent Workflow:**
  1. *Initial Search:* Discovers `INC-1042` (orders-api latency spike, v2.8.1, 2026-09-16).
  2. *Fact Extraction:* Extracts `service = orders-api`, `version = v2.8.1`, `date = 2026-09-16`.
  3. *Follow-Up Search 1:* Queries deployment notes for `orders-api` `v2.8.1` ➔ Discovers `DEP-882` (deployed 2026-09-15 at 18:10 UTC).
  4. *Follow-Up Search 2:* Queries past latency incidents/postmortems for `orders-api` ➔ Discovers `PM-211` (previous latency incident on v2.6.0).
  5. *Review & Cautious Causation:* Establishes close temporal and version correlation between `DEP-882` and `INC-1042`, but explicitly avoids claiming causation because telemetry does not prove causality. Evaluates `PM-211` as non-identical because it involved database saturation on v2.6.0 during schema migration.

### Demo 2 — Contradictory Guidance (Test B)
- **Question:**
  `The service is failing after a deployment. What should the on-call engineer do first?`
- **Agent Workflow:**
  1. *Retrieval:* Discovers `GUIDE-12` and `GUIDE-41`.
  2. *Contradiction Detection:* Identifies direct conflict: `GUIDE-12` recommends restarting Service A immediately, whereas `GUIDE-41` commands NOT to restart during dependency failures.
  3. *Date & Version Reasoning:* Compares dates (`2024-02-01` vs `2026-08-10`) and versions (`v1` vs `v3`). Recognizes `GUIDE-41` as the newer, superseding runbook.
  4. *Preserves Older Context:* Does not hide `GUIDE-12`, but instructs the engineer to check dependency health first according to `GUIDE-41`.

### Demo 3 — Insufficient Evidence (Test C)
- **Question:**
  `Did this exact failure happen before?`
- **Agent Workflow:**
  1. *Retrieval:* Retrieves available incident reports `INC-300` and `INC-301`.
  2. *Similar vs. Identical Evaluation:* Compares services (`catalog-api` vs `orders-api`) and failure mechanisms (`database saturation` vs `expired certificate`).
  3. *Evidence Status:* Sets `Evidence Status: Insufficient`.
  4. *Explicit Statement:* Returns:
     `"Insufficient evidence to determine this from the available documents."`

---

## 8. Running Automated Tests

Run the automated test suite directly from the command line:

```bash
cd backend
python -m unittest tests/test_scenarios.py -v
```

All 3 scenarios are verified:
```text
test_scenario_a_deployment_investigation ... ok
test_scenario_b_contradictory_guidance ... ok
test_scenario_c_insufficient_evidence ... ok

----------------------------------------------------------------------
Ran 3 tests in 2.014s

OK
```

---

## 9. Limitations & Future Scope

### Current Prototype Limitations
- Documents are sourced from local JSON corpus rather than live Jira, Confluence, or Datadog integrations.
- Focuses strictly on investigation and traceability; does not trigger automated remediation scripts.

### Future Scope
1. **Live Enterprise Ingestion Connectors:** Ingesting markdown runbooks, GitHub PRs, and PagerDuty postmortems via webhooks.
2. **Telemetry Cross-Validation:** Correlating document text with Prometheus metrics, OpenTelemetry traces, and error rate time series.
3. **Interactive Investigation Graph:** Visual interactive node graph allowing engineers to expand evidence hops interactively.
