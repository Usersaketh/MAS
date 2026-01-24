from app.services.memory_service import ConversationMemoryService


def test_memory_service_persists_and_truncates(tmp_path):
    memory_path = tmp_path / "conversations.json"
    service = ConversationMemoryService(memory_path=str(memory_path), max_turns=3)

    service.append_turn("conv-1", "first question", "first answer", "general")
    service.append_turn("conv-1", "second question", "second answer", "billing")

    first_read = service.get_recent_turns("conv-1")
    assert len(first_read) == 3
    assert first_read[-1].content == "second answer"

    service.append_turn("conv-1", "third question", "third answer", "shipping")

    reloaded = ConversationMemoryService(memory_path=str(memory_path), max_turns=3)
    recent_turns = reloaded.get_recent_turns("conv-1")

    assert len(recent_turns) == 3
    assert recent_turns[0].content == "second answer"
    assert recent_turns[-1].content == "third answer"
