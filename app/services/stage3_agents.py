from __future__ import annotations

from datetime import datetime

from app.core.config import settings
from app.schemas.query import EscalationDecision, IntentClassification, PolicyCheckResult
from app.services.llm_service import OllamaService


class IntentClassifierAgent:
    def __init__(self, llm: OllamaService) -> None:
        self.llm = llm

    def classify(self, query: str) -> IntentClassification:
        prompt = (
            "Classify the customer query into ONE of these intents: billing, shipping, account, complaint, or general.\n"
            "Also provide a confidence score (0.0 to 1.0) indicating how certain you are of this classification.\n\n"
            f"Query: {query}\n\n"
            "Respond in format: INTENT: <intent>, CONFIDENCE: <score>"
        )
        response = self.llm.generate(prompt)
        # Parse response (simple extraction)
        intent = "general"
        confidence = 0.5
        try:
            if "INTENT:" in response and "CONFIDENCE:" in response:
                intent_part = response.split("INTENT:")[1].split(",")[0].strip().lower()
                conf_part = response.split("CONFIDENCE:")[1].strip().split()[0]
                if intent_part in ["billing", "shipping", "account", "complaint", "general"]:
                    intent = intent_part
                confidence = min(1.0, max(0.0, float(conf_part)))
        except (ValueError, IndexError):
            pass
        return IntentClassification(intent=intent, confidence=confidence)


class EscalationEvaluatorAgent:
    def __init__(self, llm: OllamaService) -> None:
        self.llm = llm
        self.confidence_threshold = settings.escalation_confidence_threshold

    def evaluate(
        self, query: str, intent: str, confidence: float, context: list[str]
    ) -> EscalationDecision:
        escalation_keywords = ["angry", "unfair", "stolen", "broken", "fraud", "urgent"]
        has_escalation_keyword = any(kw in query.lower() for kw in escalation_keywords)
        low_confidence = confidence < self.confidence_threshold

        if has_escalation_keyword or low_confidence:
            reason = "Low confidence in intent classification"
            if has_escalation_keyword:
                reason = "Query contains escalation indicators (anger, fraud, etc.)"
            return EscalationDecision(needs_escalation=True, reason=reason)

        return EscalationDecision(needs_escalation=False, reason="Standard handling sufficient")


class PolicyGuardrailsAgent:
    def __init__(self, llm: OllamaService) -> None:
        self.llm = llm

    def check(self, query: str, intent: str) -> PolicyCheckResult:
        violations: list[str] = []
        notes = ""

        # Refund policy check
        if "refund" in query.lower():
            notes += f"Refund eligibility window: {settings.max_refund_days} days. "
            if "after" in query.lower() or "days" in query.lower():
                violations.append(
                    f"Refund policy: requests beyond {settings.max_refund_days} days may be denied"
                )

        # Cancellation policy check
        if "cancel" in query.lower() and intent in ["billing", "general"]:
            notes += f"Cancellation window: {settings.max_cancellation_minutes} minutes. "
            if "hour" in query.lower() or "day" in query.lower():
                violations.append(
                    f"Cancellation policy: cancellations after {settings.max_cancellation_minutes} minutes may not be permitted"
                )

        # Abuse/spam prevention
        if len(query) > 1000 or query.count("?") > 5:
            violations.append("Query appears to be spam or abuse attempt")

        passes_policy = len(violations) == 0

        return PolicyCheckResult(passes_policy=passes_policy, violations=violations, notes=notes.strip())
