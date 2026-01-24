from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone

from app.core.config import settings
from app.schemas.query import TraceEvent


@dataclass
class TraceRun:
    trace_id: str
    conversation_id: str
    events: list[TraceEvent]


class TraceService:
    def __init__(self, trace_path: str | None = None) -> None:
        self.trace_path = trace_path or settings.trace_log_path

    def _load_all(self) -> list[dict[str, object]]:
        if not os.path.exists(self.trace_path):
            return []

        with open(self.trace_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        return data if isinstance(data, list) else []

    def _save_all(self, payload: list[dict[str, object]]) -> None:
        os.makedirs(os.path.dirname(self.trace_path), exist_ok=True)
        with open(self.trace_path, "w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=True, indent=2)

    def begin_run(self, conversation_id: str) -> TraceRun:
        trace_id = f"trace-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"
        return TraceRun(trace_id=trace_id, conversation_id=conversation_id, events=[])

    def record(
        self,
        run: TraceRun,
        step: str,
        status: str,
        message: str | None = None,
        duration_ms: float | None = None,
    ) -> None:
        run.events.append(
            TraceEvent(
                step=step,
                status=status,
                timestamp=datetime.now(timezone.utc).isoformat(),
                duration_ms=duration_ms,
                message=message,
            )
        )

    def finish_run(self, run: TraceRun) -> None:
        payload = self._load_all()
        payload.append(
            {
                "trace_id": run.trace_id,
                "conversation_id": run.conversation_id,
                "events": [event.model_dump() for event in run.events],
            }
        )
        self._save_all(payload)

    def get_latest(self, conversation_id: str) -> list[TraceEvent]:
        runs = [run for run in self._load_all() if run.get("conversation_id") == conversation_id]
        if not runs:
            return []
        latest = runs[-1]
        return [TraceEvent(**event) for event in latest.get("events", [])]
