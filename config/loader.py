"""TOML config loader with a typed view.

Reads `config/defaults.toml`, then overlays `~/.config/ai-workout-plan-generator/user.toml`
if present. Unknown keys are rejected so typos don't silently no-op.
"""
from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

from platformdirs import user_config_dir


@dataclass(frozen=True, slots=True)
class ModelsConfig:
    backend: str
    checkpoint_dir: str
    remote_url: str | None
    max_plan_weeks: int


@dataclass(frozen=True, slots=True)
class PlannerConfig:
    default_split: str
    min_days_per_week: int
    max_days_per_week: int
    recovery_ceiling_rpe: float


@dataclass(frozen=True, slots=True)
class AppConfig:
    app_name: str
    locale: str
    models: ModelsConfig
    planner: PlannerConfig


_ALLOWED_TOP = {"app", "models", "planner"}


def _load_toml(path: Path) -> dict:
    with path.open("rb") as fh:
        return tomllib.load(fh)


def load_config(defaults_path: Path | None = None) -> AppConfig:
    defaults_path = defaults_path or Path(__file__).with_name("defaults.toml")
    raw = _load_toml(defaults_path)

    user_path = Path(user_config_dir("ai-workout-plan-generator")) / "user.toml"
    if user_path.is_file():
        for key, value in _load_toml(user_path).items():
            if key not in _ALLOWED_TOP:
                raise ValueError(f"unknown config section: {key!r}")
            raw.setdefault(key, {}).update(value)

    app = raw.get("app", {})
    models = raw["models"]
    planner = raw["planner"]

    return AppConfig(
        app_name=app.get("name", "ai-workout-plan-generator"),
        locale=app.get("locale", "en-US"),
        models=ModelsConfig(
            backend=models["backend"],
            checkpoint_dir=models["checkpoint_dir"],
            remote_url=models.get("remote_url"),
            max_plan_weeks=int(models.get("max_plan_weeks", 16)),
        ),
        planner=PlannerConfig(
            default_split=planner["default_split"],
            min_days_per_week=int(planner["min_days_per_week"]),
            max_days_per_week=int(planner["max_days_per_week"]),
            recovery_ceiling_rpe=float(planner["recovery_ceiling_rpe"]),
        ),
    )