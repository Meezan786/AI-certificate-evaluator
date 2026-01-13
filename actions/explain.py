def explain_decision(state):
    """
    Explain the last decision made by the agent, including reasoning and uncertainty.
    Also handles greetings and general queries about capabilities.
    """
    user_message = state["conversation"].last_user_message.lower().strip()

    # Detect greetings
    greetings = [
        "hello",
        "hi",
        "hey",
        "good morning",
        "good afternoon",
        "good evening",
        "greetings",
        "howdy",
    ]
    is_greeting = any(greeting in user_message for greeting in greetings)

    # Detect capability queries
    capability_queries = [
        "what can you do",
        "help",
        "capabilities",
        "what do you do",
        "how does this work",
    ]
    is_capability_query = any(query in user_message for query in capability_queries)

    if is_greeting or is_capability_query or len(user_message) < 15:
        # Welcome message for greetings
        explanation = (
            "👋 **Hello! Welcome to the Agentic Certificate Evaluation AI!**\n\n"
            "I'm a fully intelligent agent that can help you evaluate academic certificates. "
            "I make dynamic decisions based on your requests - no fixed workflows!\n\n"
            "**Here's what I can do for you:**\n\n"
            "📄 **Extract Information**\n"
            "   - Parse and extract data from your certificate\n"
            "   - Identify GPA, degrees, honors, research, leadership, and more\n"
            "   - Provide confidence levels for each extracted field\n\n"
            "⭐ **Set Evaluation Criteria**\n"
            "   - Define what factors matter (GPA, Research, Leadership, etc.)\n"
            "   - Set custom weights for each criterion\n"
            "   - Modify criteria anytime during our conversation\n\n"
            "🎯 **Score Certificates**\n"
            "   - Calculate weighted scores based on your criteria\n"
            "   - Re-score after making changes\n"
            "   - Get detailed breakdowns of scores\n\n"
            "💡 **Explain My Reasoning**\n"
            "   - Understand why I made specific decisions\n"
            "   - See my confidence levels and uncertainties\n"
            "   - Get transparent, explainable AI decisions\n\n"
            "🔄 **User Control**\n"
            "   - Correct my extractions if I make mistakes\n"
            "   - Challenge my assessments\n"
            "   - Reorder steps - I adapt to YOU, not a fixed workflow!\n\n"
            "**To get started, try saying:**\n"
            "• 'Extract information from my certificate'\n"
            "• 'Set evaluation criteria: GPA 40%, Research 30%, Leadership 30%'\n"
            "• 'Score my certificate'\n"
            "• 'Explain your reasoning'\n\n"
            "What would you like to do? 😊"
        )
    else:
        # Standard explanation of last decision
        explanation = (
            "**Decision Explanation:**\n\n"
            f"**Reason for last step:** {state['conversation'].last_reason}\n\n"
            f"**Uncertainty:** {state['conversation'].uncertainty or 'None identified'}\n\n"
            "**Extracted Data:**\n"
        )

        if state["certificate"].extracted_fields:
            for key, value in state["certificate"].extracted_fields.items():
                confidence = state["certificate"].confidence.get(key, 0.0)
                explanation += (
                    f"  - {key}: {value} (confidence: {confidence * 100:.1f}%)\n"
                )
        else:
            explanation += "  - No data extracted yet\n"

        explanation += (
            f"\n**Current Score:** {state['evaluation'].final_score:.1f}/100\n"
        )

        if state["evaluation"].criteria:
            explanation += "\n**Active Criteria:**\n"
            for criterion, weight in state["evaluation"].criteria.items():
                explanation += f"  - {criterion} (weight: {weight})\n"

    state["conversation"].last_agent_message = explanation

    # Update conversation history
    state["conversation"].conversation_history.append(
        {
            "user": state["conversation"].last_user_message,
            "agent": state["conversation"].last_agent_message,
            "action": "explain",
        }
    )

    return state
