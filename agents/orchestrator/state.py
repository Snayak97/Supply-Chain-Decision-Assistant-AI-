"""
Orchestration state for LangGraph scenario workflow.
Layer 2 - Orchestration Layer
"""
from typing import TypedDict, Optional, List, Dict, Any
from datetime import datetime
 
 
class ScenarioState(TypedDict):
    """State object for LangGraph scenario workflow."""
 
    # User input
    query: str
    session_id: str
 
    # Parsed perturbations
    perturbations: List[Dict[str, Any]]
    perturbation_summary: str
 
    # Scope filters
    scope: Dict[str, Any]
 
    # Tool results
    baseline_forecast: Optional[Dict[str, Any]]
    adjusted_forecast: Optional[Dict[str, Any]]
    stockout_risk: Optional[Dict[str, Any]]
    otb_position: Optional[Dict[str, Any]]
    recommendations: Optional[Dict[str, Any]]
 
    # Final response
    response: Optional[str]
 
    # Metadata
    current_step: str
    error: Optional[str]
    tool_calls: List[Dict[str, Any]]
 
    # Timestamps
    created_at: str
    updated_at: str