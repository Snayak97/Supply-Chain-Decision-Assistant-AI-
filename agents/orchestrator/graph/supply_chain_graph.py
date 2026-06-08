"""
LangGraph for scenario simulation workflow.
Layer 2 - Orchestration Layer
"""
from langgraph.graph import StateGraph, END
from agents.orchestrator.state import ScenarioState
from datetime import datetime
import uuid

from agents.orchestrator.nodes.forecast_node import (
    parse_perturbations_node,
    get_forecast_node,
    apply_scenario_node
)
from agents.orchestrator.nodes.inventory_node import evaluate_otb_node
from agents.orchestrator.nodes.risk_node import calculate_risk_node
from agents.orchestrator.nodes.recommendation_node import generate_recommendations_node


def build_scenario_graph():
    """Build the LangGraph for scenario simulation workflow."""
    
    graph = StateGraph(ScenarioState)
    
    # Add nodes
    graph.add_node("parse_perturbations", parse_perturbations_node)
    graph.add_node("get_forecast", get_forecast_node)
    graph.add_node("apply_scenario", apply_scenario_node)
    graph.add_node("calculate_risk", calculate_risk_node)
    graph.add_node("evaluate_otb", evaluate_otb_node)
    graph.add_node("generate_recommendations", generate_recommendations_node)
    
    # Define the workflow sequence
    graph.set_entry_point("parse_perturbations")
    
    graph.add_edge("parse_perturbations", "get_forecast")
    graph.add_edge("get_forecast", "apply_scenario")
    graph.add_edge("apply_scenario", "calculate_risk")
    graph.add_edge("calculate_risk", "evaluate_otb")
    graph.add_edge("evaluate_otb", "generate_recommendations")
    graph.add_edge("generate_recommendations", END)
    
    return graph.compile()


def initialize_state(query: str, session_id: str = None, scope: dict = None) -> ScenarioState:
    """Initialize the scenario state for a new query."""
    if session_id is None:
        session_id = str(uuid.uuid4())
    
    return {
        "query": query,
        "session_id": session_id,
        "perturbations": [],
        "perturbation_summary": "",
        "scope": scope or {},
        "baseline_forecast": None,
        "adjusted_forecast": None,
        "stockout_risk": None,
        "otb_position": None,
        "recommendations": None,
        "response": None,
        "current_step": "initialized",
        "error": None,
        "tool_calls": [],
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }