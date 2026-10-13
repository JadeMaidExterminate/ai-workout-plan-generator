"""Planner — orchestrates strategy selection and delegates to the engine.

The planner is the only place that knows about the intake form and the
inference service at the same time. It picks a strategy, asks the engine for
a skeleton, then hands off to the scheduler for volume calibration.
"""
from __future__ import annotations

import logging
from typing import Protocol

from app.container import ServiceContainer
from core.engine import TrainingEngine
from core.scheduler import VolumeScheduler
from models.intake import IntakeForm, Goal
from models.plan import Plan

log = logging.getLogger(__name__)


class PlannerStrategy(Protocol):
    name: str
    split: str

    def skeleton(self, intake: IntakeForm, weeks: int) -> Plan: ...


class Planner:
    def __init__(self, container: ServiceContainer) -> None:
        self._container = container
        self._engine = TrainingEngine(container.inference)
        self._scheduler = VolumeScheduler(container.config.planner)

    def _pick_strategy(self, intake: IntakeForm) -> PlannerStrategy:
        from core.strategies import STRATEGIES

        if intake.goal is Goal.STRENGTH:
            return STRATEGIES["strength_linear"]
        if intake.goal is Goal.FAT_LOSS:
            return STRATEGIES["metabolic_conditioning"]
        if intake.days_per_week >= 5 and intake.experience.value == "advanced":
            return STRATEGIES["ppl_double"]
        return STRATEGIES["upper_lower_hypertrophy"]

    def generate(self, intake: IntakeForm) -> Plan:
        strategy = self._pick_strategy(intake)
        log.info("planner: selected strategy=%s for goal=%s", strategy.name, intake.goal.value)

        weeks = min(self._container.config.models.max_plan_weeks, 12)
        skeleton = strategy.skeleton(intake, weeks)
        calibrated = self._scheduler.calibrate(skeleton, intake)
        rationale = self._engine.explain(intake, calibrated)
        return calibrated.model_copy(update={"rationale": rationale})