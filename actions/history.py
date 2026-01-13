def show_history(state):
    """
    Display the full conversation history with detailed information.
    Shows all exchanges, actions taken, and reasoning trail.
    """
    conversation_history = state["conversation"].conversation_history
    reasoning_history = state["conversation"].reasoning_history

    if not conversation_history:
        state["conversation"].last_agent_message = (
            "📜 **Conversation History**\n\n"
            "No conversation history yet. This is our first interaction!\n\n"
            "Start by saying:\n"
            "• 'Extract information from my certificate'\n"
            "• 'Set evaluation criteria'\n"
            "• 'Score my certificate'\n"
        )
    else:
        # Build detailed history response
        response = (
            f"📜 **Conversation History ({len(conversation_history)} exchanges)**\n\n"
        )
        response += "=" * 70 + "\n\n"

        for i, exchange in enumerate(conversation_history, 1):
            user_msg = exchange.get("user", "")
            agent_msg = exchange.get("agent", "")
            action = exchange.get("action", "unknown")

            # Truncate long messages for readability
            user_preview = user_msg[:100] + "..." if len(user_msg) > 100 else user_msg
            agent_preview = (
                agent_msg[:200] + "..." if len(agent_msg) > 200 else agent_msg
            )

            response += f"**[{i}] Turn {i}**\n"
            response += f"🎯 Action: `{action}`\n\n"
            response += f"👤 **You:** {user_preview}\n\n"
            response += f"🤖 **Agent:** {agent_preview}\n\n"
            response += "-" * 70 + "\n\n"

        # Add reasoning summary
        if reasoning_history:
            response += "\n💭 **Reasoning Trail:**\n\n"
            for i, reasoning in enumerate(reasoning_history[-5:], 1):
                decision = reasoning.get("decision", "unknown")
                reason = reasoning.get("reason", "")
                response += f"{i}. **{decision}**: {reason[:150]}...\n"

        # Add summary statistics
        response += "\n\n📊 **Session Statistics:**\n"
        response += f"  - Total Exchanges: {len(conversation_history)}\n"
        response += f"  - Reasoning Steps: {len(reasoning_history)}\n"

        # Count actions
        actions_count = {}
        for exchange in conversation_history:
            action = exchange.get("action", "unknown")
            actions_count[action] = actions_count.get(action, 0) + 1

        response += f"  - Actions Taken:\n"
        for action, count in sorted(
            actions_count.items(), key=lambda x: x[1], reverse=True
        ):
            response += f"    • {action}: {count}x\n"

        # State summary
        response += f"\n📋 **Current State:**\n"
        response += (
            f"  - Extracted Fields: {len(state['certificate'].extracted_fields)}\n"
        )
        response += f"  - Active Criteria: {len(state['evaluation'].criteria)}\n"
        response += f"  - Final Score: {state['evaluation'].final_score:.1f}/100\n"

    # Update conversation history
    state["conversation"].conversation_history.append(
        {
            "user": state["conversation"].last_user_message,
            "agent": state["conversation"].last_agent_message,
            "action": "show_history",
        }
    )

    state["conversation"].last_agent_message = response

    return state
