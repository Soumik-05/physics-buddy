"""
nodes.py — All 8 node functions for PhysicsBuddy LangGraph Agent
Each node reads from CapstoneState, returns only the fields it modifies.
Nodes are designed to be tested in isolation before graph assembly.
"""

import os
import re
from agent.state import CapstoneState
from agent.tools import run_tool

# ── Constants ────────────────────────────────────────────────────────────────
FAITHFULNESS_THRESHOLD = 0.7
MAX_EVAL_RETRIES = 2
SLIDING_WINDOW = 6          # Keep last 6 messages (3 turns)
HELPLINE = "Physics Helpline: +91-1800-PHYSICS (Mon–Sat, 9am–6pm)"

# ── LLM and Embedder (injected at graph.py runtime) ─────────────────────────
# These are set by graph.py after initialisation — not imported here
# to keep nodes testable with mock state dicts.


# ────────────────────────────────────────────────────────────────────────────
# NODE 1 — memory_node
# ────────────────────────────────────────────────────────────────────────────
def memory_node(state: CapstoneState, llm=None, embedder=None, collection=None) -> dict:
    """
    Appends current question to message history.
    Applies sliding window to prevent token overflow.
    Extracts user name if 'my name is' is present in the question.
    """
    messages = state.get("messages", [])
    question = state.get("question", "")

    # Append user message
    messages.append({"role": "user", "content": question})

    # Sliding window — keep last SLIDING_WINDOW messages
    messages = messages[-SLIDING_WINDOW:]

    # Extract user name if present
    user_name = state.get("user_name", "")
    name_match = re.search(r"my name is\s+([A-Za-z]+)", question, re.IGNORECASE)
    if name_match:
        user_name = name_match.group(1).capitalize()

    # Extract topic hint
    topic_asked = state.get("topic_asked", "")
    physics_topics = [
        "newton", "kinematics", "energy", "thermodynamics",
        "electrostatics", "current", "waves", "optics", "gravitation",
        "quantum", "photoelectric", "rotational", "magnetism", "induction"
    ]
    for kw in physics_topics:
        if kw.lower() in question.lower():
            topic_asked = kw.capitalize()
            break

    return {
        "messages": messages,
        "user_name": user_name,
        "topic_asked": topic_asked,
    }


# ────────────────────────────────────────────────────────────────────────────
# NODE 2 — router_node
# ────────────────────────────────────────────────────────────────────────────
def router_node(state: CapstoneState, llm=None, embedder=None, collection=None) -> dict:
    """
    Uses an LLM prompt to decide the route.
    Returns ONE word: 'retrieve', 'tool', or 'memory_only'.
    """
    question = state.get("question", "")
    history_summary = ""
    messages = state.get("messages", [])
    if len(messages) > 1:
        history_summary = f"Recent context: {messages[-2].get('content', '')}"

    router_prompt = f"""You are a routing assistant for a Physics Study Bot.
Given a student's question, reply with EXACTLY one word from: retrieve, tool, memory_only

Rules:
- "retrieve": Question is about a physics concept, formula, law, derivation, topic explanation, or numerical problem from the syllabus. Use this for most physics questions.
- "tool": Question asks for current date/time, a specific arithmetic calculation (e.g. "calculate F = ma with m=5, a=3"), or a study schedule based on today's date.
- "memory_only": Question is a greeting, thanks, casual small talk, or asks about something already answered in the conversation (like "can you repeat that?" or "what did you just say?").

{history_summary}
Student question: {question}

Reply with exactly one word:"""

    try:
        response = llm.invoke(router_prompt)
        raw = response.content.strip().lower().split()[0]
        route = raw if raw in ("retrieve", "tool", "memory_only") else "retrieve"
    except Exception:
        route = "retrieve"

    return {"route": route}


# ────────────────────────────────────────────────────────────────────────────
# NODE 3 — retrieval_node
# ────────────────────────────────────────────────────────────────────────────
def retrieval_node(state: CapstoneState, llm=None, embedder=None, collection=None) -> dict:
    """
    Embeds the question, queries ChromaDB for top 3 chunks.
    Formats results as a context string with [Topic] labels.
    """
    question = state.get("question", "")
    try:
        query_embedding = embedder.encode([question]).tolist()
        results = collection.query(
            query_embeddings=query_embedding,
            n_results=3
        )
        docs = results["documents"][0]
        topics = [meta["topic"] for meta in results["metadatas"][0]]
        context_parts = [f"[{topics[i]}]\n{docs[i]}" for i in range(len(docs))]
        context = "\n\n".join(context_parts)
        return {"retrieved": context, "sources": topics}
    except Exception as e:
        return {"retrieved": "", "sources": [], "tool_result": f"[retrieval error: {str(e)}]"}


# ────────────────────────────────────────────────────────────────────────────
# NODE 4 — skip_retrieval_node
# ────────────────────────────────────────────────────────────────────────────
def skip_retrieval_node(state: CapstoneState, llm=None, embedder=None, collection=None) -> dict:
    """
    Used for memory_only route. Explicitly clears retrieved and sources
    so previous turn's context does not leak into this turn.
    """
    return {"retrieved": "", "sources": []}


