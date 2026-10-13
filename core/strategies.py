"""Concrete planner strategies.

Each strategy produces a skeleton. None of them touch the scheduler — that's
the planner's job. Keep strategies pure: same intake in, same skeleton out.
"""
from __future__ import annotations

from datetime import date

from models.intake import IntakeForm
from models.plan import Plan, Prescription, Session, Week

_MOVEMENTS = {
    "push": ["bench press", "overhead press", "incline dumbbell press"],
    "pull": ["row", "lat pulldown", "face pull"],
    "legs": ["back squat", "romanian deadlift", "leg press", "calf raise"],
    "arms": ["curl", "triceps pushdown"],
    "core": ["plank", "hanging leg raise"],
}


def _session(day_label: str, focus: str, movements: list[str], minutes: int) -> Session:
    prescriptions = [
        Prescription(movement=m, sets=3, reps="8-12", rpe=7.5, rest_seconds=90)
        for m in movements
    ]
    return Session(
        day_label=day_label,
        focus=focus,
        prescriptions=prescriptions,
        estimated_minutes=minutes,
    )


class UpperLowerHypertrophy:
    name = "upper_lower_hypertrophy"
    split = "upper_lower"

    def skeleton(self, intake: IntakeForm, weeks: int) -> Plan:
        sessions = [
            _session("Day 1", "upper A", _MOVEMENTS["push"] + _MOVEMENTS["pull"], intake.session_minutes),
            _session("Day 2", "lower A", _MOVEMENTS["legs"] + _MOVEMENTS["core"], intake.session_minutes),
            _session("Day 4", "upper B", _MOVEMENTS["pull"] + _MOVEMENTS["arms"], intake.session_minutes),
            _session("Day 5", "lower B", _MOVEMENTS["legs"], intake.session_minutes),
        ]
        return Plan(
            generated_on=date.today(),
            goal=intake.goal.value,
            split=self.split,
            weeks=[Week(index=i + 1, deload=(i + 1) % 4 == 0, sessions=sessions) for i in range(weeks)],
            rationale="",
        )


class StrengthLinear:
    name = "strength_linear"
    split = "upper_lower_strength"

    def skeleton(self, intake: IntakeForm, weeks: int) -> Plan:
        sessions = [
            _session("Day 1", "squat focus", ["back squat", "bench press", "row"], intake.session_minutes),
            _session("Day 3", "deadlift focus", ["deadlift", "overhead press", "pull-up"], intake.session_minutes),
        ]
        return Plan(
            generated_on=date.today(),
            goal=intake.goal.value,
            split=self.split,
            weeks=[Week(index=i + 1, deload=(i + 1) % 4 == 0, sessions=sessions) for i in range(weeks)],
            rationale="",
        )


class MetabolicConditioning:
    name = "metabolic_conditioning"
    split = "full_body_conditioning"

    def skeleton(self, intake: IntakeForm, weeks: int) -> Plan:
        sessions = [
            _session("Day 1", "full body circuit", _MOVEMENTS["push"] + _MOVEMENTS["legs"], intake.session_minutes),
            _session("Day 3", "conditioning", ["rower intervals", "kettlebell swing", "farmer carry"], intake.session_minutes),
            _session("Day 5", "full body circuit", _MOVEMENTS["pull"] + _MOVEMENTS["core"], intake.session_minutes),
        ]
        return Plan(
            generated_on=date.today(),
            goal=intake.goal.value,
            split=self.split,
            weeks=[Week(index=i + 1, deload=(i + 1) % 4 == 0, sessions=sessions) for i in range(weeks)],
            rationale="",
        )


class PPLDouble:
    name = "ppl_double"
    split = "push_pull_legs"

    def skeleton(self, intake: IntakeForm, weeks: int) -> Plan:
        sessions = [
            _session("Day 1", "push A", _MOVEMENTS["push"], intake.session_minutes),
            _session("Day 2", "pull A", _MOVEMENTS["pull"], intake.session_minutes),
            _session("Day 3", "legs A", _MOVEMENTS["legs"], intake.session_minutes),
            _session("Day 4", "push B", _MOVEMENTS["push"] + _MOVEMENTS["arms"], intake.session_minutes),
            _session("Day 5", "pull B", _MOVEMENTS["pull"] + _MOVEMENTS["arms"], intake.session_minutes),
            _session("Day 6", "legs B", _MOVEMENTS["legs"] + _MOVEMENTS["core"], intake.session_minutes),
        ]
        return Plan(
            generated_on=date.today(),
            goal=intake.goal.value,
            split=self.split,
            weeks=[Week(index=i + 1, deload=(i + 1) % 4 == 0, sessions=sessions) for i in range(weeks)],
            rationale="",
        )


STRATEGIES: dict[str, object] = {
    "upper_lower_hypertrophy": UpperLowerHypertrophy(),
    "strength_linear": StrengthLinear(),
    "metabolic_conditioning": MetabolicConditioning(),
    "ppl_double": PPLDouble(),
}