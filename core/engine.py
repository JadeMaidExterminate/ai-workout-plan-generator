"""TrainingEngine — bridges plans to the inference service.

The engine is deliberately thin: it asks the inference service for a plan
skeleton when a remote backend is configured, and otherwise runs a
deterministic local heuristic. Explanations always come from the local
model so plans remain reproducible offline.
"""
from __future__ import annotations

import logging

from models.intake import IntakeForm
from models.plan import Plan, Session, Week
from services.inference import InferenceService

log = logging.getLogger(__name__)


class TrainingEngine:
    def __init__(self, inference: InferenceService) -> None:
        self._inference = inference

    def skeleton(self, intake: IntakeForm, weeks: int) -> Plan:
        if self._inference.backend == "remote" and self._inference.remote_available():
            try:
                return self._inference.remote_skeleton(intake, weeks)
            except Exception:  # noqa: BLE001 — fall back to local, never block the user
                log.warning("remote skeleton failed, falling back to local", exc_info=True)
        return self._local_skeleton(intake, weeks)

    def explain(self, intake: IntakeForm, plan: Plan) -> str:
        days = intake.days_per_week
        ceiling = plan.weeks[0].sessions[0].prescriptions[0].rpe if plan.weeks else 7.0
        return (
            f"{intake.days_per_week}-day {plan.split.replace('_', ' ')} block for a "
            f"{intake.experience.value} lifter training {days} days/week. "
            f"Top-set RPE capped at {ceiling:.1f}. Deload every 4th week. "
            f"Adjust volume ±10% based on sleep and soreness."
        )

    def _local_skeleton(self, intake: IntakeForm, weeks: int) -> Plan:
        from datetime import date

        # Placeholder skeleton — strategies overwrite this before scheduling.
        placeholder = Session(
            day_label="Day 1",
            focus="full body",
            prescriptions=[],
            estimated_minutes=intake.session_minutes,
        )
        return Plan(
            generated_on=date.today(),
            goal=intake.goal.value,
            split="full_body",
            weeks=[Week(index=i + 1, deload=(i + 1) % 4 == 0, sessions=[placeholder]) for i in range(weeks)],
            rationale="",
        )