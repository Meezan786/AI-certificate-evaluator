from langgraph.graph import END, StateGraph

from agent.agent import agent_node
from state.global_state import GlobalState


def build_graph():
    """
    Build the LangGraph state graph for the agentic certificate evaluator.

    Architecture:
    - Single agent node that makes all decisions
    - Each invocation is one turn (no looping)
    - Main.py handles the conversation loop
    - Agent executes one action per turn and returns
    """
    graph = StateGraph(GlobalState)

    # Add the main agent decision node
    graph.add_node("agent", agent_node)

    # Set entry point
    graph.set_entry_point("agent")

    # Agent always goes to END after one turn
    # The conversation loop in main.py handles multiple turns
    graph.add_edge("agent", END)

    # Note: We intentionally do NOT loop inside the graph
    # Each graph.invoke() executes ONE agent decision
    # The main.py conversation loop calls graph.invoke() repeatedly
    # This prevents recursion limits while maintaining agentic behavior

    return graph.compile()
