"""
app.py — FastAPI Service for Laya Decision Engine & Oppora GTM Agent.

Exposes REST API endpoints:
- GET  /health      — Service status, model info, and readiness.
- POST /decision    — Raw low-level Laya decision endpoint.
- POST /agent/plan  — Oppora GTM Workflow Planner endpoint.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from contracts import (
    DecisionRequest,
    DecisionResponse,
    GTMPlanRequest,
    WorkflowPlan,
    HealthResponse,
)
from engine import get_engine
from gtm_agent import get_gtm_agent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("laya_decision_service.app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Pre-load model weights into memory before accepting traffic."""
    logger.info("Lifespan: Pre-loading Laya Decision Engine & Agent...")
    _ = get_engine()
    _ = get_gtm_agent()
    logger.info("Lifespan: System fully initialized and ready to serve.")
    yield
    logger.info("Lifespan: Shutting down.")


app = FastAPI(
    title="Oppora Standalone Decision Service (Laya)",
    description=(
        "Standalone GTM planning demo using Laya, explicit rules and configured tools. "
        "Runs on local PyTorch Laya without external LLM dependencies."
    ),
    version="1.1.0",
    lifespan=lifespan,
)

# Enable CORS for local dashboards or frontend testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["System"],
    summary="Health check and engine readiness"
)
async def health_check() -> HealthResponse:
    """Returns the operational status of the Laya Decision Engine."""
    engine = get_engine()
    return HealthResponse(
        status="ok",
        model=engine.default_model,
        engine_ready=engine.ready,
        standalone=True,
    )


@app.post(
    "/decision",
    response_model=DecisionResponse,
    tags=["Decision Core"],
    summary="Execute low-level multi-choice decision questions"
)
async def make_decision(request: DecisionRequest) -> DecisionResponse:
    """
    Evaluates one or more decision questions against a given context state.
    """
    try:
        engine = get_engine()
        answers, latency_ms = engine.decide(
            state=request.state,
            questions=request.questions,
            model=request.model,
        )
        return DecisionResponse(
            model=request.model or engine.default_model,
            answers=answers,
            latency_ms=latency_ms,
        )
    except Exception as e:
        logger.error(f"Error processing /decision: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Decision execution failed: {str(e)}"
        )


@app.post(
    "/agent/plan",
    response_model=WorkflowPlan,
    tags=["Oppora GTM Agent"],
    summary="Plan a GTM workflow using Laya, explicit rules and configured templates"
)
async def plan_gtm_workflow(request: GTMPlanRequest) -> WorkflowPlan:
    """
    Standalone planning demo that:
    1. Classifies user intent.
    2. Extracts target scope (role, vertical, territory).
    3. Breaks the objective into workflow steps.
    4. Maps actions to configured demo tools (no tool execution).
    5. Returns JSON with decision sources, model scores and reasoning.
    Uncertain or unsupported requests return no steps and a clarification.
    """
    try:
        agent = get_gtm_agent()
        plan = agent.plan_workflow(request)
        return plan
    except Exception as e:
        logger.error(f"Error processing /agent/plan: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent workflow planning failed: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=False)
