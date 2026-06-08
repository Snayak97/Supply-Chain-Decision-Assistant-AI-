"""
Scenario simulation API routes.
Layer 1 - Interaction Layer
"""
from fastapi import APIRouter, HTTPException
from typing import Optional, Dict, Any
from datetime import datetime

from schemas.scenario_schema import ScenarioRequest, ScenarioResult
from agents.orchestrator.graph.supply_chain_graph import (
    build_scenario_graph,
    initialize_state
)
from core.cache.cache_manager import CacheManager

router = APIRouter(prefix="/scenario", tags=["scenario"])


# @router.post("/simulate", response_model=ScenarioResult)
# async def simulate_scenario(request: ScenarioRequest):
#     """
#     Run a scenario simulation query.
    
#     This endpoint orchestrates the full scenario workflow:
#     1. Parse perturbations from natural language
#     2. Retrieve baseline forecast
#     3. Apply scenario adjustments
#     4. Calculate stockout risk
#     5. Evaluate OTB position
#     6. Generate recommendations
    
#     Example queries:
#     - "What does the forecast look like if we increase the topline by 25%?"
#     - "Show me the impact if DTC demand drops 15% while wholesale stays flat."
#     - "What happens to stockout risk on core SKUs if apparel demand is up 30%?"
#     """
#     try:
#         # Initialize or retrieve session state
#         session_id = request.session_id or f"session_{datetime.utcnow().timestamp()}"
        
#         # Check for existing session perturbations
#         existing_session = CacheManager.get_scenario_session(session_id)
#         existing_perturbations = existing_session["perturbations"] if existing_session else []
        
#         # Initialize state
#         state = initialize_state(
#             query=request.query,
#             session_id=session_id,
#             scope=request.scope
#         )
        
#         # Add existing perturbations if any
#         if existing_perturbations:
#             state["perturbations"] = existing_perturbations
        
#         # Build and run the graph
#         graph = build_scenario_graph()
#         print("BEFORE GRAPH")
#         result_state = graph.invoke(state)
#         print("After GRAPH")

#         print("perturbations:", result_state.get("perturbations"))
#         ("perturbation_summary:", result_state.get("perturbation_summary"))
#         print("baseline_forecast:", result_state.get("baseline_forecast"))
#         print("adjusted_forecast:", result_state.get("adjusted_forecast"))
#         print("stockout_risk:", result_state.get("stockout_risk"))
#         print("otb_position:", result_state.get("otb_position"))
#         print("recommendations:", result_state.get("recommendations"))
#         print("tool_calls:", result_state.get("tool_calls"))
#         print("BUILDING SCENARIO RESULT...")


#         print("BUILDING SCENARIO RESULT...")

# # ADD THESE 4 LINES
#         import json
#         try:
#         test = json.dumps(result_state["recommendations"])
#         print("RECOMMENDATIONS JSON OK, size:", len(test))
#         except Exception as e:
#         print("RECOMMENDATIONS JSON FAILED:", e)

#         try:
#             test = json.dumps(result_state["adjusted_forecast"])
#             print("ADJUSTED FORECAST JSON OK, size:", len(test))
#         except Exception as e:
#             print("ADJUSTED FORECAST JSON FAILED:", e)

#         try:
#             test = json.dumps(result_state["stockout_risk"])
#             print("STOCKOUT RISK JSON OK, size:", len(test))
#         except Exception as e:
#             print("STOCKOUT RISK JSON FAILED:", e)


        
#         # Save updated perturbations to session
#         CacheManager.save_scenario_session(
#             session_id=session_id,
#             perturbations=result_state["perturbations"]
#         )
        
