# Contributing to ai-workout-plan-generator

Thanks for wanting to help build the tater-powered coach. This repo is a
Python desktop tool that generates personalized workout plans from a short
intake form. It runs fully offline by default; the AI planner is a local
inference layer with an optional remote backend.

## Ground rules

- Python 3.11+. We test on 3.11 and 3.12.
- Format with `black`, lint with `ruff`, type-check with `mypy --strict` on `core/`.
- Every new generator strategy goes behind the `PlannerStrategy` protocol in
  `core/planner.py`. No strategy talks to the GUI directly.
- Keep the intake schema in `models/intake.py` as the single source of truth.
  If you add a field, add it there first, then to the TOML defaults in
  `config/defaults.toml`, then to the form in `handlers/onboarding.py`.
- Tests: `pytest -q`. New behavior needs a test in `tests/`.

## Repo layout

```
ai-workout-plan-generator/
├── app/                # entry + bootstrap
├── core/               # engine, planner, scheduler
├── handlers/           # feature-level handlers (onboarding, export, sync)
├── services/           # long-lived services (inference, storage, telemetry-off)
├── models/             # dataclasses + domain models
├── utils/              # shared helpers
├── config/             # TOML config + schema
├── tests/              # pytest
└── tools/              # dev scripts, packaging
```

## Commit style

`<area>: <imperative summary>` — e.g. `core: clamp weekly volume to recovery ceiling`.

## Pull requests

- One concern per PR.
- Include a before/after on the plan output if you touched `core/planner.py`.
- Screenshots for any GUI change in `handlers/`.

## Reporting issues

Open an issue with your OS, Python version, and the contents of
`data/local/last_run.log`. Do not paste personal health data — redact it.