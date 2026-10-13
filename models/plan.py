"""Plan domain models.

A Plan is a list of Weeks; a Week is a list of Sessions; a Session is a list
of Prescriptions. Prescriptions carry a movement pattern, sets, reps, and an
RPE target so downstream schedulers can reason about fatigue.
"""
from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field


class Prescription(BaseModel):
    movement: str
    sets: int = Field(ge=1, le=10)
    reps: str  # e.g. "5" or "8-12" — kept as a string so AMRAP ranges survive
    rpe: float = Field(ge=4.0, le=10.0)
    rest_seconds: int = Field(ge=15, le=600)
    notes: str | None = None


class Session(BaseModel):
    day_label: str
    focus: str
    prescriptions: list[Prescription]
    estimated_minutes: int = Field(ge=10, le=180)


class Week(BaseModel):
    index: int = Field(ge=1)
    deload: bool = False
    sessions: list[Session]


class Plan(BaseModel):
    generated_on: date
    goal: str
    split: str
    weeks: list[Week]
    rationale: str

    @property
    def total_sessions(self) -> int:
        return sum(len(w.sessions) for w in self.weeks)