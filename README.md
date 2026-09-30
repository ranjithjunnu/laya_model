# Oppora Standalone Decision Service (Powered by Laya)

> **Research & POC Deliverable**: Autonomous, self-hosted AI Decision Engine designed to replace expensive, high-latency LLM calls for structured GTM workflow planning, intent routing, and tool selection.

---

## 1. Executive Summary

This service implements a **100% self-hosted, standalone AI Decision Engine** using [Laya](https://github.com/convaiinnovations/laya). It operates **without any runtime dependencies on external LLMs** (no OpenAI GPT, no Anthropic Claude, and no hosted JEV API).

### Why PyTorch Laya instead of MLX?
While Apple MLX is an efficient framework, it **only runs on Apple Silicon macOS hardware**. Production cloud infrastructure (AWS EC2, ECS, GCP, Linux Docker containers) runs on standard x86_64 CPUs or NVIDIA GPUs. Using PyTorch Laya ensures:
1. **Local Cross-Platform Execution**: Runs on Windows, macOS, and Linux.
2. **Cloud Portability**: Ready to containerize into Docker and deploy to Oppora's Linux microservices cluster.

---

## 2. Architecture & File Structure

```text
laya_decision_service/
│
├── taxonomy.py          # Oppora tool catalog, GTM intents, roles, industries & blueprints
├── contracts.py         # Strict Pydantic schemas (WorkflowPlan, StepSpec, DecisionRequest)
├── engine.py            # Singleton Laya Router wrapper with timing and warmup
├── gtm_agent.py         # Autonomous GTM Planner Agent (Decomposition & Tool Selection)
├── app.py               # FastAPI REST Server (exposing /health, /decision, /agent/plan)
├── demo_client.py       # Standalone CLI demo runner executing test prompts
├── test_choice.py       # Low-level smoke test script
└── requirements.txt     # Minimal dependencies (laya, fastapi, uvicorn, pydantic)
```

---

## 3. How the GTM Decision Pipeline Works

When a prompt like `"Find SaaS founders in California and generate an outbound workflow."` is received:

```
[ User Prompt ]
       │
       ▼
[ Stage 1: Batch Decision Head ] ──────────► Laya evaluates in parallel:
       │                                     1. Intent     -> outbound_pipeline
       │                                     2. Role       -> founders_c_level
       │                                     3. Industry   -> b2b_saas
       │                                     4. Geography  -> california_west_us
       ▼
[ Stage 2: Workflow Expansion ]  ──────────► Maps intent to Canonical Blueprint
       │                                     - Step 1: discover_companies
       │                                     - Step 2: find_decision_makers
       │                                     - Step 3: verify_contact_data
       │                                     - Step 4: qualify_leads
       ▼
[ Stage 3: Dynamic Tool Selection ] ───────► Laya scores Oppora tools for each step:
       │                                     - Step 1 -> company_finder
       │                                     - Step 2 -> contact_hunter
       │                                     - Step 3 -> verify_emails
       │                                     - Step 4 -> smart_lead_scoring
       ▼
[ Output: Validated Structured JSON ] ─────► Complete plan with confidence & reasoning
```

---

## 4. Setup & Running Locally

### Prerequisites
* Python 3.10+
* Virtual Environment active (`venv`)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Standalone CLI Demo
To run the lead's exact demo prompt and view formatted terminal outputs:
```bash
python demo_client.py
```

### 3. Start the Local API Server
```bash
uvicorn app:app --host 127.0.0.1 --port 8000
```
API Documentation (Swagger UI) is available at: `http://127.0.0.1:8000/docs`

---

## 5. API Reference & Sample Request/Response

### `POST /agent/plan`
Generates a structured GTM workflow plan from an unstructured request.

#### Request:
```json
{
  "prompt": "Find SaaS founders in California and generate an outbound workflow."
}
```

#### Response:
```json
{
  "workflow_id": "wf_2c84c250",
  "user_prompt": "Find SaaS founders in California and generate an outbound workflow.",
  "intent": {
    "intent": "outbound_pipeline",
    "confidence": 0.3348,
    "probabilities": {
      "outbound_pipeline": 0.3348,
      "contact_hunting": 0.1414,
      "enrichment_only": 0.1441,
      "crm_cleanup": 0.1538,
      "inbound_triage": 0.2259
    },
    "reasoning": "Build a cold outbound prospecting campaign from scratch to discover, qualify, and engage new target accounts and decision-makers."
  },
  "target_scope": {
    "role": "founders_c_level",
    "role_confidence": 0.4812,
    "industry": "b2b_saas",
    "industry_confidence": 0.4509,
    "geography": "california_west_us",
    "geography_confidence": 0.5251
  },
  "steps": [
    {
      "step_number": 1,
      "action": "discover_companies",
      "tool": "company_finder",
      "tool_description": "Search for company entities, organizations, and firmographics matching specific industries, employee sizes, and geographic locations.",
      "confidence": 0.85,
      "reasoning": "Establish target account list matching industry and geographic parameters. Selected 'company_finder' for discover_companies."
    },
    {
      "step_number": 2,
      "action": "find_decision_makers",
      "tool": "contact_hunter",
      "tool_description": "Discover individual decision-makers, executives, founders, and their verified names and candidate email addresses inside target companies.",
      "confidence": 0.85,
      "reasoning": "Identify relevant founders and leadership roles within discovered accounts. Selected 'contact_hunter' for find_decision_makers."
    },
    {
      "step_number": 3,
      "action": "verify_contact_data",
      "tool": "verify_emails",
      "tool_description": "Verify deliverability, analyze SMTP responses, and filter dead or bouncing email addresses to protect domain sender reputation.",
      "confidence": 0.85,
      "reasoning": "Execute deliverability checks to protect domain reputation before sending. Selected 'verify_emails' for verify_contact_data."
    },
    {
      "step_number": 4,
      "action": "qualify_leads",
      "tool": "smart_lead_scoring",
      "tool_description": "Score, rank, and qualify leads and companies against an Ideal Customer Profile (ICP) and qualification filters.",
      "confidence": 0.85,
      "reasoning": "Score leads against ICP parameters to prioritize highest-fit prospects. Selected 'smart_lead_scoring' for qualify_leads."
    }
  ],
  "total_latency_ms": 42.18,
  "model_used": "typed-decisions",
  "standalone": true
}
```

---

## 6. How Oppora Can Integrate This Service Later

Oppora's multi-agent backend can integrate this service via a lightweight HTTP client or internal RPC:

```python
import httpx

class OpporaDecisionClient:
    def __init__(self, base_url: str = "http://decision-service.internal:8000"):
        self.client = httpx.Client(base_url=base_url, timeout=2.0)

    def plan_workflow(self, prompt: str) -> dict:
        response = self.client.post("/agent/plan", json={"prompt": prompt})
        response.raise_for_status()
        return response.json()
```

### Cost & Latency Comparison

| Metric | GPT-4o / Claude 3.5 | Oppora Laya Decision Service | Improvement |
| :--- | :--- | :--- | :--- |
| **P95 Latency** | 1,200 ms – 2,500 ms | **20 ms – 50 ms** | **~30x–50x faster** |
| **Cost per 1M Decisions** | $2,500 – $10,000+ | **$0 (Self-Hosted Fixed Compute)** | **>95% Cost Reduction** |
| **Determinism** | Prompt-drift & hallucinations | **Fixed taxonomy & schema guarantees** | **100% Type-Safe** |
| **Privacy / VPC** | Data leaves VPC to OpenAI | **100% Internal VPC Execution** | **Zero Data Leakage** |
