from __future__ import annotations

import json
import os
from datetime import datetime, timezone

from app.core.config import settings
from app.schemas.query import ConversationTurn


class ConversationMemoryService:
    def __init__(self, memory_path: str | None = None, max_turns: int | None = None) -> None:
        self.memory_path = memory_path or settings.conversation_memory_path
        self.max_turns = max_turns or settings.max_memory_turns

    def _load_all(self) -> dict[str, list[dict[str, str]]]:
        if not os.path.exists(self.memory_path):
            return {}

        with open(self.memory_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        return data if isinstance(data, dict) else {}

    def _save_all(self, payload: dict[str, list[dict[str, str]]]) -> None:
        os.makedirs(os.path.dirname(self.memory_path), exist_ok=True)
        with open(self.memory_path, "w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=True, indent=2)

    def get_recent_turns(self, conversation_id: str) -> list[ConversationTurn]:
        data = self._load_all()
        turns = data.get(conversation_id, [])[-self.max_turns :]
        return [ConversationTurn(**turn) for turn in turns]

    def append_turn(self, conversation_id: str, user_query: str, assistant_answer: str, intent: str) -> None:
        data = self._load_all()
        turns = data.get(conversation_id, [])

        timestamp = datetime.now(timezone.utc).isoformat()
        turns.append(
            {
                "role": "user",
                "content": user_query,
                "intent": intent,
                "timestamp": timestamp,
            }
        )
        turns.append(
            {
                "role": "assistant",
                "content": assistant_answer,
                "intent": intent,
                "timestamp": timestamp,
            }
        )

        data[conversation_id] = turns[-(self.max_turns * 2) :]
        self._save_all(data)
