"""
graph.py — LangGraph StateGraph assembly for PhysicsBuddy Agent
Follows the 8-step graph assembly process from the capstone instructions.
"""

import os
from functools import partial

from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from sentence_transformers import SentenceTransformer
import chromadb

from agent.state import CapstoneState
from agent.knowledge_base import PHYSICS_DOCUMENTS
from agent.nodes import (
    memory_node, router_node, retrieval_node, skip_retrieval_node,
    tool_node, answer_node, eval_node, save_node,
    FAITHFULNESS_THRESHOLD, MAX_EVAL_RETRIES
)

# ── Step 1: Initialise LLM ───────────────────────────────────────────────────
def init_llm():
    return ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.1,
    api_key=os.environ.get("GROQ_API_KEY", "")
)

# ── Step 2: Initialise Embedder ──────────────────────────────────────────────
def init_embedder():
    return SentenceTransformer("all-MiniLM-L6-v2")

# ── Step 3: Build ChromaDB Collection ───────────────────────────────────────
def build_collection(embedder):
    """
    Builds an in-memory ChromaDB collection with all 12 physics documents.
    Runs a retrieval test before returning to verify KB is working.
    """
    client = chromadb.Client()
    collection = client.create_collection(
        name="physics_kb",
        metadata={"hnsw:space": "cosine"}
    )

    texts = [doc["text"] for doc in PHYSICS_DOCUMENTS]
    embeddings = embedder.encode(texts).tolist()   # NumPy → list (required by ChromaDB)
    ids = [doc["id"] for doc in PHYSICS_DOCUMENTS]
    metadatas = [{"topic": doc["topic"]} for doc in PHYSICS_DOCUMENTS]

    collection.add(
        documents=texts,
        embeddings=embeddings,
        ids=ids,
        metadatas=metadatas
    )

    # ── Retrieval verification test (MUST pass before graph assembly) ────────
    test_query = "What is Newton's second law of motion?"
    test_embedding = embedder.encode([test_query]).tolist()
    test_result = collection.query(query_embeddings=test_embedding, n_results=2)
    retrieved_topics = [m["topic"] for m in test_result["metadatas"][0]]
    print(f"[KB VERIFICATION] Query: '{test_query}'")
    print(f"[KB VERIFICATION] Retrieved topics: {retrieved_topics}")
    assert any("Newton" in t for t in retrieved_topics), "KB verification FAILED — check documents"
    print("[KB VERIFICATION] PASSED ✓")

    return collection

# ── Step 4: Routing Functions (standalone — required by add_conditional_edges) ──

def route_decision(state: CapstoneState) -> str:
    """
    Reads state.route and returns the next node name.
    Called by add_conditional_edges after router_node.
    Standalone function — independently unit testable.
    """
    route = state.get("route", "retrieve")
    if route == "tool":
        return "tool"
    elif route == "memory_only":
        return "skip"
    else:
        return "retrieve"


def eval_decision(state: CapstoneState) -> str:
    """
    Reads faithfulness and eval_retries to decide whether to retry or save.
    Returns 'answer' (retry) or 'save' (accept and persist).
    Standalone function — independently unit testable.
    """
    faithfulness = state.get("faithfulness", 1.0)
    eval_retries = state.get("eval_retries", 0)

    if faithfulness < FAITHFULNESS_THRESHOLD and eval_retries < MAX_EVAL_RETRIES:
        return "answer"   # Retry
    else:
        return "save"     # Accept (either passed or max retries reached)


# ── Step 5: Build the Compiled Graph ─────────────────────────────────────────

def build_graph(llm=None, embedder=None, collection=None):
    """
    Assembles and compiles the full LangGraph StateGraph.
    Returns the compiled app with MemorySaver checkpointer.
    """
    if llm is None:
        llm = init_llm()
    if embedder is None:
        embedder = init_embedder()
    if collection is None:
        collection = build_collection(embedder)

    # Wrap nodes with dependencies using partial (keeps node signature clean)
    def wrap(fn):
        return partial(fn, llm=llm, embedder=embedder, collection=collection)

    # Instantiate StateGraph with CapstoneState
    graph = StateGraph(CapstoneState)

    # Add all 8 nodes
    graph.add_node("memory",   wrap(memory_node))
    graph.add_node("router",   wrap(router_node))
    graph.add_node("retrieve", wrap(retrieval_node))
    graph.add_node("skip",     wrap(skip_retrieval_node))
    graph.add_node("tool",     wrap(tool_node))
    graph.add_node("answer",   wrap(answer_node))
    graph.add_node("eval",     wrap(eval_node))
    graph.add_node("save",     wrap(save_node))

    # Set entry point
    graph.set_entry_point("memory")

    # Fixed edges
    graph.add_edge("memory",   "router")
    graph.add_edge("retrieve", "answer")
    graph.add_edge("skip",     "answer")
    graph.add_edge("tool",     "answer")
    graph.add_edge("answer",   "eval")
    graph.add_edge("save",     END)         # Critical — missing this causes compile error

    # Conditional edges
    graph.add_conditional_edges("router", route_decision, {
        "retrieve": "retrieve",
        "skip":     "skip",
        "tool":     "tool",
    })
    graph.add_conditional_edges("eval", eval_decision, {
        "answer": "answer",   # Retry loop
        "save":   "save",     # Accept and persist
    })

    # Compile with MemorySaver for multi-turn thread_id memory
    app = graph.compile(checkpointer=MemorySaver())
    print("Graph compiled successfully ✓")
    return app, llm, embedder, collection


# ── Helper: ask() function for testing ───────────────────────────────────────
def ask(app, question: str, thread_id: str) -> dict:
    """
    Invokes the graph with a question and thread_id.
    Returns the full final state dict.
    """
    config = {"configurable": {"thread_id": thread_id}}
    initial_state: CapstoneState = {
        "question": question,
        "messages": [],
        "route": "",
        "retrieved": "",
        "sources": [],
        "tool_result": "",
        "answer": "",
        "faithfulness": 0.0,
        "eval_retries": 0,
        "user_name": "",
        "topic_asked": "",
    }
    result = app.invoke(initial_state, config=config)
    return result
