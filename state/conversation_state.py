from typing import Dict, List

from pydantic import BaseModel


class ConversationState(BaseModel):
    # Messages
    last_user_message: str = ""
    last_agent_message: str = ""

    # Reasoning and uncertainty
    last_reason: str = ""
    uncertainty: str = ""

    # Intent and confirmation
    last_user_intent: str = ""
    pending_confirmation: bool = False

    # Conversation history for context persistence
    conversation_history: List[Dict[str, str]] = []
    reasoning_history: List[Dict[str, str]] = []
