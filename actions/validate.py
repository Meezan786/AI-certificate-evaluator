from llm.json_utils import safe_json_parse
from llm.llm_client import get_llm

llm = get_llm()


def validate_criteria(state):
    """
    Validate, set, or modify evaluation criteria based on user input.
    Extracts criteria and weights from conversation context.
    """
    prompt = f"""
You are analyzing a user request about evaluation criteria for a certificate.

User Message: {state["conversation"].last_user_message}

Current Criteria: {state["evaluation"].criteria}

Task: Extract evaluation criteria and their weights from the user's message.
Common criteria include: GPA, Institution Reputation, Degree Type, Field of Study,
Graduation Year, Honors/Distinctions, etc.

If user specifies weights, use them. Otherwise assign equal weights.
Weights should sum to 1.0 for proper weighting.

Return STRICT JSON:
{{
  "criteria": {{
    "criterion_name": weight_value
  }},
  "validation_message": "Brief message about what criteria were set/changed"
}}

Example:
{{
  "criteria": {{
    "GPA": 0.4,
    "Institution": 0.3,
    "Degree Type": 0.3
  }},
  "validation_message": "Set 3 evaluation criteria with weights"
}}
"""

    result = llm.invoke(prompt)
    data = safe_json_parse(
        result.content,
        fallback={"criteria": {}, "validation_message": "Failed to parse criteria"},
    )

    new_criteria = data.get("criteria", {})
    validation_msg = data.get("validation_message", "Criteria updated")

    # Update evaluation state with new criteria
    if new_criteria:
        state["evaluation"].criteria = new_criteria

        criteria_list = "\n".join(
            [f"  - {k}: weight={v:.2f}" for k, v in new_criteria.items()]
        )

        state["conversation"].last_agent_message = (
            f"✓ {validation_msg}\n\n"
            f"**Active Evaluation Criteria:**\n{criteria_list}\n\n"
            f"The certificate will now be evaluated based on these criteria.\n"
            f"You can modify criteria anytime or ask me to re-score the certificate."
        )
    else:
        state["conversation"].last_agent_message = (
            "⚠️ Could not extract evaluation criteria from your message.\n\n"
            "Please specify criteria more clearly, for example:\n"
            "  - 'Evaluate based on GPA, Institution, and Degree'\n"
            "  - 'Use 40% weight for GPA, 30% for Institution, 30% for Field'\n"
            "  - 'Change criteria to prioritize Honors and Research'"
        )

    # Update conversation history
    state["conversation"].conversation_history.append(
        {
            "user": state["conversation"].last_user_message,
            "agent": state["conversation"].last_agent_message,
            "action": "validate_criteria",
        }
    )

    return state
