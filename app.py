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
    /* Modern color scheme with good contrast */
    .stApp {
        background-color: #ffffff;
        color: #2c3e50;
    }

    /* Main header */
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2c3e50;
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    /* Agent messages - blue theme */
    .agent-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #ffffff;
        padding: 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        border-left: 4px solid #4a90e2;
        box-shadow: 0 2px 10px rgba(102, 126, 234, 0.2);
    }

    /* User messages - gray theme */
    .user-message {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        color: #2c3e50;
        padding: 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        border-left: 4px solid #6c757d;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    }

    /* Reasoning box - yellow/orange theme */
    .reasoning-box {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        color: #856404;
        padding: 0.8rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        font-size: 0.9rem;
        border-left: 3px solid #ffc107;
        box-shadow: 0 2px 8px rgba(255, 193, 7, 0.2);
    }

    /* State box - light blue theme */
    .state-box {
        background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
        color: #0c5460;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #17a2b8;
        box-shadow: 0 2px 8px rgba(23, 162, 184, 0.2);
    }

    /* Success box - green theme */
    .success-box {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        color: #155724;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #28a745;
        box-shadow: 0 2px 8px rgba(40, 167, 69, 0.2);
    }

    /* Error box - red theme */
    .error-box {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        color: #721c24;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #dc3545;
        box-shadow: 0 2px 8px rgba(220, 53, 69, 0.2);
    }

    /* Sidebar styling */
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
        color: #2c3e50;
    }

    /* General text improvements */
    .stMarkdown, .stText, p, div, span {
        color: #2c3e50;
    }

    /* Button styling */
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }

    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }

    /* Input styling */
    .stTextInput input, .stTextArea textarea {
        border: 2px solid #e9ecef;
        border-radius: 8px;
        padding: 0.5rem;
        color: #2c3e50;
    }

    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
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
    '<div class="main-header">🎓 Agentic Certificate Evaluation AI</div>',
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center; color: #666;'>A fully agentic system with dynamic action selection and persistent context</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("📊 System State")

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
    st.info(
        """
    **💡 Try These:**
    - Extract information from my certificate
    - Set evaluation criteria
    - Score my certificate
    - Change criteria weights
    - Explain your reasoning
    """
    )

with col2:
    st.success(
        """
    **✨ Agentic Features:**
    - Dynamic action selection
    - Persistent state
    - Non-linear flow
    - User corrections accepted
    - Explainable decisions
    """
    )

with col3:
    if st.session_state.state["conversation"].conversation_history:
        recent = st.session_state.state["conversation"].conversation_history[-1]
        st.markdown(
            f"""
        <div class="state-box">
        <b>📝 Last Action:</b><br>
        {recent.get("action", "N/A")}
        </div>
        """,
            unsafe_allow_html=True,
        )
    else:
        st.warning("**🚀 Start chatting** to see the agent in action!")

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #999; font-size: 0.9rem;'>Built with ❤️ using LangChain, LangGraph, and Streamlit | Fully Agentic System</p>",
    unsafe_allow_html=True,
)
