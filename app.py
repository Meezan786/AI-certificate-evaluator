import os
import sys

# Add project directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from dotenv import load_dotenv

from graph.graph import build_graph
from state.certificate_state import CertificateState
from state.conversation_state import ConversationState
from state.evaluation_state import EvaluationState
from state.global_state import GlobalState
from utils.state_manager import StateManager

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Agentic Certificate Evaluator",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better UI
st.markdown(
    """
    <style>
    /* Professional Black & White Theme with Subtle Accents */

    /* Main app background */
    .stApp {
        background-color: #0a0a0a;
        color: #ffffff;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #1a1a1a;
        border-right: 1px solid #2a2a2a;
    }

    [data-testid="stSidebar"] * {
        color: #e0e0e0 !important;
    }

    /* Main header */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #ffffff;
        text-align: center;
        padding: 2rem 0 1rem 0;
        letter-spacing: -0.5px;
        border-bottom: 2px solid #2a2a2a;
        margin-bottom: 1rem;
    }

    .main-header::before {
        content: "🎓 ";
    }

    /* Agent messages - Clean white on dark */
    .agent-message {
        background-color: #1a1a1a;
        color: #ffffff;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border-left: 3px solid #ffffff;
        box-shadow: 0 2px 8px rgba(255, 255, 255, 0.05);
        font-size: 0.95rem;
        line-height: 1.6;
    }

    /* User messages - Subtle gray */
    .user-message {
        background-color: #2a2a2a;
        color: #e0e0e0;
        padding: 1.2rem;
        border-radius: 12px;
        margin: 1rem 0;
        border-left: 3px solid #666666;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        font-size: 0.95rem;
    }

    /* Reasoning box - Minimal accent */
    .reasoning-box {
        background-color: #1a1a1a;
        color: #999999;
        padding: 0.9rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        font-size: 0.85rem;
        border-left: 2px solid #444444;
        font-style: italic;
    }

    /* State box - Professional info display */
    .state-box {
        background-color: #1a1a1a;
        color: #e0e0e0;
        padding: 1.2rem;
        border-radius: 10px;
        margin: 0.8rem 0;
        border: 1px solid #2a2a2a;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
    }

    /* Success box - Clean success indicator */
    .success-box {
        background-color: #0d2818;
        color: #a8e6cf;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 3px solid #4caf50;
        font-size: 0.9rem;
    }

    /* Error box - Clean error indicator */
    .error-box {
        background-color: #2a1515;
        color: #ff9999;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 3px solid #f44336;
        font-size: 0.9rem;
    }

    /* General text styling */
    .stMarkdown, .stText, p, div, span {
        color: #e0e0e0;
    }

    /* Button styling - Professional minimal */
    .stButton button {
        background-color: #ffffff;
        color: #0a0a0a;
        border: none;
        border-radius: 6px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        transition: all 0.2s ease;
        box-shadow: 0 2px 4px rgba(255, 255, 255, 0.1);
    }

    .stButton button:hover {
        background-color: #e0e0e0;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(255, 255, 255, 0.15);
    }

    /* Secondary buttons */
    .stButton button[kind="secondary"] {
        background-color: #2a2a2a;
        color: #ffffff;
        border: 1px solid #444444;
    }

    .stButton button[kind="secondary"]:hover {
        background-color: #333333;
        border-color: #666666;
    }

    /* Input styling - Clean minimal */
    .stTextInput input, .stTextArea textarea, .stChatInput input {
        background-color: #1a1a1a;
        border: 1px solid #2a2a2a;
        border-radius: 8px;
        padding: 0.7rem;
        color: #ffffff;
        transition: all 0.2s ease;
    }

    .stTextInput input:focus, .stTextArea textarea:focus, .stChatInput input:focus {
        border-color: #ffffff;
        box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.1);
        background-color: #1f1f1f;
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #1a1a1a;
        color: #ffffff;
        border: 1px solid #2a2a2a;
        border-radius: 6px;
    }

    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #ffffff;
        font-size: 1.8rem;
    }

    [data-testid="stMetricLabel"] {
        color: #999999;
    }

    /* Progress bars */
    .stProgress > div > div > div {
        background-color: #ffffff;
    }

    /* Dividers */
    hr {
        border-color: #2a2a2a;
    }

    /* Checkbox */
    .stCheckbox label {
        color: #e0e0e0;
    }

    /* Info/Warning/Success messages */
    .stAlert {
        background-color: #1a1a1a;
        border: 1px solid #2a2a2a;
        color: #e0e0e0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# Initialize session state
def init_session_state():
    if "state_manager" not in st.session_state:
        st.session_state.state_manager = StateManager()

    if "graph" not in st.session_state:
        st.session_state.graph = build_graph()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "show_reasoning" not in st.session_state:
        st.session_state.show_reasoning = True

    if "state" not in st.session_state:
        # Initialize empty state
        st.session_state.state = {
            "certificate": CertificateState(),
            "conversation": ConversationState(),
            "evaluation": EvaluationState(),
        }

        # Try to load previous session
        st.session_state.state = st.session_state.state_manager.load_state(
            st.session_state.state
        )

        # If no saved state, load certificate
        if not st.session_state.state["certificate"].raw_text:
            try:
                with open("data/certificate.txt") as f:
                    cert_text = f.read()
                    if cert_text.strip():
                        st.session_state.state["certificate"].raw_text = cert_text
            except FileNotFoundError:
                pass


if hasattr(st, "session_state"):
    init_session_state()


# Header
st.markdown(
    '<div class="main-header">Agentic Certificate Evaluation AI</div>',
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center; color: #999999; font-size: 0.95rem; margin-top: -0.5rem;'>A fully agentic system with dynamic action selection and persistent context</p>",
    unsafe_allow_html=True,
)
st.markdown(
    "<hr style='margin: 1.5rem 0; border-color: #2a2a2a;'>", unsafe_allow_html=True
)

# Sidebar
with st.sidebar:
    st.markdown("### 📊 System State")

    # Certificate State
    with st.expander("📄 Certificate State", expanded=False):
        if st.session_state.state["certificate"].extracted_fields:
            st.metric(
                "Extracted Fields",
                len(st.session_state.state["certificate"].extracted_fields),
            )
            for (
                key,
                value,
            ) in st.session_state.state["certificate"].extracted_fields.items():
                conf = st.session_state.state["certificate"].confidence.get(key, 0.0)
                st.text(f"{key}: {value}")
                st.progress(float(conf), text=f"Confidence: {conf * 100:.1f}%")
        else:
            st.info("No fields extracted yet")

    # Evaluation State
    with st.expander("⭐ Evaluation State", expanded=False):
        if st.session_state.state["evaluation"].criteria:
            st.metric(
                "Final Score",
                f"{st.session_state.state['evaluation'].final_score:.1f}/100",
            )
            st.subheader("Criteria & Weights")
            for criterion, weight in st.session_state.state[
                "evaluation"
            ].criteria.items():
                st.text(f"{criterion}: {weight:.2f}")
                if criterion in st.session_state.state["evaluation"].scores:
                    score = st.session_state.state["evaluation"].scores[criterion]
                    st.progress(score / 100.0, text=f"Score: {score:.1f}")
        else:
            st.info("No criteria set yet")

    # Conversation Stats
    with st.expander("💬 Conversation Stats", expanded=False):
        history_len = len(st.session_state.state["conversation"].conversation_history)
        reasoning_len = len(st.session_state.state["conversation"].reasoning_history)
        st.metric("Total Exchanges", history_len)
        st.metric("Reasoning Steps", reasoning_len)

        if st.session_state.state["conversation"].uncertainty:
            st.warning(
                f"⚠️ Uncertainty: {st.session_state.state['conversation'].uncertainty}"
            )

    # Settings
    st.markdown("---")
    st.subheader("⚙️ Settings")
    st.session_state.show_reasoning = st.checkbox("Show Agent Reasoning", value=True)

    if st.button("🔄 Reset System", type="secondary"):
        st.session_state.state_manager.clear_session()
        st.session_state.state = {
            "certificate": CertificateState(),
            "conversation": ConversationState(),
            "evaluation": EvaluationState(),
        }
        st.session_state.messages = []
        # Reload certificate
        try:
            with open("data/certificate.txt") as f:
                cert_text = f.read()
                if cert_text.strip():
                    st.session_state.state["certificate"].raw_text = cert_text
        except FileNotFoundError:
            pass
        st.rerun()

    # Quick Actions
    st.markdown("---")
    st.subheader("⚡ Quick Actions")
    if st.button("Extract Info", use_container_width=True):
        st.session_state.quick_action = "Extract information from my certificate"
        st.rerun()
    if st.button("Set Criteria", use_container_width=True):
        st.session_state.quick_action = (
            "Set criteria: GPA 40%, Research 30%, Leadership 30%"
        )
        st.rerun()
    if st.button("Score", use_container_width=True):
        st.session_state.quick_action = "Score my certificate"
        st.rerun()
    if st.button("Explain", use_container_width=True):
        st.session_state.quick_action = "Explain your last decision"
        st.rerun()

# Main chat area
st.subheader("💬 Chat with Agent")

# Display chat history
chat_container = st.container()
with chat_container:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(
                f'<div class="user-message">👤 <b>You:</b><br>{msg["content"]}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="agent-message">🤖 <b>Agent:</b><br>{msg["content"]}</div>',
                unsafe_allow_html=True,
            )
            if (
                "reasoning" in msg
                and st.session_state.show_reasoning
                and msg["reasoning"]
            ):
                st.markdown(
                    f'<div class="reasoning-box">💭 <i>Reasoning: {msg["reasoning"]}</i></div>',
                    unsafe_allow_html=True,
                )
            if "action" in msg and msg["action"]:
                st.caption(f"🎯 Action taken: `{msg['action']}`")

# Handle quick actions
if "quick_action" in st.session_state and st.session_state.quick_action:
    user_input = st.session_state.quick_action
    st.session_state.quick_action = None
else:
    user_input = None

# Chat input
col1, col2 = st.columns([6, 1])
with col1:
    user_message = st.chat_input("Type your message here...")
    if user_message:
        user_input = user_message

# Process input
if user_input:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Set user message in state
    st.session_state.state["conversation"].last_user_message = user_input

    # Invoke agent
    with st.spinner("🤔 Agent is thinking..."):
        try:
            st.session_state.state = st.session_state.graph.invoke(
                st.session_state.state
            )

            # Get agent response
            agent_message = st.session_state.state["conversation"].last_agent_message
            agent_reasoning = st.session_state.state["conversation"].last_reason

            # Determine action taken
            action_taken = "unknown"
            if st.session_state.state["conversation"].reasoning_history:
                last_reasoning = st.session_state.state[
                    "conversation"
                ].reasoning_history[-1]
                action_taken = last_reasoning.get("decision", "unknown")

            # Add agent message
            st.session_state.messages.append(
                {
                    "role": "agent",
                    "content": agent_message,
                    "reasoning": agent_reasoning,
                    "action": action_taken,
                }
            )

            # Auto-save state after each turn
            st.session_state.state_manager.save_state(st.session_state.state)

        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            st.session_state.messages.append({"role": "agent", "content": error_msg})

    st.rerun()

# Info boxes at bottom
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
        <div class="state-box">
        <b style="color: #ffffff;">💡 Try These:</b><br><br>
        <span style="color: #cccccc;">
        • Extract information from my certificate<br>
        • Set evaluation criteria<br>
        • Score my certificate<br>
        • Change criteria weights<br>
        • Explain your reasoning
        </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
        <div class="state-box">
        <b style="color: #ffffff;">✨ Agentic Features:</b><br><br>
        <span style="color: #cccccc;">
        • Dynamic action selection<br>
        • Persistent state<br>
        • Non-linear flow<br>
        • User corrections accepted<br>
        • Explainable decisions
        </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    if st.session_state.state["conversation"].conversation_history:
        recent = st.session_state.state["conversation"].conversation_history[-1]
        st.markdown(
            f"""
        <div class="state-box">
        <b style="color: #ffffff;">📝 Last Action:</b><br><br>
        <span style="color: #cccccc;">{recent.get("action", "N/A")}</span>
        </div>
        """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div class="state-box">
            <b style="color: #ffffff;">🚀 Start chatting</b><br>
            <span style="color: #999999; font-size: 0.85rem;">to see the agent in action!</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

# Footer
st.markdown(
    "<hr style='margin: 2rem 0; border-color: #2a2a2a;'>", unsafe_allow_html=True
)
st.markdown(
    "<p style='text-align: center; color: #666666; font-size: 0.85rem;'>Built by MEEZAN using LangChain, LangGraph, and Streamlit | Fully Agentic System</p>",
    unsafe_allow_html=True,
)
