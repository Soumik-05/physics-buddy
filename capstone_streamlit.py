"""
capstone_streamlit.py — Streamlit UI for PhysicsBuddy Agent
Part 7 of the capstone process.

Run with: streamlit run capstone_streamlit.py

Key design decisions:
- @st.cache_resource prevents LLM/embedder/ChromaDB reloading on every rerun
- st.session_state stores messages and thread_id
- 'New conversation' button resets thread_id
- Memory persists across multiple turns within one session
"""

import streamlit as st
import uuid
import os

# ── Page config must be first Streamlit call ─────────────────────────────────
st.set_page_config(
    page_title="PhysicsBuddy — B.Tech Study Assistant",
    page_icon="⚛️",
    layout="wide"
)


# ── Cache all expensive resources (prevents reloading on every user action) ──
@st.cache_resource
def load_agent():
    """
    Initialises LLM, embedder, ChromaDB, and compiles graph.
    Called ONCE and cached — reused for all subsequent interactions.
    """
    from agent.graph import build_graph
    app, llm, embedder, collection = build_graph()
    return app, llm, embedder, collection


# ── Session state initialisation ─────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "agent_loaded" not in st.session_state:
    st.session_state.agent_loaded = False


# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("⚛️ PhysicsBuddy")
    st.markdown("**AI Study Assistant for B.Tech Physics**")
    st.markdown("---")
    st.markdown("### 📚 Topics Covered")
    topics = [
        "Newton's Laws of Motion",
        "Kinematics & Equations of Motion",
        "Work, Energy, and Power",
        "Laws of Thermodynamics",
        "Electrostatics",
        "Current Electricity & Circuits",
        "Waves and Sound",
        "Optics (Reflection & Refraction)",
        "Gravitation & Orbital Motion",
        "Modern Physics & Quantum Basics",
        "Rotational Motion",
        "Magnetism & EMI",
    ]
    for t in topics:
        st.markdown(f"• {t}")
    st.markdown("---")

    # New conversation resets thread_id
    if st.button("🔄 New Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.thread_id = str(uuid.uuid4())
        st.rerun()

    st.markdown("---")
    st.markdown(f"**Session ID:** `{st.session_state.thread_id[:8]}...`")
    st.markdown("*Memory persists within this session.*")
    st.markdown("---")
    st.caption("PhysicsBuddy v1.0 | Agentic AI Course 2026")
    st.caption("⚠️ Does not provide medical/legal advice.")


# ── Main UI ───────────────────────────────────────────────────────────────────
st.title("⚛️ PhysicsBuddy — B.Tech Physics Study Assistant")
st.markdown(
    "Ask me anything about your B.Tech Physics syllabus — concepts, formulas, "
    "numericals, or exam tips. I remember our conversation throughout this session!"
)

# Load agent (cached)
with st.spinner("Loading PhysicsBuddy agent..."):
    try:
        app, llm, embedder, collection = load_agent()
        if not st.session_state.agent_loaded:
            st.session_state.agent_loaded = True
    except Exception as e:
        st.error(f"Failed to load agent: {e}. Please check your GROQ_API_KEY.")
        st.stop()

# Display conversation history
for msg in st.session_state.messages:
    role = msg["role"]
    with st.chat_message(role, avatar="🧑‍🎓" if role == "user" else "⚛️"):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Ask a physics question... (e.g. 'Explain Newton's second law')"):

    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑‍🎓"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant", avatar="⚛️"):
        with st.spinner("Thinking..."):
            try:
                from agent.graph import ask as agent_ask
                config = {"configurable": {"thread_id": st.session_state.thread_id}}

                from agent.state import CapstoneState
                initial_state: CapstoneState = {
                    "question": prompt,
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
                answer = result.get("answer", "I could not generate a response. Please try again.")
                sources = result.get("sources", [])
                route = result.get("route", "")
                faith = result.get("faithfulness", 0.0)

                                # Format response
                response_text = answer
                if sources:
                    response_text += f"\n\n---\n📚 **Sources:** {', '.join(sources)}"

                response_text = (response_text
                    .replace("\\[", "$$").replace("\\]", "$$")
                    .replace("\\(", "$").replace("\\)", "$"))

                st.markdown(response_text)
                
                # Debug info in expander
                with st.expander("🔍 Agent Trace", expanded=False):
                    st.markdown(f"**Route:** `{route}`")
                    st.markdown(f"**Faithfulness Score:** `{faith:.2f}`")
                    st.markdown(f"**Eval Retries:** `{result.get('eval_retries', 0)}`")
                    if result.get("retrieved"):
                        st.markdown("**Retrieved Context (first 300 chars):**")
                        st.code(result["retrieved"][:300] + "...")

                st.session_state.messages.append({"role": "assistant", "content": response_text})

            except Exception as e:
                err_msg = f"Error generating response: {str(e)}"
                st.error(err_msg)
                st.session_state.messages.append({"role": "assistant", "content": err_msg})
