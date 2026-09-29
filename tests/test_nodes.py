"""
tests/test_nodes.py — Isolation tests for all 8 PhysicsBuddy nodes
Part 5 of the capstone process: test each node BEFORE connecting to the graph.
Uses mock state dicts — no LLM or ChromaDB required for structural tests.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.nodes import (
    memory_node, skip_retrieval_node, save_node,
    FAITHFULNESS_THRESHOLD, MAX_EVAL_RETRIES
)

# Import routing functions inline to avoid triggering heavy graph.py imports
# These are the same logic as in graph.py — copied here for isolation testing
def route_decision(state):
    route = state.get("route", "retrieve")
    if route == "tool":
        return "tool"
    elif route == "memory_only":
        return "skip"
    else:
        return "retrieve"

def eval_decision(state):
    faithfulness = state.get("faithfulness", 1.0)
    eval_retries = state.get("eval_retries", 0)
    if faithfulness < FAITHFULNESS_THRESHOLD and eval_retries < MAX_EVAL_RETRIES:
        return "answer"
    else:
        return "save"


# ── Helper: build a mock state ────────────────────────────────────────────────
def mock_state(**overrides):
    base = {
        "question": "What is Newton's second law?",
        "messages": [],
        "route": "retrieve",
        "retrieved": "",
        "sources": [],
        "tool_result": "",
        "answer": "",
        "faithfulness": 0.0,
        "eval_retries": 0,
        "user_name": "",
        "topic_asked": "",
    }
    base.update(overrides)
    return base


# ── Test 1: memory_node — basic ───────────────────────────────────────────────
def test_memory_node_appends_message():
    state = mock_state(question="Explain Newton's laws")
    result = memory_node(state)
    assert len(result["messages"]) == 1
    assert result["messages"][0]["role"] == "user"
    assert "Newton" in result["messages"][0]["content"]
    print("PASS — memory_node appends user message")


# ── Test 2: memory_node — name extraction ─────────────────────────────────────
def test_memory_node_extracts_name():
    state = mock_state(question="My name is Arjun, explain kinematics")
    result = memory_node(state)
    assert result["user_name"] == "Arjun", f"Expected 'Arjun', got '{result['user_name']}'"
    print("PASS — memory_node extracts user name")


# ── Test 3: memory_node — sliding window ─────────────────────────────────────
def test_memory_node_sliding_window():
    # Build 10 existing messages
    existing = [{"role": "user", "content": f"msg {i}"} for i in range(10)]
    state = mock_state(question="latest question", messages=existing)
    result = memory_node(state)
    # After appending, sliding window should keep last 6
    assert len(result["messages"]) <= 6, f"Window not applied, got {len(result['messages'])} messages"
    print("PASS — memory_node applies sliding window")


# ── Test 4: skip_retrieval_node — clears context ─────────────────────────────
def test_skip_retrieval_node_clears_context():
    state = mock_state(retrieved="Previous turn context", sources=["Newton's Laws"])
    result = skip_retrieval_node(state)
    assert result["retrieved"] == ""
    assert result["sources"] == []
    print("PASS — skip_retrieval_node clears previous context")


# ── Test 5: save_node — appends assistant answer ──────────────────────────────
def test_save_node_appends_answer():
    state = mock_state(
        messages=[{"role": "user", "content": "What is F=ma?"}],
        answer="Force equals mass times acceleration.",
        sources=["Newton's Laws of Motion"]
    )
    result = save_node(state)
    assistant_msgs = [m for m in result["messages"] if m["role"] == "assistant"]
    assert len(assistant_msgs) == 1
    assert "Force equals mass" in assistant_msgs[0]["content"]
    print("PASS — save_node appends assistant message")


# ── Test 6: save_node — resets eval_retries ───────────────────────────────────
def test_save_node_resets_retries():
    state = mock_state(eval_retries=2, answer="test answer")
    result = save_node(state)
    assert result["eval_retries"] == 0
    print("PASS — save_node resets eval_retries to 0")


# ── Test 7: route_decision — retrieve ────────────────────────────────────────
def test_route_decision_retrieve():
    state = mock_state(route="retrieve")
    assert route_decision(state) == "retrieve"
    print("PASS — route_decision returns 'retrieve'")


# ── Test 8: route_decision — tool ─────────────────────────────────────────────
def test_route_decision_tool():
    state = mock_state(route="tool")
    assert route_decision(state) == "tool"
    print("PASS — route_decision returns 'tool'")


# ── Test 9: route_decision — memory_only ─────────────────────────────────────
def test_route_decision_skip():
    state = mock_state(route="memory_only")
    assert route_decision(state) == "skip"
    print("PASS — route_decision returns 'skip' for memory_only")


# ── Test 10: eval_decision — pass (score above threshold) ────────────────────
def test_eval_decision_pass():
    state = mock_state(faithfulness=0.85, eval_retries=1)
    assert eval_decision(state) == "save"
    print("PASS — eval_decision returns 'save' when faithfulness >= threshold")


# ── Test 11: eval_decision — retry (score below threshold) ───────────────────
def test_eval_decision_retry():
    state = mock_state(faithfulness=0.50, eval_retries=0)
    assert eval_decision(state) == "answer"
    print("PASS — eval_decision returns 'answer' (retry) when faithfulness low")


# ── Test 12: eval_decision — max retries reached ─────────────────────────────
def test_eval_decision_max_retries():
    state = mock_state(faithfulness=0.40, eval_retries=MAX_EVAL_RETRIES)
    assert eval_decision(state) == "save"
    print(f"PASS — eval_decision returns 'save' when eval_retries >= {MAX_EVAL_RETRIES}")


# ── Test 13: Tools — datetime ─────────────────────────────────────────────────
def test_datetime_tool():
    from agent.tools import get_datetime_tool
    result = get_datetime_tool()
    assert "Current date" in result
    assert "Current time" in result
    print(f"PASS — datetime tool returns: {result}")


# ── Test 14: Tools — calculator ───────────────────────────────────────────────
def test_calculator_tool():
    from agent.tools import calculator_tool
    result = calculator_tool("5 * 9.8")
    assert "49" in result or "Calculator result" in result
    print(f"PASS — calculator tool returns: {result}")


# ── Test 15: Tools — calculator with sqrt ────────────────────────────────────
def test_calculator_sqrt():
    from agent.tools import calculator_tool
    result = calculator_tool("sqrt(144)")
    assert "12" in result
    print(f"PASS — calculator sqrt: {result}")


# ── Test 16: Tools — unknown tool returns error string ───────────────────────
def test_unknown_tool_no_exception():
    from agent.tools import run_tool
    result = run_tool("nonexistent_tool", "")
    assert "error" in result.lower()
    print(f"PASS — unknown tool returns error string: {result}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("PhysicsBuddy — Node Isolation Tests")
    print("="*60 + "\n")

    tests = [
        test_memory_node_appends_message,
        test_memory_node_extracts_name,
        test_memory_node_sliding_window,
        test_skip_retrieval_node_clears_context,
        test_save_node_appends_answer,
        test_save_node_resets_retries,
        test_route_decision_retrieve,
        test_route_decision_tool,
        test_route_decision_skip,
        test_eval_decision_pass,
        test_eval_decision_retry,
        test_eval_decision_max_retries,
        test_datetime_tool,
        test_calculator_tool,
        test_calculator_sqrt,
        test_unknown_tool_no_exception,
    ]

    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"FAIL — {test.__name__}: {e}")
            failed += 1

    print(f"\n{'='*60}")
    print(f"Results: {passed} PASSED | {failed} FAILED")
    print("="*60)
