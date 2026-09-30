"""
demo_client.py — Standalone Demo Runner for Oppora GTM Agent.

Demonstrates autonomous GTM workflow planning using the local Laya Decision Engine.
Runs directly in-process or queries the local HTTP server.
"""

import json
import sys
from contracts import GTMPlanRequest
from gtm_agent import get_gtm_agent


DEMO_PROMPTS = [
    # 1. The Lead's Exact Target Prompt:
    "Find SaaS founders in California and generate an outbound workflow.",

    # 2. Targeted Contact Hunting in Fintech:
    "Discover VPs of Engineering and CTOs at European fintech companies.",

    # 3. Data Hygiene / Bounce Cleanup:
    "Validate, clean, and purge bouncing email addresses in our CRM database."
]


def print_banner(text: str) -> None:
    width = 76
    print("\n" + "=" * width)
    print(f" {text}")
    print("=" * width)


def run_demo() -> None:
    print_banner("OPPORA STANDALONE AI DECISION SERVICE (POWERED BY LAYA)")
    print("Zero External LLM Dependency (No OpenAI, No Claude, No Hosted JEV API)")
    print("All decisions, routing, and workflow planning executed locally on PyTorch.\n")

    agent = get_gtm_agent()

    for idx, prompt in enumerate(DEMO_PROMPTS, start=1):
        print_banner(f"TEST CASE {idx}: \"{prompt}\"")

        request = GTMPlanRequest(prompt=prompt)
        plan = agent.plan_workflow(request)

        print(f"Workflow ID       : {plan.workflow_id}")
        print(f"Total Planning Latency: {plan.total_latency_ms:.2f} ms")
        print(f"Decision Model    : {plan.model_used} (Self-Hosted: {plan.standalone})")
        print("-" * 76)

        print("\n[STAGE 1: INTENT & TARGET DECOMPOSITION]")
        print(f"  • Classified Intent : {plan.intent.intent} (Confidence: {plan.intent.confidence:.2%})")
        print(f"  • Target Role       : {plan.target_scope.role} (Confidence: {plan.target_scope.role_confidence:.2%})")
        print(f"  • Target Industry   : {plan.target_scope.industry} (Confidence: {plan.target_scope.industry_confidence:.2%})")
        print(f"  • Target Geography  : {plan.target_scope.geography} (Confidence: {plan.target_scope.geography_confidence:.2%})")

        print("\n[STAGE 2: PLANNED WORKFLOW STEPS & TOOL SELECTION]")
        for step in plan.steps:
            print(f"  Step {step.step_number}: [{step.action.upper()}]")
            print(f"         Selected Tool : {step.tool} (Confidence: {step.confidence:.2%})")
            print(f"         Tool Purpose  : {step.tool_description}")
            print(f"         Reasoning     : {step.reasoning}")

        print("\n[STAGE 3: RAW STRUCTURED JSON PAYLOAD (OPPORA COMPATIBLE)]")
        formatted_json = json.dumps(plan.model_dump(), indent=2)
        print(formatted_json)

    print_banner("DEMO COMPLETED SUCCESSFULLY")


if __name__ == "__main__":
    run_demo()
