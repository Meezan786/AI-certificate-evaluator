from graph.graph import build_graph
from state.certificate_state import CertificateState
from state.conversation_state import ConversationState
from state.evaluation_state import EvaluationState
from state.global_state import GlobalState
from utils.state_manager import StateManager

# Initialize state manager for persistence
state_manager = StateManager()

# Initialize state as a dict (required for TypedDict)
state: GlobalState = {
    "certificate": CertificateState(),
    "conversation": ConversationState(),
    "evaluation": EvaluationState(),
}

# Try to load previous session
print("🔄 Checking for previous session...")
state = state_manager.load_state(state)

# If no previous session, load certificate data
if not state["certificate"].raw_text:
    try:
        with open("data/certificate.txt") as f:
            certificate_text = f.read()
            if certificate_text.strip():
                state["certificate"].raw_text = certificate_text
                print("✓ Certificate data loaded successfully")
            else:
                print(
                    "⚠️  Warning: certificate.txt is empty. Please add your certificate data."
                )
    except FileNotFoundError:
        print(
            "⚠️  Warning: certificate.txt not found. Please create it with your certificate data."
        )
else:
    print("✓ Using certificate data from previous session")

# Build the agent graph
graph = build_graph()

print("\n" + "=" * 70)
print("🎓 Agentic Certificate Evaluation AI (Production-Ready)")
print("=" * 70)
print("\nThis is a fully agentic system with PERSISTENT MEMORY!")
print("Your data is automatically saved and restored across sessions.")
print("\nFeatures:")
print("  • Intelligent auto-extraction when needed")
print("  • Context-aware responses using existing data")
print("  • Persistent state - no data loss between sessions")
print("  • Full conversation history tracking")
print("  • Dynamic action selection - no workflows!")
print("\nYou can:")
print("  • Ask questions directly (I'll extract automatically if needed)")
print("  • Set or modify evaluation criteria")
print("  • Request scoring or re-scoring")
print("  • Ask for explanations of my decisions")
print("  • Challenge or correct my assessments")
print("  • View conversation history")
print("\nCommands:")
print("  • 'exit' - Quit (your session is auto-saved)")
print("  • 'history' - See conversation history")
print("  • 'clear' - Start fresh session")
print("  • 'status' - Show current session info")
print("=" * 70 + "\n")

# Show session info if continuing
if state["conversation"].conversation_history:
    print(
        f"📌 Continuing previous session ({len(state['conversation'].conversation_history)} exchanges)"
    )
    print(f"   Extracted fields: {len(state['certificate'].extracted_fields)}")
    print(f"   Active criteria: {len(state['evaluation'].criteria)}")
    print(f"   Current score: {state['evaluation'].final_score:.1f}/100\n")

# Main conversation loop
turn_number = 0
while True:
    user_input = input("\n💬 You: ")

    if user_input.lower() == "exit":
        # Save state before exiting
        print("\n💾 Saving session...")
        if state_manager.save_state(state):
            print("✓ Session saved successfully!")
        print("👋 Goodbye! Your session is saved and will be restored next time.")
        break

    if user_input.lower() == "history":
        print("\n📜 Conversation History:")
        print("-" * 70)
        if state["conversation"].conversation_history:
            for i, exchange in enumerate(state["conversation"].conversation_history, 1):
                print(f"\n[{i}] Action: {exchange.get('action', 'unknown')}")
                print(f"    You: {exchange.get('user', '')[:100]}...")
                print(f"    Agent: {exchange.get('agent', '')[:150]}...")
        else:
            print("No history yet - start a conversation!")
        print("-" * 70)
        continue

    if user_input.lower() == "clear":
        confirm = input("⚠️  Clear current session? This cannot be undone. (yes/no): ")
        if confirm.lower() == "yes":
            state_manager.clear_session()
            state = {
                "certificate": CertificateState(),
                "conversation": ConversationState(),
                "evaluation": EvaluationState(),
            }
            # Reload certificate
            try:
                with open("data/certificate.txt") as f:
                    cert_text = f.read()
                    if cert_text.strip():
                        state["certificate"].raw_text = cert_text
            except FileNotFoundError:
                pass
            print("✓ Session cleared! Starting fresh.")
        continue

    if user_input.lower() == "status":
        print("\n" + state_manager.get_session_summary())
        continue

    if not user_input.strip():
        print("⚠️  Please enter a message.")
        continue

    turn_number += 1

    # Set user message in state
    state["conversation"].last_user_message = user_input

    # Invoke the agent graph - it will decide what to do
    try:
        state = graph.invoke(state)

        # Display agent response
        print(f"\n🤖 Agent: {state['conversation'].last_agent_message}")

        # Show reasoning if available (optional debug info)
        if state["conversation"].last_reason and turn_number <= 3:
            print(f"\n💭 [Reasoning: {state['conversation'].last_reason}]")

        # Auto-save state after each turn (production feature!)
        state_manager.save_state(state)

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("Please try rephrasing your request or check the system logs.")

print("\n" + "=" * 70)
print(
    f"Session ended. Total exchanges: {len(state['conversation'].conversation_history)}"
)
print("=" * 70)
