"""
LangGraph nodes for scenario orchestration.
Layer 2 - Orchestration Layer
"""
from typing import Dict, Any
from datetime import datetime
import json

from langchain_ollama import ChatOllama
from core.config.settings import settings
from agents.orchestrator.state import ScenarioState
from tools.forecast.forecast_engine import get_demand_forecast, apply_topline_adjustment
from schemas.perturbation_schema import Perturbation, PerturbationType
from langchain_google_genai import ChatGoogleGenerativeAI
# Initialize Ollama LLM
# llm = ChatOllama(model=settings.OLLAMA_MODEL, base_url=settings.OLLAMA_BASE_URL)
# print(settings.OLLAMA_MODEL)
# print(settings.OLLAMA_BASE_URL)

def get_llm():
    print("PROVIDER:", settings.LLM_PROVIDER)
    print("MODEL:", settings.OLLAMA_MODEL)
    print("BASE_URL:", settings.OLLAMA_BASE_URL)

    if settings.LLM_PROVIDER == "ollama":

        return ChatOllama(
            model=settings.OLLAMA_MODEL,
            base_url=settings.OLLAMA_BASE_URL
        )

    elif settings.LLM_PROVIDER == "gemini":

        return ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            google_api_key=settings.GOOGLE_API_KEY
        )

    raise ValueError(
        f"Unsupported provider: {settings.LLM_PROVIDER}"
    )

llm = get_llm()





# def parse_perturbations_node(state: ScenarioState) -> ScenarioState:
#     """
#     Parse user query to extract perturbations using LLM.
    
#     Recognizes and structures four categories of perturbation from natural language:
#     - Topline scalar: 'increase the topline by 25%'
#     - Segment or channel override: 'DTC down 15%'
#     - Category pin: 'apparel up 30%'
#     - Compound (multi-turn): accumulated as a list
#     """
#     query = state["query"]
#     perturbations = []
    
#     # Use LLM to parse perturbations
#     prompt = f"""
# You are a supply chain assistant. Parse the following user query and extract perturbations.

# Query: "{query}"

# Extract perturbations in the following categories:
# 1. Topline: scalar multiplier (e.g., "increase topline by 25%" -> multiplier: 1.25)
# 2. Channel: channel-specific adjustment (e.g., "DTC down 15%" -> channel: "DTC", multiplier: 0.85)
# 3. Category: category-specific adjustment (e.g., "apparel up 30%" -> category: "Apparel", multiplier: 1.30)
# 4. Shipment Delay: delay in days (e.g., "shipment delay 5 days" -> delay_days: 5)

# Return ONLY a JSON array of perturbations. If no perturbations found, return empty array [].

# Example output format:
# [
#   {{"type": "topline", "multiplier": 1.25, "scope": "all"}},
#   {{"type": "channel", "channel": "DTC", "multiplier": 0.85}},
#   {{"type": "category", "category": "Apparel", "multiplier": 1.30}},
#   {{"type": "shipment_delay", "delay_days": 5, "scope": "all"}}
# ]
# """
    
#     try:
#         response = llm.invoke(prompt)

#         print("RESPONSE TYPE:")
#         print(type(response))

#         print("FULL RESPONSE:")
#         print(response)

#         print("CONTENT:")
#         print(repr(response.content))
#         print("RAW RESPONSE START")
#         response_text = response.content.strip()
#         print("RAW RESPONSE END")


        

#         if "```json" in response_text:
#             response_text = response_text.split("```json")[1].split("```")[0].strip()
#         elif "```" in response_text:
#             response_text = response_text.split("```")[1].split("```")[0].strip()

#     # Extract JSON array from prose
#         start_idx = response_text.find("[")
#         end_idx = response_text.rfind("]")

#         if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
#             response_text = response_text[start_idx:end_idx + 1]
#             perturbations = json.loads(response_text)
#         else:
#             perturbations = []


#         # # # Parse JSON response
#         # if response_text.startswith("```json"):
#         #     response_text = response_text.replace("```json", "").replace("```", "").strip()
        
#         # perturbations = json.loads(response_text)
        
#         # # Ensure perturbations is a list
#         if not isinstance(perturbations, list):
#             perturbations = []
            
#     except Exception as e:
#         # Fallback to empty perturbations if LLM fails
#         print(f"LLM parsing failed: {e}")
#         perturbations = []
    
#     state["perturbations"] = perturbations
#     state["perturbation_summary"] = " | ".join([str(p) for p in perturbations]) if perturbations else "No perturbations detected"
#     state["current_step"] = "perturbations_parsed"
#     state["updated_at"] = datetime.utcnow().isoformat()
    
#     return state

