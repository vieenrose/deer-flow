"""The memory-update prompt must keep third-party specs out of user memory.

Regression: unverified bandwidth/price figures from earlier assistant answers
were stored as high-confidence facts (one as a 0.96 "correction") and then
injected into later threads, where a local model repeated them as research.
"""

from deerflow.agents.memory.backends.deermem.deermem.core.prompt import load_prompt_messages

_VARIABLES = {
    "current_memory": "",
    "conversation": "",
    "correction_hint": "",
    "staleness_review_section": "",
    "consolidation_section": "",
}


def _system_prompt() -> str:
    return load_prompt_messages("memory_update", _VARIABLES)[0].content


def test_memory_update_prompt_excludes_third_party_specs():
    system = _system_prompt()
    assert "Do NOT store third-party product specs, prices, benchmarks" in system
    assert "Record only that the user is researching or comparing those products" in system


def test_memory_update_prompt_requires_user_origin_for_corrections():
    system = _system_prompt()
    assert "Never turn the assistant's own claims into facts" in system
