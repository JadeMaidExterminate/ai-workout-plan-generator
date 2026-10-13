"""Intake form — the single source of truth for user input.

Every field is validated at the boundary. Downstream code can assume a valid
IntakeForm and never re-check.
"""
from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class Goal(str, Enum):
    HYPERTROPHY = "hypertrophy"
    STRENGTH = "strength"
    ENDURANCE = "endurance"
    FAT_LOSS = "fat_loss"
    GENERAL_HEALTH = "general_health"


class Experience(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class Equipment(str, Enum):
    BODYWEIGHT = "bodyweight"
    DUMBBELLS = "dumbbells"
    BARBELL = "barbell"
    MACHINES = "machines"
    FULL_GYM = "full_gym"


class IntakeForm(BaseModel):
    """User intake. All fields validated; no free-form strings downstream."""

    model_config = {"extra": "forbid"}

    name: str = Field(min_length=1, max_length=64)
    age: int = Field(ge=13, le=99)
    sex: Literal["male", "female", "other"]
    height_cm: float = Field(ge=120.0, le=230.0)
    weight_kg: float = Field(ge=35.0, le=250.0)
    goal: Goal
    experience: Experience
    equipment: Equipment
    days_per_week: int = Field(ge=2, le=6)
    session_minutes: int = Field(ge=20, le=120)
    injuries: list[str] = Field(default_factory=list, max_length=8)

    @field_validator("injuries")
    @classmethod
    def _normalize_injuries(cls, value: list[str]) -> list[str]:
        return [v.strip().lower() for v in value if v.strip()]

    @property
    def bmi(self) -> float:
        return self.weight_kg / ((self.height_cm / 100.0) ** 2)

    @property
    def is_novice(self) -> bool:
        return self.experience is Experience.BEGINNER