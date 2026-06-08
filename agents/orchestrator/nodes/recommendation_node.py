"""
Recommendation node for LangGraph orchestration.
Layer 2 - Orchestration Layer
"""
from typing import Dict, Any
from datetime import datetime

from agents.orchestrator.state import ScenarioState
from tools.recommendation.recommendation_engine import generate_recommendations
from schemas.risk_schema import StockoutRiskResult
from schemas.otb_schema import OTBPositionResult


def generate_recommendations_node(state: ScenarioState) -> ScenarioState:
    """Generate recommendations based on risk and OTB analysis."""
    if not state["stockout_risk"] or not state["otb_position"]:
        return state
    
    risk = StockoutRiskResult(**state["stockout_risk"])
    otb = OTBPositionResult(**state["otb_position"])
    scope = state.get("scope", {})
    
    recommendations = generate_recommendations(
        stockout_risk=risk,
        otb_position=otb,
        category=scope.get("category")
    )
    
    state["recommendations"] = recommendations.model_dump()
    state["current_step"] = "recommendations_generated"
    state["updated_at"] = datetime.utcnow().isoformat()
    
    state["tool_calls"].append({
        "tool": "generate_recommendations",
        "timestamp": datetime.utcnow().isoformat(),
        "result": recommendations.summary
    })
    
    return state