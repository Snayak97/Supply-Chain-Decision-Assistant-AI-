"""
Risk analysis node for LangGraph orchestration.
Layer 2 - Orchestration Layer
"""
from typing import Dict, Any
from datetime import datetime

from agents.orchestrator.state import ScenarioState
from tools.risk.risk_engine import calculate_stockout_risk
from schemas.forecast_schema import AdjustedForecastResult


def calculate_risk_node(state: ScenarioState) -> ScenarioState:
    """Calculate stockout risk under adjusted forecast."""
    if not state["adjusted_forecast"]:
        return state
    
    adjusted = AdjustedForecastResult(**state["adjusted_forecast"])
    scope = state.get("scope", {})
    
    risk_result = calculate_stockout_risk(
        adjusted_forecast=adjusted,
        category=scope.get("category"),
        channel=scope.get("channel")
    )
    
    state["stockout_risk"] = risk_result.model_dump()
    state["current_step"] = "risk_calculated"
    state["updated_at"] = datetime.utcnow().isoformat()
    
    state["tool_calls"].append({
        "tool": "calculate_stockout_risk",
        "timestamp": datetime.utcnow().isoformat(),
        "result": risk_result.summary
    })
    
    return state