# ────────────────────────────────────────────────────────────────────────────
# NODE 5 — tool_node
# ────────────────────────────────────────────────────────────────────────────
def tool_node(state: CapstoneState, llm=None, embedder=None, collection=None) -> dict:
    """
    Decides which tool to call (datetime or calculator) based on the question.
    Always returns a string — never raises an exception.
    """
    question = state.get("question", "").lower()

    # Detect calculator intent
    calc_keywords = ["calculate", "compute", "what is", "solve", "find", "evaluate", "="]
    math_patterns = [r"\d+[\+\-\*\/\^]\d+", r"sqrt", r"sin\(", r"cos\(", r"tan\("]
    is_calc = any(kw in question for kw in calc_keywords) and (
        any(re.search(p, question) for p in math_patterns)
    )

    if is_calc:
        # Extract mathematical expression using LLM or pattern
        expr_match = re.search(r"[\d\.\+\-\*\/\(\)\^\s]+", question)
        expression = expr_match.group().strip() if expr_match else question
        result = run_tool("calculator", expression)
    else:
        result = run_tool("datetime", "")

    return {"tool_result": result, "retrieved": "", "sources": []}


# ────────────────────────────────────────────────────────────────────────────
# NODE 6 — answer_node
# ────────────────────────────────────────────────────────────────────────────
def answer_node(state: CapstoneState, llm=None, embedder=None, collection=None) -> dict:
    """
    Builds system prompt with strict grounding rule.
    Generates answer from retrieved context or tool result.
    Handles eval_retries escalation instruction.
    """
    question = state.get("question", "")
    retrieved = state.get("retrieved", "")
    tool_result = state.get("tool_result", "")
    messages = state.get("messages", [])
    user_name = state.get("user_name", "")
    eval_retries = state.get("eval_retries", 0)

    student_ref = f"the student (name: {user_name})" if user_name else "the student"

    retry_instruction = ""
    if eval_retries > 0:
        retry_instruction = (
            f"\n[RETRY {eval_retries}]: Your previous answer was not faithful enough to the context. "
            "This time, use ONLY the provided knowledge base context. Do NOT add any information "
            "from your general training knowledge."
        )

    knowledge_section = ""
    if retrieved:
        knowledge_section = f"\n\nKNOWLEDGE BASE CONTEXT:\n{retrieved}"
    if tool_result:
        knowledge_section += f"\n\nTOOL RESULT:\n{tool_result}"

    system_prompt = f"""You are PhysicsBuddy, a friendly and knowledgeable Physics Study Assistant for B.Tech students.
You are helping {student_ref}.

STRICT RULES:
1. Answer ONLY using information from the KNOWLEDGE BASE CONTEXT or TOOL RESULT provided below.
2. If the answer is not in the context, say clearly: "I don't have information about that in my knowledge base. Please refer to your textbook or ask your professor. {HELPLINE}"
3. NEVER give medical, legal, or financial advice.
4. NEVER hallucinate formulas, constants, or facts not present in the context.
5. Keep answers clear, structured, and exam-focused for B.Tech students.
6. Write all maths in plain text (e.g. F = m × a, sqrt(144) = 12). NEVER use LaTeX, backslashes, \\( \\), \\[ \\] or \\boxed.
7. If asked for derivations or proofs not in the KB, admit it and guide the student to their syllabus material.{retry_instruction}{knowledge_section}
Conversation history (most recent):
{chr(10).join([f"{m['role'].upper()}: {m['content']}" for m in messages[-4:]])}

Answer the student's latest question clearly and helpfully."""

    try:
        response = llm.invoke(system_prompt)
        answer = response.content.strip()
    except Exception as e:
        answer = f"I encountered a technical issue. Please try again. {HELPLINE} [Error: {str(e)}]"

    return {"answer": answer}


# ────────────────────────────────────────────────────────────────────────────
# NODE 7 — eval_node
# ────────────────────────────────────────────────────────────────────────────
def eval_node(state: CapstoneState, llm=None, embedder=None, collection=None) -> dict:
    """
    LLM-based faithfulness evaluation.
    Scores answer 0.0–1.0 based on groundedness in retrieved context.
    Skips check if retrieved is empty (tool or memory_only route).
    Increments eval_retries counter.
    """
    retrieved = state.get("retrieved", "")
    answer = state.get("answer", "")
    eval_retries = state.get("eval_retries", 0)

    # Skip faithfulness check if no retrieved context (tool/memory_only route)
    if not retrieved.strip():
        return {"faithfulness": 1.0, "eval_retries": eval_retries}

    eval_prompt = f"""You are an evaluator checking if an AI answer is FAITHFUL to the provided context.

CONTEXT:
{retrieved}

ANSWER:
{answer}

Rate faithfulness from 0.0 to 1.0:
- 1.0: Every claim in the answer is directly supported by the context.
- 0.7–0.9: Most claims supported; minor additions from common knowledge.
- 0.4–0.6: Some claims from outside the context.
- 0.0–0.3: Answer mostly ignores or contradicts the context.

Reply with ONLY a decimal number between 0.0 and 1.0. Nothing else."""

    try:
        response = llm.invoke(eval_prompt)
        score_text = response.content.strip().split()[0]
        score = float(score_text)
        score = max(0.0, min(1.0, score))
    except Exception:
        score = 1.0  # Default to passing if eval fails

    return {"faithfulness": score, "eval_retries": eval_retries + 1}


# ────────────────────────────────────────────────────────────────────────────
# NODE 8 — save_node
# ────────────────────────────────────────────────────────────────────────────
def save_node(state: CapstoneState, llm=None, embedder=None, collection=None) -> dict:
    """
    Appends the final assistant answer to the conversation history.
    Resets eval_retries to 0 for the next turn.
    """
    messages = state.get("messages", [])
    answer = state.get("answer", "")
    sources = state.get("sources", [])

    source_note = f"\n\n📚 Sources: {', '.join(sources)}" if sources else ""
    messages.append({"role": "assistant", "content": answer + source_note})

    return {
        "messages": messages,
        "eval_retries": 0,  # Reset for next question
        "tool_result": "",  # Clear tool result for next turn
    }
