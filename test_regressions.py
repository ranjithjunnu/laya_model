"""Regression checks for the observed planning failures; no model inference."""

import unittest
from unittest.mock import patch

from pydantic import ValidationError
from contracts import ChoiceAnswer, GTMPlanRequest, QuestionSpec
from engine import DecisionEngine
from gtm_agent import OpporaGTMAgent
from taxonomy import GTM_INTENTS, OPPORA_TOOLS, WORKFLOW_BLUEPRINTS


class WrongPredictionEngine:
    """Deliberately wrong predictions ensure rules, not model luck, fix the bugs."""
    default_model = "typed-decisions"

    def __init__(self, intent="account_discovery", confidence=0.2):
        self.intent = intent
        self.confidence = confidence

    def decide(self, prompt, questions):
        labels = {"intent": self.intent, "role": "sales_leaders", "industry": "fintech", "geography": "us_nationwide"}
        return {field: ChoiceAnswer(choice=label, confidence=self.confidence, probabilities={label: self.confidence}) for field, label in labels.items()}, 0


def plan(prompt, engine=None):
    with patch("gtm_agent.get_engine", return_value=engine or WrongPredictionEngine()):
        return OpporaGTMAgent().plan_workflow(GTMPlanRequest(prompt=prompt))


class PlannerRegressions(unittest.TestCase):
    def test_all_intents_have_valid_blueprints(self):
        self.assertEqual(set(GTM_INTENTS), set(WORKFLOW_BLUEPRINTS))
        for blueprint in WORKFLOW_BLUEPRINTS.values():
            self.assertTrue(blueprint)
            for step in blueprint:
                self.assertIn(step["preferred_tool"], OPPORA_TOOLS)

    def test_explicit_operations(self):
        cases = [
            ("Find IT services companies in India", "account_discovery", ["discover_companies"], "none_specified", "it_services", "india"),
            ("Find VP of engineering in the USA", "contact_hunting", ["find_decision_makers"], "engineering_leaders", "none_specified", "us_nationwide"),
            ("Find SaaS founders in California and generate an outbound workflow.", "outbound_pipeline", ["discover_companies", "find_decision_makers", "verify_contact_data", "qualify_leads"], "founders_c_level", "b2b_saas", "california_west_us"),
            ("Enrich existing company records with missing firmographics.", "enrichment_only", ["enrich_records"], "none_specified", "none_specified", "none_specified"),
            ("Classify incoming sales replies and out-of-office responses.", "inbound_triage", ["classify_incoming_replies"], "none_specified", "none_specified", "none_specified"),
            ("Validate, clean, and purge bouncing email addresses in our CRM database.", "crm_cleanup", ["verify_contact_data"], "none_specified", "none_specified", "none_specified"),
            ("Find companies", "account_discovery", ["discover_companies"], "none_specified", "none_specified", "none_specified"),
            ("Discover VPs of Engineering at European fintech companies.", "contact_hunting", ["find_decision_makers"], "engineering_leaders", "fintech", "europe"),
            ("Find IT services companies in India without outreach", "account_discovery", ["discover_companies"], "none_specified", "it_services", "india"),
        ]
        for prompt, intent, actions, role, industry, geography in cases:
            with self.subTest(prompt=prompt):
                result = plan(prompt)
                self.assertEqual(result.status, "planned")
                self.assertEqual(result.intent.intent, intent)
                self.assertEqual([step.action for step in result.steps], actions)
                self.assertEqual((result.target_scope.role, result.target_scope.industry, result.target_scope.geography), (role, industry, geography))

    def test_email_search_keeps_verification(self):
        result = plan("Find VP of Engineering emails in the USA")
        self.assertEqual(result.intent.intent, "contact_hunting")
        self.assertEqual([step.action for step in result.steps], ["find_decision_makers", "verify_contact_data"])

    def test_rules_preserve_raw_model_scores_without_fake_confidence(self):
        result = plan("Find VP of engineering in the USA")
        self.assertEqual(result.model_predictions["intent"].choice, "account_discovery")
        self.assertEqual(result.model_predictions["intent"].confidence, 0.2)
        self.assertIsNone(result.intent.confidence)
        self.assertEqual(result.intent.source, "explicit_rule")
        self.assertIsNone(result.steps[0].confidence)
        self.assertEqual(result.steps[0].source, "fixed_mapping")

    def test_missing_blueprint_never_becomes_outbound(self):
        result = plan("An unrecognised request", WrongPredictionEngine("unknown_intent", 0.9))
        self.assertEqual(result.status, "unsupported")
        self.assertEqual(result.steps, [])

    def test_uncertain_model_does_not_expand_workflow(self):
        result = plan("Help with this task")
        self.assertEqual(result.status, "needs_clarification")
        self.assertEqual(result.steps, [])
        self.assertTrue(result.clarification)

    def test_supported_model_choice_can_plan_without_rule(self):
        result = plan("Please handle missing firmographics", WrongPredictionEngine("enrichment_only", 0.8))
        self.assertEqual(result.status, "planned")
        self.assertEqual(result.intent.source, "model_probability")
        self.assertEqual(result.steps[0].action, "enrich_records")

    def test_unsupported_and_multiple_targets_need_clarification(self):
        for prompt in ("Find companies in Canada", "Find companies in Atlantis", "Find manufacturing companies", "Find companies in India and the USA"):
            with self.subTest(prompt=prompt):
                result = plan(prompt)
                self.assertEqual(result.status, "needs_clarification")
                self.assertEqual(result.steps, [])
                self.assertTrue(result.warnings)

    def test_blank_prompts_are_rejected(self):
        for prompt in ("", "   ", "\n\t"):
            with self.subTest(prompt=repr(prompt)), self.assertRaises(ValidationError):
                GTMPlanRequest(prompt=prompt)
        self.assertEqual(GTMPlanRequest(prompt="  Find companies  ").prompt, "Find companies")

    def test_engine_does_not_invent_missing_scores(self):
        class RouterWithoutScores:
            def predict(self, *args, **kwargs):
                return {"answers": {"intent": {"choice": "account_discovery"}}}
        engine = object.__new__(DecisionEngine)
        engine.router = RouterWithoutScores()
        engine.default_model = "typed-decisions"
        answers, _ = engine.decide("Find companies", {"intent": QuestionSpec(instructions="Choose an intent", criteria=["account_discovery"])})
        self.assertIsNone(answers["intent"].confidence)
        self.assertEqual(answers["intent"].source, "unavailable")


if __name__ == "__main__":
    unittest.main(verbosity=2)
