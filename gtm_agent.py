"""
gtm_agent.py — Autonomous Oppora GTM Workflow Planner Agent.

This agent runs completely self-hosted on Laya Decision Engine without
invoking any external LLMs (no GPT, no Claude).

Pipeline:
1. Classify GTM Intent (e.g. outbound_pipeline, contact_hunting, crm_cleanup)
2. Extract Target Scope (Role, Industry, Geography)
3. Break into Workflow Steps using Canonical Blueprints
4. Select Optimal Oppora Tool for each step via Laya Decision Engine
5. Compile structured JSON with confidence scores, reasoning, and latency metrics
"""

import time
import uuid
from typing import Optional, Dict, Any

from engine import get_engine
from contracts import (
    GTMPlanRequest,
    WorkflowPlan,
    WorkflowStep,
    IntentDecision,
    TargetScope,
    QuestionSpec,
)
from taxonomy import (
    OPPORA_TOOLS,
    GTM_INTENTS,
    TARGET_ROLES,
    INDUSTRIES,
    GEOGRAPHIES,
    WORKFLOW_BLUEPRINTS,
)


class OpporaGTMAgent:
    """
    Autonomous GTM Planning Agent powered solely by Laya Decision Engine.
    """
    def __init__(self) -> None:
        self.engine = get_engine()

    def plan_workflow(self, request: GTMPlanRequest) -> WorkflowPlan:
        """
        Executes end-to-end GTM workflow planning for a user's prompt.
        """
        start_total = time.perf_counter()
        prompt = request.prompt.strip()

        # ─────────────────────────────────────────────────────────────────────
        # Stage 1: Batch Decision for Intent & Target Scope Decomposition
        # ─────────────────────────────────────────────────────────────────────
        # Running these decisions in a single batch against Laya maximizes throughput.
        batch_questions = {
            "intent": QuestionSpec(
                type="choice",
                instructions="What is the primary GTM objective or outbound workflow required by this request?",
                criteria=GTM_INTENTS
            ),
            "role": QuestionSpec(
                type="choice",
                instructions="Which job role, executive title, or seniority level is being targeted?",
                criteria=TARGET_ROLES
            ),
            "industry": QuestionSpec(
                type="choice",
                instructions="Which target industry, vertical, or market sector is mentioned or implied?",
                criteria=INDUSTRIES
            ),
            "geography": QuestionSpec(
                type="choice",
                instructions="Which target geographic territory, location, or region applies to this request?",
                criteria=GEOGRAPHIES
            ),
        }

        stage1_answers, _ = self.engine.decide(prompt, batch_questions)

        intent_ans = stage1_answers["intent"]
        role_ans = stage1_answers["role"]
        ind_ans = stage1_answers["industry"]
        geo_ans = stage1_answers["geography"]

        # Format Intent Decision
        intent_decision = IntentDecision(
            intent=intent_ans.choice,
            confidence=intent_ans.confidence,
            probabilities=intent_ans.probabilities,
            reasoning=GTM_INTENTS.get(intent_ans.choice, "Matching GTM operational intent.")
        )

        # Format Target Scope
        target_scope = TargetScope(
            role=role_ans.choice,
            role_confidence=role_ans.confidence,
            industry=ind_ans.choice,
            industry_confidence=ind_ans.confidence,
            geography=geo_ans.choice,
            geography_confidence=geo_ans.confidence,
        )

        # ─────────────────────────────────────────────────────────────────────
        # Stage 2: Workflow Step Expansion & Tool Selection
        # ─────────────────────────────────────────────────────────────────────
        # Fetch canonical blueprint for the chosen intent, or default to outbound_pipeline
        blueprint_steps = WORKFLOW_BLUEPRINTS.get(
            intent_ans.choice,
            WORKFLOW_BLUEPRINTS["outbound_pipeline"]
        )

        workflow_steps = []
        for idx, step_template in enumerate(blueprint_steps, start=1):
            action_name = step_template["action"]
            default_reasoning = step_template["reasoning"]

            # Use Laya to verify or dynamically select the best tool from OPPORA_TOOLS
            tool_query = {
                "selected_tool": QuestionSpec(
                    type="choice",
                    instructions=f"For action '{action_name}' in workflow '{intent_ans.choice}', which Oppora tool should be invoked?",
                    criteria=OPPORA_TOOLS
                )
            }

            step_state = (
                f"Context: {prompt}\n"
                f"Current Action: {action_name}\n"
                f"Target Profile: {role_ans.choice} in {ind_ans.choice} ({geo_ans.choice})"
            )

            tool_ans_dict, _ = self.engine.decide(step_state, tool_query)
            tool_res = tool_ans_dict["selected_tool"]

            # Prefer high-confidence Laya tool decision, fallback to blueprint preference
            chosen_tool = tool_res.choice or step_template["preferred_tool"]
            tool_conf = tool_res.confidence if tool_res.choice else 0.85

            workflow_steps.append(
                WorkflowStep(
                    step_number=idx,
                    action=action_name,
                    tool=chosen_tool,
                    tool_description=OPPORA_TOOLS.get(chosen_tool, "Standard Oppora execution tool."),
                    confidence=tool_conf,
                    reasoning=f"{default_reasoning} Selected '{chosen_tool}' for {action_name}."
                )
            )

        total_elapsed_ms = (time.perf_counter() - start_total) * 1000.0

        plan = WorkflowPlan(
            workflow_id=f"wf_{uuid.uuid4().hex[:8]}",
            user_prompt=prompt,
            intent=intent_decision,
            target_scope=target_scope,
            steps=workflow_steps,
            total_latency_ms=round(total_elapsed_ms, 2),
            model_used=self.engine.default_model,
            standalone=True
        )

        return plan


# Global agent helper
_agent_instance: Optional[OpporaGTMAgent] = None

def get_gtm_agent() -> OpporaGTMAgent:
    """Returns singleton OpporaGTMAgent instance."""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = OpporaGTMAgent()
    return _agent_instance
