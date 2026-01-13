def compare_certificates(state):
    """
    Compare certificates. Handles single certificate mode with comparison intent.
    In a full multi-certificate system, this would compare multiple loaded certificates.
    """
    # Check if user provided comparison data in message
    user_message = state["conversation"].last_user_message.lower()
    
    if "with" in user_message or "vs" in user_message or "versus" in user_message:
        # User is trying to compare with something
        state["conversation"].last_agent_message = (
            "📊 Certificate comparison requested.\n\n"
            "I detected a comparison request, but this system is currently configured "
            "for single-certificate evaluation.\n\n"
            "To enable multi-certificate comparison:\n"
            "  1. Load additional certificate data into the system\n"
            "  2. Define comparison criteria (e.g., GPA ranges, institution tiers)\n"
            "  3. Specify what aspects to compare (academic performance, honors, etc.)\n\n"
            "For this certificate, I can provide detailed evaluation against "
            "standard benchmarks or custom criteria you specify."
        )
    else:
        # General comparison inquiry
        state["conversation"].last_agent_message = (
            "📊 Certificate comparison capabilities:\n\n"
            "Current system: Single certificate evaluation mode\n\n"
            "Available comparison features:\n"
            "  • Evaluate against standard academic benchmarks\n"
            "  • Compare to industry averages\n"
            "  • Assess competitiveness for graduate programs\n"
            "  • Benchmark against peer institutions\n\n"
            "What specific comparison would you like me to perform?"
        )

    # Update conversation history
    state["conversation"].conversation_history.append(
        {
            "user": state["conversation"].last_user_message,
            "agent": state["conversation"].last_agent_message,
            "action": "compare_certificates",
        }
    )

    return state
