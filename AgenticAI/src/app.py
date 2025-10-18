from typing import Dict, Any, TypedDict, List
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from .search import search_ai_news
from .summarize import summarize_results
from .selection import generate_post, verify_post_against_facts


class AppState(TypedDict):
    queries: List[str]
    results: List[Dict[str, Any]]
    summaries: List[Dict[str, Any]]
    chosen: Dict[str, Any]
    post: str
    facts: List[str]
    verification: Dict[str, Any]
    iteration_count: int
    max_iterations: int


def build_workflow():
    graph = StateGraph(AppState)

    graph.add_node("search", search_ai_news)
    graph.add_node("summarize", summarize_results)
    graph.add_node("generate_post", generate_post)
    graph.add_node("verify", verify_post_against_facts)

    graph.add_edge(START, "search")
    graph.add_edge("search", "summarize")
    # After summarize, we pause for human to set state['chosen'] externally via CLI
    def route_after_choice(state: Dict[str, Any]):
        # Return special end label string when there's no human choice yet
        return "generate_post" if state.get("chosen") else "__end__"

    graph.add_conditional_edges("summarize", route_after_choice, {"generate_post": "generate_post", "__end__": END})

    graph.add_edge("generate_post", "verify")
    
    # After verify, check if we need to regenerate or can end
    def route_after_verify(state: Dict[str, Any]):
        verification = state.get("verification", {})
        iteration_count = state.get("iteration_count", 0)
        max_iterations = state.get("max_iterations", 3)
        
        # If verification passed or max iterations reached, end
        if verification.get("ok", False) or iteration_count >= max_iterations:
            return "__end__"
        else:
            # Need to regenerate post
            return "generate_post"

    graph.add_conditional_edges("verify", route_after_verify, {"generate_post": "generate_post", "__end__": END})

    memory = MemorySaver()
    return graph.compile(checkpointer=memory)
