def explain_decision(state):
    """
    Explain the last decision made by the agent, including reasoning and uncertainty.
    Context-aware: Explains WHY the previous action was chosen based on conversation history.
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

    # Detect farewells
    farewells = [
        "bye",
        "goodbye",
        "see you",
        "farewell",
        "take care",
        "later",
        "gotta go",
        "have to go",
    ]
    is_farewell = any(farewell in user_message for farewell in farewells)

    # Detect gratitude/acknowledgment
    gratitude = [
        "thank you",
        "thanks",
        "appreciate",
        "got it",
        "understood",
        "ok thanks",
        "okay thanks",
        "cool thanks",
    ]
    is_gratitude = any(thanks in user_message for thanks in gratitude)

    # Detect capability queries
    capability_queries = [
        "what can you do",
        "help",
        "capabilities",
        "what do you do",
        "how does this work",
    ]
    is_capability_query = any(query in user_message for query in capability_queries)

    # Detect if user is asking to explain PREVIOUS action
    asking_about_previous = any(
        phrase in user_message
        for phrase in [
            "explain your last",
            "explain the last",
            "why did you",
            "explain your previous",
            "explain that",
        ]
    )

    # If asking about previous action, explain it from history
    if asking_about_previous and len(state["conversation"].reasoning_history) >= 2:
        # Get the PREVIOUS reasoning (not current one which is this explain action)
        # reasoning_history[-1] = current explain action's reasoning (added in agent.py)
        # reasoning_history[-2] = the action we want to explain
        previous_reasoning = state["conversation"].reasoning_history[-2]

        # Get the exchange that triggered that previous action
        # conversation_history[-1] = the previous action's exchange (hasn't added current explain yet)
        # This gives us the user message that triggered the action we're explaining
        previous_exchange = None
        if len(state["conversation"].conversation_history) >= 1:
            # The previous action's user message is at -1 position
            previous_exchange = state["conversation"].conversation_history[-1]

        if previous_reasoning and previous_exchange:
            prev_action = previous_reasoning.get("decision", "unknown")
            prev_reason = previous_reasoning.get("reason", "No reason recorded")
            prev_user_msg = previous_exchange.get("user", "")
            prev_uncertainty = previous_reasoning.get("uncertainty", "None")

            explanation = (
                f"📋 **Explanation of My Last Action:**\n\n"
                f"**Action I Took:** `{prev_action}`\n\n"
                f'**What You Said:** "{prev_user_msg}"\n\n'
                f"**Why I Chose This Action:**\n"
                f"{prev_reason}\n\n"
                f"**Uncertainty Level:** {prev_uncertainty if prev_uncertainty else 'None - I was confident in this decision'}\n\n"
            )

            # Add context-specific elaboration
            if prev_action == "explain":
                explanation += (
                    "**Detailed Logic:**\n"
                    "I detected that your message was a greeting or general question. "
                    "For such inputs, the 'explain' action is most appropriate because it:\n"
                    "  • Provides a friendly welcome to new users\n"
                    "  • Explains my capabilities and how to use me\n"
                    "  • Sets the foundation for our conversation\n"
                    "  • Doesn't make assumptions about what you want to do\n\n"
                    "This demonstrates agentic intelligence - adapting my response to the conversational context rather than following a fixed script."
                )
            elif prev_action == "extract_information":
                explanation += (
                    "**Detailed Logic:**\n"
                    "I detected that you wanted certificate data extraction. I chose this action because:\n"
                    "  • You explicitly requested extraction\n"
                    "  • This is a prerequisite for evaluation\n"
                    "  • Extracting first allows me to provide accurate information later\n\n"
                    "If data was already extracted, I showed cached data for efficiency (treating previous outputs as living context)."
                )
            elif prev_action == "rescore":
                explanation += (
                    "**Detailed Logic:**\n"
                    "I detected that you wanted scoring/evaluation. I chose this action because:\n"
                    "  • Evaluation criteria were already set in state\n"
                    "  • Certificate data was already extracted\n"
                    "  • All prerequisites were met for calculating scores\n\n"
                    "The scoring used weighted criteria to calculate the final score based on your specified factors."
                )
            elif prev_action == "validate_criteria":
                explanation += (
                    "**Detailed Logic:**\n"
                    "I detected that you wanted to set or modify evaluation criteria. I chose this action because:\n"
                    "  • You specified what factors to evaluate\n"
                    "  • You may have provided weights/percentages\n"
                    "  • This establishes the framework for scoring\n\n"
                    "Setting criteria before scoring ensures the evaluation matches your priorities."
                )
            elif prev_action == "answer_from_state":
                explanation += (
                    "**Detailed Logic:**\n"
                    "I detected that you asked a question about information that already exists in state. I chose this action because:\n"
                    "  • The requested data was already extracted\n"
                    "  • No need to re-extract (efficient and treats state as living context)\n"
                    "  • Answering from state is faster and more reliable\n\n"
                    "This demonstrates 'treating previous outputs as living context' - a key agentic principle."
                )
            elif prev_action == "ask_clarification":
                explanation += (
                    "**Detailed Logic:**\n"
                    "I detected that something was unclear or missing. I chose this action because:\n"
                    "  • Your request needed additional information to fulfill\n"
                    "  • OR missing data (e.g., no criteria set when you wanted scoring)\n"
                    "  • Asking for clarification ensures I understand correctly\n\n"
                    "This shows intelligent interaction - I don't make assumptions when uncertain."
                )
            else:
                explanation += (
                    f"**Detailed Logic:**\n"
                    f"Based on your message and the current state, the '{prev_action}' action "
                    f"was the most contextually appropriate response. This decision was made dynamically "
                    f"by analyzing your intent, the current conversation state, and available actions."
                )

            state["conversation"].last_agent_message = explanation

        else:
            # Fallback if no previous reasoning
            state["conversation"].last_agent_message = (
                "⚠️ I don't have detailed information about my last action.\n\n"
                "This is likely because we just started the conversation. "
                "Try asking me to do something, then ask me to explain it!"
            )

    elif is_farewell:
        # Farewell message
        explanation = (
            "👋 **Goodbye!**\n\n"
            "Thank you for using the Agentic Certificate Evaluation AI!\n\n"
            "**Session Summary:**\n"
        )

        # Add session stats if available
        if state["conversation"].conversation_history:
            explanation += f"  • Total exchanges: {len(state['conversation'].conversation_history)}\n"
        if state["certificate"].extracted_fields:
            explanation += (
                f"  • Extracted fields: {len(state['certificate'].extracted_fields)}\n"
            )
        if state["evaluation"].criteria:
            explanation += (
                f"  • Evaluation criteria set: {len(state['evaluation'].criteria)}\n"
            )
        if state["evaluation"].final_score > 0:
            explanation += (
                f"  • Final score: {state['evaluation'].final_score:.1f}/100\n"
            )

        explanation += (
            "\n✓ All your data has been saved and will be available when you return.\n\n"
            "Feel free to come back anytime to continue evaluating certificates! 😊"
        )
        state["conversation"].last_agent_message = explanation

    elif is_gratitude:
        # Gratitude/acknowledgment response
        explanation = (
            "😊 **You're welcome!**\n\n"
            "I'm glad I could help! If you need anything else, feel free to ask:\n\n"
            "• Extract more information\n"
            "• Modify evaluation criteria\n"
            "• Re-score the certificate\n"
            "• Explain any decisions\n"
            "• Compare with other certificates\n\n"
            "Or simply say 'bye' when you're done. I'm here to assist! 🎓"
        )
        state["conversation"].last_agent_message = explanation

    elif is_greeting or is_capability_query or len(user_message) < 20:
        # Welcome message for greetings or general questions
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
        state["conversation"].last_agent_message = explanation

    else:
        # Standard explanation of current state and last decision
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
