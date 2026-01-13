def pause_execution(state):
    """
    Pause execution and await user confirmation before proceeding.
    """
    state["conversation"].last_agent_message = (
        "⏸️ Pausing execution. Awaiting your confirmation.\n\n"
        "Current state:\n"
        f"  - Extracted fields: {len(state['certificate'].extracted_fields)}\n"
        f"  - Active criteria: {len(state['evaluation'].criteria)}\n"
        f"  - Current score: {state['evaluation'].final_score:.1f}/100\n\n"
        "Please confirm to proceed or provide new instructions."
    )
    state["conversation"].pending_confirmation = True

    # Update conversation history
    state["conversation"].conversation_history.append(
        {
            "user": state["conversation"].last_user_message,
            "agent": state["conversation"].last_agent_message,
            "action": "pause",
        }
    )

    return state
