def ask_clarification(state):
    """
    Ask for clarification when information is unclear or missing.
    Handles missing criteria, unclear data, and low confidence fields.
    """
    # Check if this is about missing criteria for scoring
    user_message = state["conversation"].last_user_message.lower()
    wants_score = any(
        word in user_message
        for word in ["score", "calculate", "rate", "evaluate", "scoring"]
    )

    if wants_score and not state["evaluation"].criteria:
        # User wants to score but no criteria set
        msg = (
            "⚠️ **No evaluation criteria set yet!**\n\n"
            "To calculate scores, I need to know what criteria to use.\n\n"
            "**Please tell me what factors to evaluate, for example:**\n"
            "• 'Set criteria to GPA 40%, Research 30%, Leadership 30%'\n"
            "• 'Evaluate based on GPA, Institution, and Degree'\n"
            "• 'Use GPA and Research as criteria'\n\n"
            "You can specify weights (percentages) or I'll distribute them equally.\n\n"
            "What criteria would you like to use? 🎯"
        )
    else:
        # General unclear information
        msg = (
            "⚠️ Some information is unclear or missing.\n\n"
            "Please confirm or provide more details:\n"
        )

        # Identify what's unclear
        if state["conversation"].uncertainty:
            msg += f"\nUncertainty detected: {state['conversation'].uncertainty}\n"

        # Check for low confidence fields - safely handle confidence values
        low_confidence_fields = []
        if state["certificate"].confidence:
            for k, v in state["certificate"].confidence.items():
                try:
                    # Ensure v is a float
                    if isinstance(v, (int, float)):
                        conf_value = float(v)
                        if conf_value < 0.7:
                            low_confidence_fields.append(
                                f"{k} ({conf_value * 100:.1f}% confidence)"
                            )
                except (ValueError, TypeError):
                    # Skip if we can't convert to float
                    continue

        if low_confidence_fields:
            msg += "\nFields with low confidence:\n"
            for field in low_confidence_fields:
                msg += f"  - {field}\n"

        # General tip if no specific issue identified
        if not state["conversation"].uncertainty and not low_confidence_fields:
            msg += "\n💡 Tip: Try being more specific about what you'd like me to do.\n"

    state["conversation"].last_agent_message = msg
    state["conversation"].pending_confirmation = True

    # Update conversation history
    state["conversation"].conversation_history.append(
        {
            "user": state["conversation"].last_user_message,
            "agent": state["conversation"].last_agent_message,
            "action": "ask_clarification",
        }
    )

    return state
