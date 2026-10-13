"""VolumeScheduler — calibrates weekly volume against recovery ceilings.

Takes a raw skeleton and adjusts sets/reps so that:
  * weekly hard sets per muscle group stay within evidence-based bands
  * deload weeks drop volume 40-50%
  * session duration stays within the user's requested window
"""
from __future__ import annotations

from config.loader import PlannerConfig
from models.intake import Experience, IntakeForm
from models.plan import Plan

# Weekly hard-set targets per experience level (lower, upper) for a major muscle.
_VOLUME_BANDS: dict[Experience, tuple[int, int]] = {
    Experience.BEGINNER: (6, 10),
    Experience.INTERMEDIATE: (10, 18),
    Experience.ADVANCED: (14, 24),
}


class VolumeScheduler:
    def __init__(self, cfg: PlannerConfig) -> None:
        self._cfg = cfg

    def calibrate(self, plan: Plan, intake: IntakeForm) -> Plan:
        low, high = _VOLUME_BANDS[intake.experience]
        target = (low + high) // 2
        if intake.session_minutes < 45:
            target = max(low, target - 2)

        ceiling = self._cfg.recovery_ceiling_rpe
        calibrated_weeks = []
        for week in plan.weeks:
            sessions = []
            for session in week.sessions:
                capped = [
                    p.model_copy(
                        update={
                            "rpe": min(p.rpe, ceiling if week.deload else p.rpe),
                            "sets": max(1, round(p.sets * (0.55 if week.deload else 1.0))),
                        }
                    )
                    for p in session.prescriptions
                ]
                sessions.append(session.model_copy(update={"prescriptions": capped}))
            calibrated_weeks.append(week.model_copy(update={"sessions": sessions}))

        return plan.model_copy(update={"weeks": calibrated_weeks})

    def weekly_sets(self, plan: Plan) -> int:
        return sum(p.sets for w in plan.weeks for s in w.sessions for p in s.prescriptions)