#         # Build response
#         scenario_result = ScenarioResult(
#             session_id=session_id,
#             query=request.query,
#             perturbations=result_state["perturbations"],
#             perturbation_summary=result_state["perturbation_summary"],
#             baseline_forecast=result_state["baseline_forecast"],
#             adjusted_forecast=result_state["adjusted_forecast"],
#             stockout_risk=result_state["stockout_risk"],
#             otb_position=result_state["otb_position"],
#             recommendations=result_state["recommendations"],
#             tool_calls=result_state["tool_calls"],
#             processing_time_ms=0,  # Could add timing
#             summary=_generate_response_summary(result_state)
#         )
        
#         return scenario_result
#         # return {
#         #     "message": "working"
#         # # }
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Scenario simulation failed: {str(e)}")


# def _strip_forecast_items(forecast):
#     """Remove raw SKU rows, keep only summary fields."""
#     if not forecast:
#         return forecast
#     return {k: v for k, v in forecast.items() if k != "items"}

# def _strip_risk_items(stockout_risk):
#     """Keep only top 10 at-risk SKUs, remove the rest."""
#     if not stockout_risk:
#         return stockout_risk
#     result = dict(stockout_risk)
#     if "at_risk_skus" in result:
#         result["at_risk_skus"] = result["at_risk_skus"][:10]
#     return result


# @router.post("/simulate", response_model=ScenarioResult)
# async def simulate_scenario(request: ScenarioRequest):
#     try:
#         session_id = request.session_id or f"session_{datetime.utcnow().timestamp()}"
        
#         existing_session = CacheManager.get_scenario_session(session_id)
#         existing_perturbations = existing_session["perturbations"] if existing_session else []
        
#         state = initialize_state(
#             query=request.query,
#             session_id=session_id,
#             scope=request.scope
#         )
        
#         if existing_perturbations:
#             state["perturbations"] = existing_perturbations
        
#         graph = build_scenario_graph()
#         print("BEFORE GRAPH")
#         result_state = graph.invoke(state)
#         print("After GRAPH")

#         print("BUILDING SCENARIO RESULT...")

#         import json
#         try:
#             test = json.dumps(result_state["recommendations"])
#             print("RECOMMENDATIONS JSON OK, size:", len(test))
#         except Exception as e:
#             print("RECOMMENDATIONS JSON FAILED:", e)

#         try:
#             test = json.dumps(result_state["adjusted_forecast"])
#             print("ADJUSTED FORECAST JSON OK, size:", len(test))
#         except Exception as e:
#             print("ADJUSTED FORECAST JSON FAILED:", e)

#         try:
#             test = json.dumps(result_state["stockout_risk"])
#             print("STOCKOUT RISK JSON OK, size:", len(test))
#         except Exception as e:
#             print("STOCKOUT RISK JSON FAILED:", e)

#         CacheManager.save_scenario_session(
#             session_id=session_id,
#             perturbations=result_state["perturbations"]
#         )
        
#         scenario_result = ScenarioResult(
#             session_id=session_id,
#             query=request.query,
#             perturbations=result_state["perturbations"],
#             perturbation_summary=result_state["perturbation_summary"],
#             # baseline_forecast=result_state["baseline_forecast"],
#             # adjusted_forecast=result_state["adjusted_forecast"],
#             baseline_forecast=_strip_forecast_items(result_state["baseline_forecast"]),
#             adjusted_forecast=_strip_forecast_items(result_state["adjusted_forecast"]),
#             stockout_risk=result_state["stockout_risk"],
#             otb_position=result_state["otb_position"],
#             recommendations=result_state["recommendations"],
#             tool_calls=result_state["tool_calls"],
#             processing_time_ms=0,
#             summary=_generate_response_summary(result_state)
#         )
        
#         return scenario_result
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Scenario simulation failed: {str(e)}")




# def _strip_forecast_items(forecast):
#     if not forecast:
#         return forecast
#     return {k: v for k, v in forecast.items() if k != "items"}
def _strip_forecast_items(forecast):
    if not forecast:
        return forecast
    return {k: v for k, v in forecast.items() if k not in ("items", "forecast_data", "adjusted_data")}

