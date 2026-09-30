# Standalone Laya decision-service demo

For a visual walkthrough, file responsibilities and examples to explain to your lead, see [ARCHITECTURE.md](ARCHITECTURE.md).

This project demonstrates local classification and GTM workflow planning. It
returns structured JSON; it does not execute Oppora tools, generate emails,
send messages, or modify CRM records.

The current implementation uses **PyTorch Laya**, not MLX. The lead's MLX-specific
deliverable therefore remains a separate framework requirement to resolve.
No hosted GPT, Claude or Jev API is called by this demo. Model weights must be
available locally; the first setup may download them through Laya.

## Setup and restart

From PowerShell:

```powershell
cd E:\laya_decision_service
python -m venv venv  # Only if the project environment does not already exist.
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe -m uvicorn app:app --host 127.0.0.1 --port 8000
```

Open <http://127.0.0.1:8000/docs>. Use POST `/agent/plan` -> Try it out.
After a code change, stop the existing server with Ctrl+C and run the command
again. The normal launch command does not automatically reload changed files.
After this update the Swagger title should show version `1.1.0`.

Run the separate CLI demo or regression checks:

```powershell
.\venv\Scripts\python.exe demo_client.py
.\venv\Scripts\python.exe -m unittest test_regressions -v
```

The regression checks use deliberately incorrect model predictions to verify
the corrections independently of model accuracy. They do not run inference.
The CLI demo uses the real local model and prints the complete responses.

## How it works

```text
User prompt
  -> Laya choice predictions: intent, role, industry, geography
  -> Simple explicit-request rules preserve recognised user constraints
  -> Intent maps to a supported workflow blueprint
  -> Blueprint actions map to configured demo tools
  -> Pydantic validates the structured response
```

Laya scores finite choices. It does not generate the workflow JSON or reasoning
text; Python builds those from rules, descriptions and templates. Tool selection
is a fixed mapping, not a separate Laya comparison of all Oppora tools.

Every supported intent has a blueprint, including enrichment and incoming-reply
classification. A missing blueprint returns `unsupported` with no steps; it
never silently becomes an outbound workflow. Company searches do not add people
or outreach. People searches add email verification only when email/verification
is requested. The outbound blueprint represents discovery and qualification;
it does not include email writing or sending.

An absent target is `none_specified`. This is different from an explicitly
requested `global` location. Scope recognition uses a small keyword catalog;
unsupported recognised targets and multiple categories require clarification.
Arbitrary job titles, industries and locations are not comprehensively parsed.
Full natural-language understanding, negation and mixed-operation planning remain
limitations of this small demo.

## Scores, sources and uncertainty

Each decision has a source:

| Source | Meaning of confidence |
| --- | --- |
| `model_probability` | Winning-choice probability from Laya, not verified accuracy. |
| `model_score` | Another model-provided confidence score; not verified accuracy. |
| `explicit_rule` | `null`: a deterministic text rule matched, not a model probability. |
| `fixed_mapping` | `null`: the blueprint specifies the tool, not a learned tool-selection score. |
| `unavailable` | `null`: the model returned no usable score. |

`model_predictions` preserves the original Laya choices and scores before rules.
Use it to evaluate the model separately from the combined planner. Rule fixes
do not prove an improvement in Laya's underlying classification accuracy.

When no explicit intent rule matches, a model probability below 0.5 (or a missing
score) returns `needs_clarification` with no steps. This is a conservative demo
guardrail, not a calibrated production threshold. A high score still does not
guarantee a correct decision. Tune the threshold against labelled Oppora examples.

Clients should check `status == "planned"` before using steps. Confidence fields
are now nullable; display `N/A` for rules/mappings rather than formatting null as
a percentage. The local checkpoint may emit calibration warnings. Do not describe
the exposed probabilities as measured correctness.

## Demo requests and expected behaviour

Submit a request such as:

```json
{"prompt": "Find IT services companies in India"}
```

| Prompt | Expected intent and plan |
| --- | --- |
| Find IT services companies in India | `account_discovery`; IT services, India; company finder only. |
| Find VP of engineering in the USA | `contact_hunting`; engineering leaders, US; no invented industry; contact hunter only. |
| Find SaaS founders in California and generate an outbound workflow. | `outbound_pipeline`; SaaS, founders, California; discover, find contacts, verify, qualify. |
| Enrich existing company records with missing firmographics. | `enrichment_only`; enrich existing records; no invented target scope. |
| Classify incoming sales replies and out-of-office responses. | `inbound_triage`; classify incoming messages only. |
| Find companies | `account_discovery`; all target fields unspecified; company finder only. |

`sample_responses.json` contains real local-model responses captured during
verification of this update. IDs, model scores and latency can change on a later
run. No production accuracy or cost savings have been established.

## API and files

- GET `/health`: readiness after successful model warmup. Failed warmup prevents startup.
- POST `/decision`: raw Laya choice decisions without planner correction rules.
- POST `/agent/plan`: combined planner, sources, raw predictions, status and ordered steps.
- `taxonomy.py`: supported choices, scope keywords, demo tools and all six blueprints.
- `gtm_agent.py`: explicit rules, clarification guardrail and plan construction.
- `engine.py`: local Laya Router and score parsing.
- `contracts.py`: Pydantic request/response schemas.
- `app.py`: FastAPI server.
- `demo_client.py`: six standalone demo requests.
- `test_regressions.py`: checks for the observed failures and response semantics.

## Later Oppora integration

The Oppora assessment identified bounded decisions such as Ask Ora routing,
Finder mode/source selection, semantic lead fit, evidence matching and workflow
branches. This prototype's six GTM intents are not Oppora's seven specialist-agent
routes. Integration requires the real tool registry, current conversation/task
state and production examples; changing the model dropdown alone is insufficient.

Oppora could call the service with an internal HTTP client:

```python
import httpx

response = httpx.post(
    "http://decision-service.internal:8000/agent/plan",
    json={"prompt": "Find IT services companies in India"},
    timeout=30.0,
)
response.raise_for_status()
plan = response.json()
if plan["status"] != "planned":
    # Present clarification or use the existing Oppora fallback.
    pass
else:
    # Validate real tool names, constraints and permissions before execution.
    pass
```

`context` is accepted for future integration but is currently unused. Tool names
are demo labels, including the new `company_enrichment` planning label, not an
assertion that a corresponding production API exists. Keep generative LLMs for
writing and research synthesis; code should enforce exact filters and execute
approved tools.

## Performance

The pre-update local API check observed roughly 4.7–6.5 seconds per plan on this
CPU environment. This is a small observation, not a P95 benchmark. The verification
samples record updated per-request latency. Measure on the intended hardware and
representative workloads before claiming speedups or savings. Self-hosting still
has compute and operational costs.
