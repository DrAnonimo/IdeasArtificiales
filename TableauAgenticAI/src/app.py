from typing import Dict, Any, TypedDict, List
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from .search import search_ai_news
from .summarize import summarize_results
from .selection import generate_post, verify_post_against_facts
from .news_tracker import NewsTracker
from .bubble_analysis import AIBubbleAnalyzer
from .tableau_export import TableauExporter
from .time_series_collector import TimeSeriesCollector


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
    # New bubble analysis fields
    tracked_news: List[Dict[str, Any]]
    bubble_analysis: Dict[str, Any]
    tableau_export: Dict[str, Any]
    # Time series fields
    daily_snapshot: Dict[str, Any]
    time_series_export: Dict[str, Any]


def track_news_for_bubble_analysis(state: Dict[str, Any]) -> Dict[str, Any]:
    """Track news articles for bubble analysis"""
    tracker = NewsTracker()
    results = state.get("results", [])
    
    # Add news articles to tracker
    tracking_result = tracker.add_news_articles(results)
    
    return {
        **state,
        "tracked_news": tracking_result["articles"]
    }


def analyze_bubble_indicators(state: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze tracked news for bubble indicators"""
    tracker = NewsTracker()
    
    # Analyze news for bubble indicators
    analysis_result = tracker.analyze_news()
    
    # Get bubble report
    bubble_report = tracker.get_bubble_report()
    
    return {
        **state,
        "bubble_analysis": bubble_report
    }


def export_for_tableau(state: Dict[str, Any]) -> Dict[str, Any]:
    """Export data for Tableau dashboard"""
    exporter = TableauExporter()
    
    # Export all data
    export_result = exporter.export_all_data()
    
    return {
        **state,
        "tableau_export": export_result
    }


def collect_daily_snapshot(state: Dict[str, Any]) -> Dict[str, Any]:
    """Collect daily snapshot for time series analysis"""
    collector = TimeSeriesCollector()
    
    # Collect daily snapshot
    snapshot = collector.collect_daily_snapshot()
    
    return {
        **state,
        "daily_snapshot": {
            "date": snapshot.date,
            "timestamp": snapshot.timestamp,
            "market_assessment": snapshot.market_assessment,
            "average_bubble_risk": snapshot.average_bubble_risk,
            "average_sentiment": snapshot.average_sentiment,
            "concerning_articles": snapshot.concerning_articles
        }
    }


def export_time_series_data(state: Dict[str, Any]) -> Dict[str, Any]:
    """Export time series data for Grafana"""
    collector = TimeSeriesCollector()
    
    # Export for Grafana
    export_result = collector.export_for_grafana(days=30)
    
    return {
        **state,
        "time_series_export": export_result
    }


def build_workflow():
    graph = StateGraph(AppState)

    graph.add_node("search", search_ai_news)
    graph.add_node("summarize", summarize_results)
    graph.add_node("track_news", track_news_for_bubble_analysis)
    graph.add_node("analyze_bubble", analyze_bubble_indicators)
    graph.add_node("export_tableau", export_for_tableau)
    graph.add_node("collect_snapshot", collect_daily_snapshot)
    graph.add_node("export_timeseries", export_time_series_data)
    graph.add_node("generate_post", generate_post)
    graph.add_node("verify", verify_post_against_facts)

    graph.add_edge(START, "search")
    graph.add_edge("search", "summarize")
    graph.add_edge("summarize", "track_news")
    graph.add_edge("track_news", "analyze_bubble")
    graph.add_edge("analyze_bubble", "export_tableau")
    graph.add_edge("export_tableau", "collect_snapshot")
    graph.add_edge("collect_snapshot", "export_timeseries")
    
    # After time series export, we pause for human to set state['chosen'] externally via CLI
    def route_after_timeseries(state: Dict[str, Any]):
        # Return special end label string when there's no human choice yet
        return "generate_post" if state.get("chosen") else "__end__"

    graph.add_conditional_edges("export_timeseries", route_after_timeseries, {"generate_post": "generate_post", "__end__": END})

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
