"""Onboarding handler — turns raw GUI input into an IntakeForm.

Keeps validation errors user-facing and non-fatal: the GUI can render them
inline rather than crashing on a bad field.
"""
from __future__ import annotations

from dataclasses import dataclass

from pydantic import ValidationError

from models.intake import IntakeForm


@dataclass(slots=True)
class OnboardingResult:
    intake: IntakeForm | None
    errors: dict[str, str]


def build_intake(raw: dict) -> OnboardingResult:
    try:
        intake = IntakeForm.model_validate(raw)
    except ValidationError as exc:
        errors: dict[str, str] = {}
        for err in exc.errors():
            field = ".".join(str(p) for p in err["loc"]) or "__root__"
            errors[field] = err["msg"]
        return OnboardingResult(intake=None, errors=errors)
    return OnboardingResult(intake=intake, errors={})