def parse_perturbations_node(state: ScenarioState) -> ScenarioState:
    query = state["query"]
    perturbations = []
    
    prompt = f"""You are a supply chain assistant. Parse the following user query and extract perturbations.

Query: "{query}"

Rules:
- If the query mentions a CHANNEL (DTC or Wholesale) with a percentage change, use type "channel"
- If the query mentions a CATEGORY (Apparel, Shoes, Accessories) with a percentage change, use type "category"
- If the query mentions overall/topline/total demand with a percentage change, use type "topline"
- If the query mentions shipment delay in days, use type "shipment_delay"
- "DTC" and "Wholesale" are CHANNELS, NOT categories. Never use them as category values.

Return ONLY a raw JSON array. No explanation, no preamble, no markdown.
Output must start with [ and end with ].
Only extract perturbations explicitly mentioned in the query. Do not infer or add anything not stated.
If no perturbations found, return [].

Examples:
Query "Reduce DTC demand by 15%" -> [{{"type": "channel", "channel": "DTC", "multiplier": 0.85}}]
Query "increase topline by 25%" -> [{{"type": "topline", "multiplier": 1.25, "scope": "all"}}]
Query "apparel up 30%" -> [{{"type": "category", "category": "Apparel", "multiplier": 1.30}}]
Query "DTC down 15% while wholesale stays flat" -> [{{"type": "channel", "channel": "DTC", "multiplier": 0.85}}]
Query "shipment delay 5 days" -> [{{"type": "shipment_delay", "delay_days": 5, "scope": "all"}}]
"""
    
    try:
        response = llm.invoke(prompt)
        response_text = response.content.strip()

        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        start_idx = response_text.find("[")
        end_idx = response_text.rfind("]")

        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            response_text = response_text[start_idx:end_idx + 1]
            perturbations = json.loads(response_text)
        else:
            perturbations = []

        if not isinstance(perturbations, list):
            perturbations = []

        query_lower = query.lower()
        validated = []
        for p in perturbations:
            ptype = p.get("type")
            if ptype == "topline":
                if any(word in query_lower for word in ["topline", "overall", "total", "all"]):
                    validated.append(p)
            elif ptype == "channel":
                channel = p.get("channel", "").lower()
                if channel in query_lower:
                    validated.append(p)
            elif ptype == "category":
                category = p.get("category", "").lower()
                if category in query_lower:
                    validated.append(p)
            elif ptype == "shipment_delay":
                if any(word in query_lower for word in ["delay", "ship", "transit"]):
                    validated.append(p)
        perturbations = validated

    except Exception as e:
        print(f"LLM parsing failed: {e}")
        perturbations = []
    
    state["perturbations"] = perturbations
    state["perturbation_summary"] = " | ".join([str(p) for p in perturbations]) if perturbations else "No perturbations detected"
    state["current_step"] = "perturbations_parsed"
    state["updated_at"] = datetime.utcnow().isoformat()
    
    return state


def get_forecast_node(state: ScenarioState) -> ScenarioState:
    """Retrieve baseline forecast."""
    scope = state.get("scope", {})
    
    forecast_result = get_demand_forecast(
        category=scope.get("category"),
        channel=scope.get("channel"),
        sku_ids=scope.get("sku_ids")
    )
    
    state["baseline_forecast"] = forecast_result.model_dump()
    state["current_step"] = "forecast_retrieved"
    state["updated_at"] = datetime.utcnow().isoformat()
    
    state["tool_calls"].append({
        "tool": "get_demand_forecast",
        "timestamp": datetime.utcnow().isoformat(),
        "result": forecast_result.summary
    })
    
    return state


def apply_scenario_node(state: ScenarioState) -> ScenarioState:
    """Apply perturbations to forecast."""
    if not state["baseline_forecast"]:
        return state
    
    from schemas.forecast_schema import ForecastResult
    baseline = ForecastResult(**state["baseline_forecast"])
    
    # Convert dict perturbations to Perturbation objects
    pert_objs = []
    for p_dict in state["perturbations"]:
        if p_dict["type"] == "topline":
            pert_objs.append(Perturbation(type=PerturbationType.TOPLINE, multiplier=p_dict["multiplier"], scope=p_dict.get("scope", "all")))
        elif p_dict["type"] == "channel":
            pert_objs.append(Perturbation(type=PerturbationType.CHANNEL, channel=p_dict["channel"], multiplier=p_dict["multiplier"]))
        elif p_dict["type"] == "category":
            pert_objs.append(Perturbation(type=PerturbationType.CATEGORY, category=p_dict["category"], multiplier=p_dict["multiplier"]))
    
    scope = state.get("scope", {})
    adjusted_result = apply_topline_adjustment(baseline, pert_objs, scope)
    
    state["adjusted_forecast"] = adjusted_result.model_dump()
    state["current_step"] = "scenario_applied"
    state["updated_at"] = datetime.utcnow().isoformat()
    
    state["tool_calls"].append({
        "tool": "apply_topline_adjustment",
        "timestamp": datetime.utcnow().isoformat(),
        "result": adjusted_result.summary
    })
    
    return state

    