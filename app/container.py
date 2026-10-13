"""Dependency container.

Wires config, storage, inference, and the planner together. Kept deliberately
dumb — no magic, no DI framework, just explicit construction so the graph is
readable in one screen.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from config.loader import AppConfig
from services.inference import InferenceService
from services.storage import StorageService


@dataclass(slots=True)
class ServiceContainer:
    config: AppConfig
    data_dir: Path
    storage: StorageService
    inference: InferenceService

    @classmethod
    def build(cls, config: AppConfig, data_dir: Path) -> "ServiceContainer":
        data_dir.mkdir(parents=True, exist_ok=True)
        storage = StorageService(db_path=data_dir / "history.sqlite3")
        inference = InferenceService(
            checkpoint_dir=Path(config.models.checkpoint_dir),
            backend=config.models.backend,
            remote_url=config.models.remote_url,
        )
        return cls(config=config, data_dir=data_dir, storage=storage, inference=inference)

    def close(self) -> None:
        self.storage.close()
        self.inference.close()