def _strip_risk_items(stockout_risk):
    if not stockout_risk:
        return stockout_risk
    result = dict(stockout_risk)
    if "at_risk_skus" in result:
        result["at_risk_skus"] = result["at_risk_skus"][:10]
    return result

def _strip_recommendations(recommendations):
    if not recommendations:
        return recommendations
    result = dict(recommendations)
    if "recommendations" in result:
        result["recommendations"] = result["recommendations"][:10]
    return result


@router.post("/simulate", response_model=ScenarioResult,response_model_exclude_none=True)
async def simulate_scenario(request: ScenarioRequest):
    try:
        session_id = request.session_id or f"session_{datetime.utcnow().timestamp()}"
        
        existing_session = CacheManager.get_scenario_session(session_id)
        existing_perturbations = existing_session["perturbations"] if existing_session else []
        
        state = initialize_state(
            query=request.query,
            session_id=session_id,
            scope=request.scope
        )
        
        if existing_perturbations:
            state["perturbations"] = existing_perturbations
        
        graph = build_scenario_graph()
        print("BEFORE GRAPH")
        result_state = graph.invoke(state)
        print("After GRAPH")

        CacheManager.save_scenario_session(
            session_id=session_id,
            perturbations=result_state["perturbations"]
        )
        
        scenario_result = ScenarioResult(
            session_id=session_id,
            query=request.query,
            perturbations=result_state["perturbations"],
            perturbation_summary=result_state["perturbation_summary"],
            baseline_forecast=_strip_forecast_items(result_state["baseline_forecast"]),
            adjusted_forecast=_strip_forecast_items(result_state["adjusted_forecast"]),
            stockout_risk=_strip_risk_items(result_state["stockout_risk"]),
            otb_position=result_state["otb_position"],
            recommendations=_strip_recommendations(result_state["recommendations"]),
            tool_calls=result_state["tool_calls"],
            processing_time_ms=0,
            summary=_generate_response_summary(result_state)
        )
        
        return scenario_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scenario simulation failed: {str(e)}")





@router.post("/reset")
async def reset_scenario(session_id: str):
    """
    Clear scenario perturbations for a session.
    
    This resets the session state without ending the conversation,
    allowing the user to start fresh with a new scenario.
    """
    try:
        CacheManager.clear_scenario_session(session_id)
        return {
            "session_id": session_id,
            "status": "reset",
            "message": "Scenario perturbations cleared"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reset scenario: {str(e)}")


@router.get("/session/{session_id}")
async def get_session(session_id: str):
    """Retrieve current scenario session state."""
    try:
        session = CacheManager.get_scenario_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve session: {str(e)}")


def _generate_response_summary(state: Dict[str, Any]) -> str:
    """Generate a natural language summary of the scenario results."""
    summary_parts = []
    
    # Perturbation summary
    if state["perturbation_summary"]:
        summary_parts.append(f"Applied: {state['perturbation_summary']}")
    
    # Forecast impact
    if state["adjusted_forecast"]:
        adj = state["adjusted_forecast"]
        change_pct = adj.get("total_change_pct", 0)
        summary_parts.append(f"Forecast changed by {change_pct:+.1f}%")
    
    # Risk impact
    if state["stockout_risk"]:
        risk = state["stockout_risk"]
        summary_parts.append(
            f"{risk['sku_count_at_risk']} SKUs at risk, "
            f"${risk['total_revenue_at_risk']:,.0f} revenue at risk"
        )
    
    # OTB impact
    if state["otb_position"]:
        otb = state["otb_position"]
        if otb["overcommitted_categories"]:
            summary_parts.append(
                f"{len(otb['overcommitted_categories'])} categories overcommitted"
            )
    
    # Recommendations
    if state["recommendations"]:
        recs = state["recommendations"]
        summary_parts.append(f"{len(recs['recommendations'])} recommendations generated")
    
    return ". ".join(summary_parts) if summary_parts else "Scenario simulation complete."
