import json
import os
from datetime import datetime
from pathlib import Path


class StateManager:
    """
    Manages state persistence for the Agentic Certificate Evaluator.
    Saves and loads state to/from disk for production-ready memory.
    """

    def __init__(self, state_dir="session_data"):
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(exist_ok=True)
        self.current_session_file = self.state_dir / "current_session.json"
        self.history_dir = self.state_dir / "history"
        self.history_dir.mkdir(exist_ok=True)

    def save_state(self, state):
        """
        Save the current state to disk.

        Args:
            state: GlobalState dict with certificate, conversation, evaluation
        """
        try:
            # Convert state to JSON-serializable format
            state_data = {
                "timestamp": datetime.now().isoformat(),
                "certificate": {
                    "raw_text": state["certificate"].raw_text,
                    "extracted_fields": state["certificate"].extracted_fields,
                    "confidence": state["certificate"].confidence,
                },
                "evaluation": {
                    "criteria": state["evaluation"].criteria,
                    "scores": state["evaluation"].scores,
                    "final_score": state["evaluation"].final_score,
                },
                "conversation": {
                    "last_user_message": state["conversation"].last_user_message,
                    "last_agent_message": state["conversation"].last_agent_message,
                    "last_reason": state["conversation"].last_reason,
                    "uncertainty": state["conversation"].uncertainty,
                    "last_user_intent": state["conversation"].last_user_intent,
                    "pending_confirmation": state["conversation"].pending_confirmation,
                    "conversation_history": state["conversation"].conversation_history,
                    "reasoning_history": state["conversation"].reasoning_history,
                },
            }

            # Save to current session file
            with open(self.current_session_file, "w") as f:
                json.dump(state_data, f, indent=2)

            # Also save to history with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            history_file = self.history_dir / f"session_{timestamp}.json"
            with open(history_file, "w") as f:
                json.dump(state_data, f, indent=2)

            return True

        except Exception as e:
            print(f"⚠️ Failed to save state: {e}")
            return False

    def load_state(self, state):
        """
        Load the last saved state from disk if it exists.

        Args:
            state: Empty GlobalState dict to populate

        Returns:
            Populated state dict or original empty state
        """
        try:
            if not self.current_session_file.exists():
                return state  # No saved state, return empty

            with open(self.current_session_file, "r") as f:
                state_data = json.load(f)

            # Restore certificate state
            state["certificate"].raw_text = state_data["certificate"]["raw_text"]
            state["certificate"].extracted_fields = state_data["certificate"][
                "extracted_fields"
            ]
            state["certificate"].confidence = state_data["certificate"]["confidence"]

            # Restore evaluation state
            state["evaluation"].criteria = state_data["evaluation"]["criteria"]
            state["evaluation"].scores = state_data["evaluation"]["scores"]
            state["evaluation"].final_score = state_data["evaluation"]["final_score"]

            # Restore conversation state
            conv = state_data["conversation"]
            state["conversation"].last_user_message = conv["last_user_message"]
            state["conversation"].last_agent_message = conv["last_agent_message"]
            state["conversation"].last_reason = conv["last_reason"]
            state["conversation"].uncertainty = conv["uncertainty"]
            state["conversation"].last_user_intent = conv["last_user_intent"]
            state["conversation"].pending_confirmation = conv["pending_confirmation"]
            state["conversation"].conversation_history = conv["conversation_history"]
            state["conversation"].reasoning_history = conv["reasoning_history"]

            print(
                f"✓ Loaded previous session ({len(conv['conversation_history'])} exchanges)"
            )
            return state

        except Exception as e:
            print(f"⚠️ Failed to load state: {e}")
            return state  # Return empty state on error

    def clear_session(self):
        """Clear the current session file."""
        try:
            if self.current_session_file.exists():
                self.current_session_file.unlink()
            print("✓ Session cleared")
            return True
        except Exception as e:
            print(f"⚠️ Failed to clear session: {e}")
            return False

    def list_sessions(self):
        """List all saved session files."""
        try:
            sessions = sorted(self.history_dir.glob("session_*.json"), reverse=True)
            return [s.name for s in sessions]
        except Exception as e:
            print(f"⚠️ Failed to list sessions: {e}")
            return []

    def get_session_summary(self):
        """Get a summary of the current session."""
        try:
            if not self.current_session_file.exists():
                return "No active session"

            with open(self.current_session_file, "r") as f:
                state_data = json.load(f)

            timestamp = state_data.get("timestamp", "Unknown")
            conv_count = len(state_data["conversation"]["conversation_history"])
            extracted_count = len(state_data["certificate"]["extracted_fields"])
            criteria_count = len(state_data["evaluation"]["criteria"])

            return (
                f"Session from {timestamp}\n"
                f"  - Conversations: {conv_count}\n"
                f"  - Extracted fields: {extracted_count}\n"
                f"  - Active criteria: {criteria_count}"
            )

        except Exception as e:
            return f"Error reading session: {e}"
