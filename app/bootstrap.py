"""Bootstrap entry point.

Resolves platform dirs, loads config, constructs the service container, and
hands control to the GUI. Also supports a headless `--plan` path used by the
CLI and by CI smoke tests.
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from platformdirs import user_data_dir

from app.container import ServiceContainer
from config.loader import load_config
from core.planner import Planner
from models.intake import IntakeForm


def _configure_logging(log_path: Path) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[logging.FileHandler(log_path), logging.StreamHandler(sys.stderr)],
    )


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="ai-workout-plan-generator")
    parser.add_argument("--plan", metavar="INTAKE_JSON", help="Headless: generate a plan from an intake JSON file.")
    parser.add_argument("--out", metavar="PATH", default=None, help="Where to write the plan when using --plan.")
    parser.add_argument("--no-gui", action="store_true", help="Force headless mode.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv if argv is not None else sys.argv[1:])
    data_dir = Path(user_data_dir("ai-workout-plan-generator", "awpg"))
    _configure_logging(data_dir / "last_run.log")

    config = load_config()
    container = ServiceContainer.build(config=config, data_dir=data_dir)

    if args.plan:
        intake = IntakeForm.model_validate_json(Path(args.plan).read_text(encoding="utf-8"))
        plan = Planner(container).generate(intake)
        out = Path(args.out) if args.out else data_dir / "plan.json"
        out.write_text(plan.model_dump_json(indent=2), encoding="utf-8")
        print(f"plan written to {out}")
        return 0

    if args.no_gui:
        logging.getLogger(__name__).error("no GUI requested and no --plan provided")
        return 2

    from handlers.main_window import run_gui

    return run_gui(container)


if __name__ == "__main__":
    raise SystemExit(main())