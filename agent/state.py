"""
state.py — CapstoneState TypedDict for PhysicsBuddy Agent
Designed BEFORE any node function is written, as required.
Every field that any node reads or writes is declared here.
"""

from typing import TypedDict, List


class CapstoneState(TypedDict):
    # Core fields (mandatory for all capstone agents)
    question: str                   # Current user question
    messages: List[dict]            # Full sliding-window conversation history
    route: str                      # Router decision: 'retrieve' | 'tool' | 'memory_only'
    retrieved: str                  # Formatted retrieved context string
    sources: List[str]              # List of topic names retrieved
    tool_result: str                # Output from tool_node (datetime / calculator)
    answer: str                     # Final LLM-generated answer
    faithfulness: float             # RAGAS-style faithfulness score 0.0–1.0
    eval_retries: int               # Number of eval retries so far

    # Domain-specific fields for PhysicsBuddy
    user_name: str                  # Extracted student name (if shared)
    topic_asked: str                # Physics topic extracted from question
