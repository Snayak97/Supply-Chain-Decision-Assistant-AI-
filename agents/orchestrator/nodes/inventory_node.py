"""
Inventory node for LangGraph orchestration.
Layer 2 - Orchestration Layer
"""
from typing import Dict, Any
from datetime import datetime

from agents.orchestrator.state import ScenarioState
from tools.otb.otb_engine import evaluate_otb_position
from schemas.forecast_schema import AdjustedForecastResult


def evaluate_otb_node(state: ScenarioState) -> ScenarioState:
    """Evaluate OTB position under adjusted forecast."""
    if not state["adjusted_forecast"]:
        return state
    
    adjusted = AdjustedForecastResult(**state["adjusted_forecast"])
    scope = state.get("scope", {})
    
    otb_result = evaluate_otb_position(
        adjusted_forecast=adjusted,
        category=scope.get("category")
    )
    
    state["otb_position"] = otb_result.model_dump()
    state["current_step"] = "otb_evaluated"
    state["updated_at"] = datetime.utcnow().isoformat()
    
    state["tool_calls"].append({
        "tool": "evaluate_otb_position",
        "timestamp": datetime.utcnow().isoformat(),
        "result": otb_result.summary
    })
    
    return state