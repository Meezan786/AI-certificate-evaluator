from actions.answer import answer_from_state
from actions.clarify import ask_clarification
from actions.compare import compare_certificates
from actions.explain import explain_decision
from actions.extract import extract_information
from actions.history import show_history
from actions.pause import pause_execution
from actions.score import rescore_certificate
from actions.validate import validate_criteria
from agent.prompts import AGENT_DECISION_PROMPT
from llm.json_utils import safe_json_parse
from llm.llm_client import get_llm

llm = get_llm()


def agent_node(state):
    """
    Main agent decision node that dynamically selects next action based on context.
    This is the core of the agentic system - no predefined workflow.
    """
    # Build decision prompt with full context - EXPLICIT state information
    extracted_count = len(state["certificate"].extracted_fields)
    criteria_count = len(state["evaluation"].criteria)
    history_count = len(state["conversation"].conversation_history)

    decision_prompt = f"""
{AGENT_DECISION_PROMPT}

User Input:
{state["conversation"].last_user_message}

=== CURRENT STATE (CHECK THIS CAREFULLY!) ===

Certificate State:
- Raw Text Available: {bool(state["certificate"].raw_text)}
- Extracted Fields COUNT: {extracted_count}
- Fields: {list(state["certificate"].extracted_fields.keys()) if extracted_count > 0 else "NONE - NO DATA EXTRACTED YET"}
- Sample Data: {dict(list(state["certificate"].extracted_fields.items())[:3]) if extracted_count > 0 else "EMPTY"}

Evaluation State:
- Criteria COUNT: {criteria_count}
- Criteria: {state["evaluation"].criteria if criteria_count > 0 else "NONE - NO CRITERIA SET"}
- Final Score: {state["evaluation"].final_score}

Conversation State:
- History Length: {history_count}
- Recent Context: {state["conversation"].conversation_history[-2:] if history_count > 0 else "NO HISTORY"}

=== CRITICAL DECISION LOGIC ===
- If user asks for info AND extracted_count = 0 → choose "extract_information" (NOT answer_from_state)
- If user asks for info AND extracted_count > 0 → choose "answer_from_state"
- If user asks "show history" → choose "show_history"
- If user asks to score AND criteria_count = 0 → choose "ask_clarification"
- If user asks to score AND criteria_count > 0 → choose "rescore"
"""

    # Get LLM decision with safe parsing
    response = llm.invoke(decision_prompt)
    decision = safe_json_parse(
        response.content,
        fallback={
            "next_action": "explain",
            "reason": "Failed to parse decision, defaulting to explanation",
            "uncertainty": "LLM response was not valid JSON",
        },
    )

    # Store reasoning and uncertainty
    state["conversation"].last_reason = decision.get("reason", "")
    state["conversation"].uncertainty = decision.get("uncertainty", "")

    # Add reasoning to history for explainability
    state["conversation"].reasoning_history.append(
        {
            "decision": decision.get("next_action", ""),
            "reason": state["conversation"].last_reason,
            "uncertainty": state["conversation"].uncertainty,
            "context": f"User said: {state['conversation'].last_user_message}",
        }
    )

    action = decision.get("next_action", "explain")

    # Route to appropriate action - dynamic selection, not workflow
    if action == "answer_from_state":
        state = answer_from_state(state)
    elif action == "show_history":
        state = show_history(state)
    elif action == "extract_information":
        state = extract_information(state)
    elif action == "rescore":
        state = rescore_certificate(state)
    elif action == "validate_criteria":
        state = validate_criteria(state)
    elif action == "ask_clarification":
        state = ask_clarification(state)
    elif action == "compare_certificates":
        state = compare_certificates(state)
    elif action == "pause":
        state = pause_execution(state)
    else:  # Default to explain
        state = explain_decision(state)

    # Add reasoning summary to agent message for better explainability
    reasoning_summary = f"\n💭 [Decision: {action}] {state['conversation'].last_reason}"
    if state["conversation"].uncertainty:
        reasoning_summary += f" | Uncertainty: {state['conversation'].uncertainty}"
    
    # Append to the last agent message
    state["conversation"].last_agent_message += reasoning_summary

    return state
