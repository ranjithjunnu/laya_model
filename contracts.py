"""
contracts.py — Pydantic Schemas for Oppora Decision Service & GTM Agent.

Defines strict type contracts for:
1. Low-level generic decision requests/responses (/decision)
2. Oppora GTM Workflow Planner agent requests/responses (/agent/plan)
3. Health check status (/health)
"""

from typing import Dict, List, Optional, Any, Union, Literal
from pydantic import BaseModel, Field, field_validator

DecisionSource = Literal["model_probability", "model_score", "explicit_rule", "fixed_mapping", "unavailable"]


# ─────────────────────────────────────────────────────────────────────────────
# 1. Low-Level Generic Decision Contracts (/decision)
# ─────────────────────────────────────────────────────────────────────────────

class QuestionSpec(BaseModel):
    """Specification of a single decision question for Laya."""
    type: str = Field(
        default="choice",
        description="Type of decision question. Defaults to 'choice'."
    )
    instructions: str = Field(
        ...,
        description="The question or directive the decision model must evaluate."
    )
    criteria: Union[Dict[str, str], List[str]] = Field(
        ...,
        description="Dictionary of label -> description, or list of labels."
    )


class DecisionRequest(BaseModel):
    """Request payload for the raw /decision endpoint."""
    state: str = Field(
        ...,
        description="The contextual state or prompt for the decision engine."
    )
    questions: Dict[str, QuestionSpec] = Field(
        ...,
        description="Dictionary mapping question IDs to their QuestionSpec."
    )
    model: Optional[str] = Field(
        default="typed-decisions",
        description="Model identifier (e.g. 'typed-decisions' or default router)."
    )


class ChoiceAnswer(BaseModel):
    """Normalized response for a single choice question."""
    choice: str = Field(..., description="Selected winner label.")
    confidence: Optional[float] = Field(default=None, ge=0, le=1, description="Model score, not verified accuracy. Null for explicit rules or unavailable scores.")
    source: DecisionSource = Field(default="model_probability", description="Origin of the decision and its score.")
    probabilities: Dict[str, float] = Field(
        default_factory=dict,
        description="Probability distribution across all candidate options."
    )


class DecisionResponse(BaseModel):
    """Response payload returned by /decision."""
    model: str = Field(..., description="The model that executed the decision.")
    answers: Dict[str, ChoiceAnswer] = Field(
        ...,
        description="Decision answers keyed by question ID."
    )
    latency_ms: float = Field(..., description="Inference latency in milliseconds.")


# ─────────────────────────────────────────────────────────────────────────────
# 2. Oppora GTM Planner Agent Contracts (/agent/plan)
# ─────────────────────────────────────────────────────────────────────────────

class GTMPlanRequest(BaseModel):
    """User request sent to the Oppora GTM Agent."""
    prompt: str = Field(
        ...,
        min_length=1,
        example="Find SaaS founders in California and generate an outbound workflow.",
        description="User's high-level GTM, prospecting, or outbound objective."
    )
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional metadata such as user_id, tier, or CRM settings."
    )

    @field_validator("prompt")
    @classmethod
    def nonempty_prompt(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Prompt must contain a request, not only whitespace.")
        return value


class IntentDecision(BaseModel):
    """Decomposed intent category for the GTM request."""
    intent: str = Field(..., description="Selected GTM intent category.")
    confidence: Optional[float] = Field(default=None, ge=0, le=1, description="Model score; null for a deterministic rule. Not calibrated accuracy.")
    source: DecisionSource = Field(default="model_probability")
    probabilities: Dict[str, float] = Field(
        default_factory=dict,
        description="Probability breakdown across intent categories."
    )
    reasoning: str = Field(..., description="Why this intent was selected.")


class TargetScope(BaseModel):
    """Target audience parameters extracted via discrete decisions."""
    role: str = Field(..., description="Target role or seniority level.")
    role_confidence: Optional[float] = Field(default=None, description="Model score; null for an explicit rule.")
    role_source: DecisionSource = Field(default="model_probability")
    role_reasoning: str = Field(default="", description="Why this role category was selected.")
    industry: str = Field(..., description="Target industry vertical.")
    industry_confidence: Optional[float] = Field(default=None, description="Model score; null for an explicit rule.")
    industry_source: DecisionSource = Field(default="model_probability")
    industry_reasoning: str = Field(default="", description="Why this industry category was selected.")
    geography: str = Field(..., description="Target geographical focus.")
    geography_confidence: Optional[float] = Field(default=None, description="Model score; null for an explicit rule.")
    geography_source: DecisionSource = Field(default="model_probability")
    geography_reasoning: str = Field(default="", description="Why this geography category was selected.")


class WorkflowStep(BaseModel):
    """A planned step; this demo does not execute tools."""
    step_number: int = Field(..., description="Execution sequence index (1-indexed).")
    action: str = Field(..., description="Semantic action to perform.")
    tool: str = Field(..., description="Oppora tool selected to execute this action.")
    tool_description: str = Field(..., description="Description of the chosen tool.")
    confidence: Optional[float] = Field(default=None, description="Null for fixed tool mappings; no model score is fabricated.")
    source: DecisionSource = Field(default="fixed_mapping")
    reasoning: str = Field(..., description="Operational reasoning for this step.")


class WorkflowPlan(BaseModel):
    """Complete structured workflow returned by Oppora GTM Planner Agent."""
    workflow_id: str = Field(..., description="Unique generated plan identifier.")
    user_prompt: str = Field(..., description="Original user prompt received.")
    intent: IntentDecision = Field(..., description="Classified intent.")
    target_scope: TargetScope = Field(..., description="Discovered target criteria.")
    steps: List[WorkflowStep] = Field(
        ...,
        description="Ordered sequence of actions and tools."
    )
    status: Literal["planned", "needs_clarification", "unsupported"] = Field(default="planned", description="Only planned responses contain usable workflow steps.")
    clarification: Optional[str] = Field(default=None)
    warnings: List[str] = Field(default_factory=list)
    model_predictions: Dict[str, ChoiceAnswer] = Field(default_factory=dict, description="Original Laya predictions before explicit rules; useful for evaluating the model separately.")
    total_latency_ms: float = Field(
        ...,
        description="End-to-end multi-step planning latency in milliseconds."
    )
    model_used: str = Field(..., description="Laya checkpoint used for raw predictions; rules and templates assemble the plan.")
    standalone: bool = Field(
        default=True,
        description="True indicates 100% self-hosted local decision execution without external LLMs."
    )


# ─────────────────────────────────────────────────────────────────────────────
# 3. Service Health Check Contract (/health)
# ─────────────────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    """Health check status of the decision service."""
    status: str = Field(default="ok", description="Service health status.")
    model: str = Field(..., description="Active Laya decision model.")
    engine_ready: bool = Field(..., description="Whether the model weights are loaded and ready.")
    standalone: bool = Field(default=True, description="Self-hosted mode flag.")
